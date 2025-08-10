from __future__ import annotations

import os
import random
from datetime import datetime, timedelta
from typing import List, Optional

from database import get_database

from .models import (
    Learner,
    ReferralHistory,
    ScoreComponents,
    ScoreItem,
    ReferralOutcomeEvent,
)


class RefermoreService:
    """
    WHY: Central service for referral propensity scoring and messaging.
    HOW LLM interprets: We build clear, constrained prompts with user context
    so the model outputs brief, professional referral messages.
    HOW to swap with ML later: Replace `score_learner` with a model.predict()
    while keeping input/output contracts unchanged.
    """

    # Frequency cap in days for referral nudges
    NUDGE_COOLDOWN_DAYS = 14

    # Rule weights (0..1 normalized features)
    W_COMPLETION = 0.35
    W_FEEDBACK = 0.30
    W_PARTICIPATION = 0.20
    W_RECENCY = 0.10
    W_PRIOR = 0.05

    REWARD_PHRASE = "Earn ₹1,000 when a friend enrolls with your link."
    REWARD_LIMIT_NOTE = "Up to 5 payouts per month."

    # AI usage and caching controls
    AI_REQUIRED = True
    CACHE_TTL_SECONDS = 7 * 24 * 3600

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

    # ---------------- Synthetic data ----------------
    def generate_synthetic_learners(self, n: int = 100) -> List[Learner]:
        """Generate synthetic learners with varied engagement/referral histories.
        Deprecated for runtime scoring; retained for initial DB seeding and tests.
        """
        learners: List[Learner] = []
        now = datetime.utcnow()
        for i in range(n):
            completion = max(0, min(100, random.gauss(70, 20)))
            feedback = int(max(-100, min(100, random.gauss(40, 40))))
            participation = max(0, int(random.expovariate(1 / 8)))
            days_ago = max(0, int(abs(random.gauss(7, 10))))
            last_act = now - timedelta(days=days_ago)
            invites = max(0, int(random.expovariate(1 / 2)))
            clicks = max(0, min(invites * 3, int(random.gauss(invites * 1.5, max(1, invites * 0.5)))))
            signups = max(0, min(clicks // 4, int(random.gauss(max(1, clicks // 5), 1)))) if clicks > 0 else 0
            payouts = min(5, signups)  # align with monthly limit notionally

            learners.append(
                Learner(
                    id=f"L{i+1:04d}",
                    name=f"Learner {i+1}",
                    email=f"learner{i+1}@example.com",
                    completion_pct=completion,
                    feedback_score=feedback,
                    participation_count=participation,
                    last_activity_at=last_act,
                    referral_link=f"https://yourdomain.com/r/L{i+1:04d}",
                    referral_history=ReferralHistory(
                        invites_sent=invites,
                        clicks=clicks,
                        signups=signups,
                        payouts_total=payouts,
                    ),
                    last_nudged_at=(now - timedelta(days=random.randint(0, 30))) if random.random() < 0.6 else None,
                )
            )
        return learners

    # ---------------- Database seeding and fetch ----------------
    async def seed_db(self, n: int = 100, overwrite: bool = True) -> dict:
        """Populate Mongo with synthetic learners.
        Collection: refermore_learners
        """
        db = get_database()
        if db is None:
            return {"db_connected": False, "learners": 0}

        col = db["refermore_learners"]

        try:
            await col.create_index("id", unique=True)
        except Exception:
            pass

        if overwrite:
            await col.delete_many({})

        for l in self.generate_synthetic_learners(n=n):
            doc = l.model_dump()
            await col.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)

        count = await col.count_documents({})
        return {"db_connected": True, "learners": count}

    async def fetch_learners_from_db(self, limit: int = 100) -> List[Learner]:
        db = get_database()
        if db is None:
            return []
        cursor = db["refermore_learners"].find({}).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [Learner(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

    async def fetch_random_learners_from_db(self, n: int = 1) -> List[Learner]:
        db = get_database()
        if db is None:
            return []
        col = db["refermore_learners"]
        try:
            cursor = col.aggregate([{"$sample": {"size": n}}])
            docs = await cursor.to_list(length=n)
        except Exception:
            cursor = col.find({}).limit(n)
            docs = await cursor.to_list(length=n)
        return [Learner(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

    async def fetch_learner_by_id(self, learner_id: str) -> Optional[Learner]:
        db = get_database()
        if db is None:
            return None
        doc = await db["refermore_learners"].find_one({"id": learner_id})
        return Learner(**{k: v for k, v in doc.items() if k != "_id"}) if doc else None

    # ---------------- Scoring ----------------
    @staticmethod
    def _scale_completion(x: float) -> float:
        return max(0.0, min(1.0, x / 100.0))

    @staticmethod
    def _scale_feedback(nps: int) -> float:
        # Map -100..100 to 0..1
        return max(0.0, min(1.0, (nps + 100) / 200.0))

    @staticmethod
    def _scale_participation(cnt: int) -> float:
        # Cap at 20 activities
        return max(0.0, min(1.0, cnt / 20.0))

    @staticmethod
    def _scale_recency(days_since: int) -> float:
        # Recent activity is better: 0 days -> 1.0; 30+ days -> ~0.0
        return max(0.0, min(1.0, 1.0 - (days_since / 30.0)))

    @staticmethod
    def _scale_prior(signups: int) -> float:
        # Cap contribution at 5 signups
        return max(0.0, min(1.0, signups / 5.0))

    def score_learner(self, learner: Learner) -> ScoreItem:
        now = datetime.utcnow()
        days_since_activity = max(0, (now - learner.last_activity_at).days)

        comp = self._scale_completion(learner.completion_pct)
        feed = self._scale_feedback(learner.feedback_score)
        part = self._scale_participation(learner.participation_count)
        rec = self._scale_recency(days_since_activity)
        prior = self._scale_prior(learner.referral_history.signups)

        score = (
            comp * self.W_COMPLETION
            + feed * self.W_FEEDBACK
            + part * self.W_PARTICIPATION
            + rec * self.W_RECENCY
            + prior * self.W_PRIOR
        )

        tier = "high" if score >= 0.70 else ("medium" if score >= 0.40 else "low")

        reasons = []
        if comp >= 0.7:
            reasons.append("High course completion")
        if feed >= 0.6:
            reasons.append("Strong feedback/NPS")
        if part >= 0.5:
            reasons.append("Active participation")
        if prior >= 0.2:
            reasons.append("Past referral success")
        if rec >= 0.6:
            reasons.append("Recent engagement")
        if not reasons:
            reasons.append("Moderate engagement indicators")

        # Frequency cap handling
        suggested: Optional[datetime] = None
        if learner.last_nudged_at:
            delta = learner.last_nudged_at + timedelta(days=self.NUDGE_COOLDOWN_DAYS)
            if delta > now:
                suggested = delta

        return ScoreItem(
            learner_id=learner.id,
            score=round(score, 4),
            tier=tier,
            reasons=reasons,
            score_components=ScoreComponents(
                completion=round(comp, 3),
                feedback=round(feed, 3),
                participation=round(part, 3),
                recency=round(rec, 3),
                prior_referrals=round(prior, 3),
            ),
            suggested_next_nudge_time=suggested,
        )

    # ---------------- Messaging ----------------
    def _openai_client(self):
        try:
            from openai import OpenAI  # type: ignore
        except Exception:
            return None
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        # Set a client-level timeout; avoid passing timeout to each request
        try:
            return OpenAI(api_key=api_key, timeout=30)
        except Exception:
            return None

    async def generate_messages(self, learner: Learner, variants: int = 3, tone: str = "professional") -> List[str]:
        """Generate referral messages via OpenAI; enforce JSON-only output and cache with TTL."""
        client = self._openai_client()
        messages: List[str] = []

        # Cache lookup first
        cache_key = {
            "kind": "ref_msgs",
            "learner_id": learner.id,
            "tone": tone,
            "n": variants,
        }
        try:
            dbi = get_database()
            if dbi is not None:
                col = dbi["refermore_ai_cache"]
                await col.create_index("expires_at", expireAfterSeconds=0)
                doc = await col.find_one({"key": cache_key})
                if doc and isinstance(doc.get("messages"), list):
                    return doc["messages"][:variants]
        except Exception:
            pass

        system = (
            "You write brief, professional referral prompts for learners in India."
            " Output strictly a JSON array with exactly N strings; each string is ≤2 sentences; no emojis; include the reward line when relevant."
        )
        user_prompt = (
            f"N={variants}. Learner: {learner.name}; completion={learner.completion_pct}%; feedback={learner.feedback_score}; participation_30d={learner.participation_count}.\n"
            f"Referral link={learner.referral_link}. Reward='{self.REWARD_PHRASE} {self.REWARD_LIMIT_NOTE}'. Tone={tone}. Return only the JSON array."
        )

        if client is not None:
            try:
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_prompt},
                    ],
                    n=1,
                    temperature=0.35,
                    max_tokens=220,
                )
                import json as _json
                text = completion.choices[0].message.content or "[]"
                parsed = _json.loads(text)
                if isinstance(parsed, list):
                    messages = [str(m).strip() for m in parsed if str(m).strip()][:variants]
            except Exception:
                messages = []

        if not messages:
            if getattr(self, "AI_REQUIRED", False):
                raise RuntimeError("AI-required message generation failed")
            base = [
                f"I’ve had a great experience learning here—if you’re exploring upskilling, take a look: {learner.referral_link}. {self.REWARD_PHRASE}",
                f"This program helped me level up quickly. You might find it useful too: {learner.referral_link}. {self.REWARD_PHRASE}",
                f"If you’ve been considering a career move, this course is worth it: {learner.referral_link}. {self.REWARD_PHRASE}",
            ]
            messages = base[:variants]

        # Save to cache best-effort
        try:
            dbi = get_database()
            if dbi is not None:
                from datetime import datetime, timedelta
                col = dbi["refermore_ai_cache"]
                expires_at = datetime.utcnow() + timedelta(seconds=self.CACHE_TTL_SECONDS)
                await col.update_one(
                    {"key": cache_key},
                    {"$set": {"key": cache_key, "messages": messages, "expires_at": expires_at}},
                    upsert=True,
                )
        except Exception:
            pass

        return messages

    # ---------------- AI-assisted prioritization and diagnosis ----------------
    def _ai_reason(self, learner: Learner, item: ScoreItem) -> Optional[str]:
        """Use LLM to produce a crisp, 1-sentence diagnosis-style reason. Fallback: None."""
        client = self._openai_client()
        if client is None:
            return None
        try:
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            prompt = (
                "You explain, in one short professional sentence, why a learner is likely to refer now. "
                "Use these inputs only: completion_pct, feedback_score (NPS-like), participation_count (30d), recency (days since last activity), prior signups. "
                "No emojis. Return just the sentence.\n"
                f"completion_pct={learner.completion_pct}; feedback_score={learner.feedback_score}; participation={learner.participation_count}; "
                f"days_since_last_activity={(datetime.utcnow()-learner.last_activity_at).days}; prior_signups={learner.referral_history.signups}."
            )
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a concise analyst."},
                    {"role": "user", "content": prompt},
                ],
                n=1,
                temperature=0.3,
            )
            text = (completion.choices[0].message.content or "").strip()
            return text if text else None
        except Exception:
            return None

    def _ai_tiebreak_pair(self, a: ScoreItem, b: ScoreItem, la: Learner, lb: Learner) -> Optional[str]:
        """Ask LLM which learner to prioritize: return 'A' or 'B' or None on failure."""
        client = self._openai_client()
        if client is None:
            return None
        try:
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            prompt = (
                "Two learners have nearly equal referral propensity. Choose who to nudge first based on these fields only: "
                "completion_pct, feedback_score (NPS-like), participation_count (30d), days_since_last_activity, prior_signups. "
                "Reply with exactly 'A' or 'B'. No explanation.\n\n"
                f"A: completion={la.completion_pct}, feedback={la.feedback_score}, participation={la.participation_count}, "
                f"days_since={(datetime.utcnow()-la.last_activity_at).days}, prior_signups={la.referral_history.signups}.\n"
                f"B: completion={lb.completion_pct}, feedback={lb.feedback_score}, participation={lb.participation_count}, "
                f"days_since={(datetime.utcnow()-lb.last_activity_at).days}, prior_signups={lb.referral_history.signups}."
            )
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a precise selector."},
                    {"role": "user", "content": prompt},
                ],
                n=1,
                temperature=0.0,
            )
            text = (completion.choices[0].message.content or "").strip().upper()
            if text.startswith("A"):
                return "A"
            if text.startswith("B"):
                return "B"
            return None
        except Exception:
            return None

    def rerank_and_enhance(self, items: List[ScoreItem], learners: List[Learner], top_k_ai: int = 20) -> List[ScoreItem]:
        """
        WHY: Use AI to (a) enhance diagnosis reasons and (b) tiebreak near-equal scores.
        HOW LLM interprets: Small, structured prompts with only approved fields.
        HOW to swap with ML later: Keep same contract, replace internals.
        """
        if not items:
            return items

        # Map for quick access
        lmap = {l.id: l for l in learners}

        # Enhance reasons for top subset
        enhance_n = min(len(items), max(0, top_k_ai))
        for i in range(enhance_n):
            it = items[i]
            learner = lmap.get(it.learner_id)
            if not learner:
                continue
            ai_reason = self._ai_reason(learner, it)
            if self.AI_REQUIRED and not ai_reason:
                raise RuntimeError("AI-required diagnosis failed")
            if ai_reason:
                # Prepend concise AI diagnosis without changing schema
                it.reasons = [ai_reason] + it.reasons

        # Tiebreak adjacent pairs with very close scores (|Δ| < 0.02), up to a few attempts
        max_calls = 5
        calls = 0
        i = 0
        while i < enhance_n - 1 and calls < max_calls:
            a = items[i]
            b = items[i + 1]
            if abs(a.score - b.score) < 0.02:
                la = lmap.get(a.learner_id)
                lb = lmap.get(b.learner_id)
                if la and lb:
                    pick = self._ai_tiebreak_pair(a, b, la, lb)
                    if self.AI_REQUIRED and not pick:
                        raise RuntimeError("AI-required tiebreak failed")
                    if pick == "B":
                        # Swap to prioritize B
                        items[i], items[i + 1] = items[i + 1], items[i]
                    calls += 1
            i += 1

        return items

    # ---------------- Outcomes ingestion & diagnostics ----------------
    async def ingest_outcome(self, evt: ReferralOutcomeEvent) -> dict:
        db = get_database()
        if db is None:
            return {"db_connected": False}
        col = db["refermore_outcomes"]
        await col.insert_one({**evt.model_dump()})
        return {"db_connected": True, "ok": True}

    async def diagnostics(self, baseline_days: Optional[int] = None, narrate: bool = False) -> dict:
        db = get_database()
        if db is None:
            return {"db_connected": False}
        col = db["refermore_outcomes"]
        total = await col.count_documents({})
        # funnel totals
        pipeline = [
            {"$group": {
                "_id": None,
                "invited": {"$sum": {"$cond": ["$invited", 1, 0]}},
                "clicked": {"$sum": {"$cond": ["$clicked", 1, 0]}},
                "signed_up": {"$sum": {"$cond": ["$signed_up", 1, 0]}},
                "payout": {"$sum": {"$cond": ["$payout", 1, 0]}},
            }}
        ]
        funnel = {"invited": 0, "clicked": 0, "signed_up": 0, "payout": 0}
        async for doc in col.aggregate(pipeline):
            funnel = {
                "invited": doc.get("invited", 0),
                "clicked": doc.get("clicked", 0),
                "signed_up": doc.get("signed_up", 0),
                "payout": doc.get("payout", 0),
            }
        # by score tier at time of event (join learners by id)
        learners_col = db["refermore_learners"]
        outcomes = col.find({})
        by_tier = {}
        async for evt in outcomes:
            lid = evt.get("learner_id")
            if not lid:
                continue
            ldoc = await learners_col.find_one({"id": lid})
            if not ldoc:
                continue
            l = Learner(**{k: v for k, v in ldoc.items() if k != "_id"})
            tier = self.score_learner(l).tier
            agg = by_tier.setdefault(tier, {"events": 0, "payouts": 0})
            agg["events"] += 1
            if evt.get("payout"):
                agg["payouts"] += 1
        # compute payout rate per tier
        for t, agg in by_tier.items():
            e = agg.get("events", 0)
            agg["payout_rate"] = round(agg.get("payouts", 0) / e, 4) if e else 0.0
        result = {"db_connected": True, "total_events": total, "funnel": funnel, "by_tier": by_tier}
        # Placeholder for baseline/deltas to match schema (can be expanded later with time windows)
        if narrate:
            summary = await self._ai_diag_summary_basic(result)
            if summary:
                result["ai_summary"] = summary
        return result

    async def _ai_diag_summary_basic(self, data: dict) -> Optional[str]:
        client = self._openai_client()
        if client is None:
            return None
        try:
            import json as _json
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            prompt = (
                "In one or two short sentences, summarize the referral funnel (invited→clicked→signed_up→payout) and the highest payout rate tier."
                f" Data: {_json.dumps(data)}"
            )
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a concise growth analyst."},
                    {"role": "user", "content": prompt},
                ],
                n=1,
                temperature=0.2,
                max_tokens=120,
            )
            text = (completion.choices[0].message.content or "").strip()
            return text or None
        except Exception:
            return None
