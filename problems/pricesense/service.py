from __future__ import annotations

import os
import random
from typing import List, Optional, Tuple

from database import get_database

from .models import MessageRequest, Plan, RecommendResponse, Segment, UserProfile, OutcomeEvent


class PricesenseService:
    """
    WHY: Recommend best plan per segment and generate clear plan messaging.
    HOW LLM interprets: Prompts include segment context, plan benefits, and scholarship.
    HOW to swap with ML later: Replace `recommend` with a model-based scorer and keep contracts.
    """

    PRICE_TOTAL_INR = 120_000
    SCHOLARSHIP_PCT = 50  # flat percentage, no min/max caps
    # Make AI mandatory for messaging; routes will map failures to 503
    AI_REQUIRED = True
    # Cache LLM outputs to reduce cost; 7-day TTL
    CACHE_TTL_SECONDS = 7 * 24 * 3600

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

    # ---------------- Synthetic data ----------------
    def generate_plans(self) -> List[Plan]:
    # Deprecated for runtime usage: kept only for initial DB seeding and tests.
        total = self.PRICE_TOTAL_INR
        plans = [
            Plan(id="FULL", name="FULL", price_total=total, installment_count=1, installment_amount=total, scholarship_pct=self.SCHOLARSHIP_PCT, fees=0),
            Plan(id="3M", name="3M", price_total=total, installment_count=3, installment_amount=total // 3, scholarship_pct=self.SCHOLARSHIP_PCT, fees=0),
            Plan(id="6M", name="6M", price_total=total, installment_count=6, installment_amount=total // 6, scholarship_pct=self.SCHOLARSHIP_PCT, fees=0),
            Plan(id="12M", name="12M", price_total=total, installment_count=12, installment_amount=total // 12, scholarship_pct=self.SCHOLARSHIP_PCT, fees=0),
        ]
        return plans

    def generate_users(self, n: int = 100) -> List[UserProfile]:
    # Deprecated for runtime usage: kept only for initial DB seeding and tests.
        sources = ["paid_search", "organic", "referral", "social"]
        devices = ["mobile", "desktop"]
        engagement = ["low", "med", "high"]
        users: List[UserProfile] = []
        for i in range(n):
            seg = Segment(
                source=random.choice(sources),
                geography="IN",
                device="mobile" if random.random() < 0.65 else "desktop",
                prior_engagement=random.choices(engagement, weights=[0.3, 0.5, 0.2])[0],
            )
            users.append(UserProfile(id=f"U{i+1:04d}", segment=seg))
        return users

    # ---------------- Database seeding and fetch ----------------
    async def seed_db(self, n: int = 100, overwrite: bool = True) -> dict:
        """Populate Mongo with synthetic plans and users.
        Collections: pricesense_plans, pricesense_users
        """
        db = get_database()
        if db is None:
            return {"db_connected": False, "plans": 0, "users": 0}

        plans_col = db["pricesense_plans"]
        users_col = db["pricesense_users"]

        # Ensure unique indexes on id
        try:
            await plans_col.create_index("id", unique=True)
            await users_col.create_index("id", unique=True)
        except Exception:
            # Index may already exist; ignore
            pass

        if overwrite:
            await plans_col.delete_many({})
            await users_col.delete_many({})

        # Upsert plans
        for p in self.generate_plans():
            doc = p.model_dump()
            await plans_col.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)

        # Upsert users
        for u in self.generate_users(n=n):
            doc = u.model_dump()
            await users_col.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)

        plans_count = await plans_col.count_documents({})
        users_count = await users_col.count_documents({})
        return {"db_connected": True, "plans": plans_count, "users": users_count}

    async def fetch_plans_from_db(self) -> List[Plan]:
        db = get_database()
        if db is None:
            return []
        cursor = db["pricesense_plans"].find({})
        docs = await cursor.to_list(length=100)
        return [Plan(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

    async def fetch_random_users_from_db(self, n: int = 1) -> List[UserProfile]:
        db = get_database()
        if db is None:
            return []
        col = db["pricesense_users"]
        try:
            cursor = col.aggregate([{"$sample": {"size": n}}])
            docs = await cursor.to_list(length=n)
        except Exception:
            # Fallback if $sample unsupported
            cursor = col.find({}).limit(n)
            docs = await cursor.to_list(length=n)
        return [UserProfile(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

    # ---------------- Outcomes ingestion & diagnostics ----------------
    async def ingest_outcome(self, evt: OutcomeEvent) -> dict:
        db = get_database()
        if db is None:
            return {"db_connected": False}
        col = db["pricesense_outcomes"]
        doc = {**evt.model_dump()}
        if not doc.get("ts"):
            from datetime import datetime
            doc["ts"] = datetime.utcnow().isoformat()
        await col.insert_one(doc)
        return {"db_connected": True, "ok": True}

    async def diagnostics(self, baseline_days: Optional[int] = None, narrate: bool = False) -> dict:
        db = get_database()
        if db is None:
            return {"db_connected": False}
        col = db["pricesense_outcomes"]
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        total = await col.count_documents({})
        # by plan
        pipeline = [
            {"$group": {
                "_id": "$plan_id",
                "events": {"$sum": 1},
                "conversions": {"$sum": {"$cond": ["$converted", 1, 0]}},
                "refunds": {"$sum": {"$cond": ["$refunded", 1, 0]}},
                "defaults": {"$sum": {"$cond": ["$defaulted", 1, 0]}},
            }}
        ]
        by_plan = {}
        async for doc in col.aggregate(pipeline):
            _id = doc.get("_id")
            if _id is None:
                continue
            events = doc.get("events", 0)
            by_plan[_id] = {
                "events": events,
                "conversion_rate": round((doc.get("conversions", 0) / events), 4) if events else 0.0,
                "refund_rate": round((doc.get("refunds", 0) / events), 4) if events else 0.0,
                "default_rate": round((doc.get("defaults", 0) / events), 4) if events else 0.0,
            }
        # by segment coarse key: source|device|engagement
        pipeline2 = [
            {"$project": {
                "k": {"$concat": ["$segment.source", "|", "$segment.device", "|", "$segment.prior_engagement"]},
                "converted": 1, "refunded": 1, "defaulted": 1
            }},
            {"$group": {
                "_id": "$k",
                "events": {"$sum": 1},
                "conversions": {"$sum": {"$cond": ["$converted", 1, 0]}},
                "refunds": {"$sum": {"$cond": ["$refunded", 1, 0]}},
                "defaults": {"$sum": {"$cond": ["$defaulted", 1, 0]}},
            }}
        ]
        by_seg = {}
        async for doc in col.aggregate(pipeline2):
            k = doc.get("_id")
            if k is None:
                continue
            events = doc.get("events", 0)
            by_seg[k] = {
                "events": events,
                "conversion_rate": round((doc.get("conversions", 0) / events), 4) if events else 0.0,
                "refund_rate": round((doc.get("refunds", 0) / events), 4) if events else 0.0,
                "default_rate": round((doc.get("defaults", 0) / events), 4) if events else 0.0,
            }
        result = {"db_connected": True, "total_events": total, "by_plan": by_plan, "by_segment_key": by_seg}

        # Optional baseline window: previous period of length baseline_days (current window is last baseline_days)
        if baseline_days and baseline_days > 0:
            cur_start = (now - timedelta(days=baseline_days)).isoformat()
            base_start = (now - timedelta(days=baseline_days * 2)).isoformat()
            cur_match = {"ts": {"$gte": cur_start}}
            base_match = {"ts": {"$gte": base_start, "$lt": cur_start}}

            def _agg_plan(match):
                return [
                    {"$match": {**match}},
                    {"$group": {
                        "_id": "$plan_id",
                        "events": {"$sum": 1},
                        "conversions": {"$sum": {"$cond": ["$converted", 1, 0]}},
                        "refunds": {"$sum": {"$cond": ["$refunded", 1, 0]}},
                        "defaults": {"$sum": {"$cond": ["$defaulted", 1, 0]}},
                    }}
                ]

            def _agg_seg(match):
                return [
                    {"$match": {**match}},
                    {"$project": {
                        "k": {"$concat": ["$segment.source", "|", "$segment.device", "|", "$segment.prior_engagement"]},
                        "converted": 1, "refunded": 1, "defaulted": 1
                    }},
                    {"$group": {
                        "_id": "$k",
                        "events": {"$sum": 1},
                        "conversions": {"$sum": {"$cond": ["$converted", 1, 0]}},
                        "refunds": {"$sum": {"$cond": ["$refunded", 1, 0]}},
                        "defaults": {"$sum": {"$cond": ["$defaulted", 1, 0]}},
                    }}
                ]

            baseline_by_plan = {}
            async for doc in col.aggregate(_agg_plan(base_match)):
                _id = doc.get("_id")
                if _id is None:
                    continue
                events = doc.get("events", 0)
                baseline_by_plan[_id] = {
                    "events": events,
                    "conversion_rate": round((doc.get("conversions", 0) / events), 4) if events else 0.0,
                    "refund_rate": round((doc.get("refunds", 0) / events), 4) if events else 0.0,
                    "default_rate": round((doc.get("defaults", 0) / events), 4) if events else 0.0,
                }

            baseline_by_seg = {}
            async for doc in col.aggregate(_agg_seg(base_match)):
                k = doc.get("_id")
                if k is None:
                    continue
                events = doc.get("events", 0)
                baseline_by_seg[k] = {
                    "events": events,
                    "conversion_rate": round((doc.get("conversions", 0) / events), 4) if events else 0.0,
                    "refund_rate": round((doc.get("refunds", 0) / events), 4) if events else 0.0,
                    "default_rate": round((doc.get("defaults", 0) / events), 4) if events else 0.0,
                }

            # Deltas: differences current - baseline for conversion_rate
            deltas = {"by_plan": {}, "by_segment_key": {}}
            for k, cur in by_plan.items():
                base = baseline_by_plan.get(k, {})
                deltas["by_plan"][k] = {
                    "conversion_rate": round(cur.get("conversion_rate", 0.0) - base.get("conversion_rate", 0.0), 4),
                    "events_delta": cur.get("events", 0) - base.get("events", 0),
                }
            for k, cur in by_seg.items():
                base = baseline_by_seg.get(k, {})
                deltas["by_segment_key"][k] = {
                    "conversion_rate": round(cur.get("conversion_rate", 0.0) - base.get("conversion_rate", 0.0), 4),
                    "events_delta": cur.get("events", 0) - base.get("events", 0),
                }

            result.update({
                "baseline_by_plan": baseline_by_plan,
                "baseline_by_segment_key": baseline_by_seg,
                "deltas": deltas,
            })

            if narrate:
                summary = await self._ai_diag_summary(deltas)
                if summary:
                    result["ai_summary"] = summary

        return result

    async def _ai_diag_summary(self, deltas: dict) -> Optional[str]:
        client = self._openai_client()
        if client is None:
            return None
        try:
            import json as _json
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            prompt = (
                "Summarize in one or two short professional sentences the most notable changes in conversion rates by plan"
                " and segment. Keep it neutral and specific to India context where relevant."
                f" Deltas JSON: {_json.dumps(deltas)}"
            )
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a concise product analyst."},
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

    # ---------------- Recommendation heuristics ----------------
    def _risk_score(self, seg: Segment) -> float:
        """Lower is safer.
        Simple heuristic: higher risk for mobile + low engagement + paid search.
        """
        risk = 0.0
        if seg.device == "mobile":
            risk += 0.2
        if seg.prior_engagement == "low":
            risk += 0.5
        elif seg.prior_engagement == "med":
            risk += 0.2
        if seg.source == "paid_search":
            risk += 0.2
        return min(1.0, risk)

    def recommend(self, seg: Segment, plans: List[Plan]) -> Tuple[str, List[str], dict, List[dict]]:
        risk_v = self._risk_score(seg)
        reasons: List[str] = []

        # Preferences derived from segment
        prefer_simpler = seg.device == "mobile"
        high_engaged = seg.prior_engagement == "high"
        low_engaged = seg.prior_engagement == "low"

        # Rank plans by simple utility that balances risk and conversion
        scored = []
        for p in plans:
            utility = 0.0
            # Simpler plans (FULL/3M) favored on mobile
            if prefer_simpler and p.name in ("FULL", "3M"):
                utility += 0.2
            # High engagement: nudge to FULL for savings
            if high_engaged and p.name == "FULL":
                utility += 0.3
            # Low engagement: avoid 12M; prefer 3M/6M
            if low_engaged and p.name in ("3M", "6M"):
                utility += 0.2
            if low_engaged and p.name == "12M":
                utility -= 0.2
            # Penalize longer terms when risk is high
            if risk_v >= 0.6 and p.name == "12M":
                utility -= 0.3
            elif risk_v >= 0.4 and p.name == "12M":
                utility -= 0.15
            scored.append((p, utility))

        scored.sort(key=lambda t: t[1], reverse=True)
        # If top two are very close, use AI to break the tie
        scored.sort(key=lambda t: t[1], reverse=True)
        best = scored[0][0]
        if len(scored) > 1 and abs(scored[0][1] - scored[1][1]) < 0.05:
            pick = self._ai_tiebreak_plans(seg, scored[0][0], scored[1][0])
            if self.AI_REQUIRED and not pick:
                raise RuntimeError("AI-required plan tie-break failed")
            if pick == scored[1][0].id:
                best = scored[1][0]
        alternatives = [
            {"plan_id": s[0].id, "why": "alternative option"} for s in scored[1:3]
        ]

        # Reasons
        if prefer_simpler:
            reasons.append("Simpler plan preferred on mobile")
        if high_engaged and best.name == "FULL":
            reasons.append("High engagement favors upfront savings")
        if low_engaged and best.name in ("3M", "6M"):
            reasons.append("Lower commitment suits lower engagement")
        if best.name != "12M" and risk_v >= 0.4:
            reasons.append("Avoiding long-term due to higher risk")

        risk_flags = {
            "default_risk": "high" if risk_v >= 0.6 else ("med" if risk_v >= 0.3 else "low"),
            "refund_risk": "med" if low_engaged else ("low" if high_engaged else "med"),
        }

        # Add concise AI justification at the top of reasons; require if AI_REQUIRED
        ai_reason = self._ai_reason(seg=seg, plan=best)
        if self.AI_REQUIRED and not ai_reason:
            raise RuntimeError("AI-required plan justification failed")
        if ai_reason:
            reasons = [ai_reason] + reasons

        return best.id, reasons, risk_flags, alternatives

    # ---------------- Messaging ----------------
    def _openai_client(self):
        try:
            from openai import OpenAI  # type: ignore
        except Exception:
            return None
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            return OpenAI(api_key=api_key, timeout=30)
        except Exception:
            return None

    async def generate_messages(self, req: MessageRequest) -> List[str]:
        client = self._openai_client()
        messages: List[str] = []
        seg = req.user_or_segment.segment if hasattr(req.user_or_segment, "segment") else req.user_or_segment
        scholarship_line = f"Eligible learners receive a {self.SCHOLARSHIP_PCT}% scholarship—applied to the first installment or upfront payment."

        # Try cache first
        cache_key = {
            "kind": "plan_msgs",
            "plan": req.plan_id,
            "seg": seg.model_dump(),
            "tone": req.tone,
            "n": req.variants,
        }
        try:
            dbi = get_database()
            if dbi is not None:
                col = dbi["pricesense_ai_cache"]
                await col.create_index("expires_at", expireAfterSeconds=0)
                existing = await col.find_one({"key": cache_key})
                if existing and isinstance(existing.get("messages"), list):
                    return existing["messages"][: req.variants]
        except Exception:
            # best-effort cache
            pass

        system = (
            "You write concise, professional plan messages for prospects in India."
            " Output strictly a JSON array of exactly N strings; each string is ≤2 sentences; no emojis; clarify scholarship plainly."
        )
        user_prompt = (
            f"N={req.variants}. Segment: source={seg.source}, geography={seg.geography}, device={seg.device}, engagement={seg.prior_engagement}.\n"
            f"Plan={req.plan_id}; total=₹{self.PRICE_TOTAL_INR}; 0% interest; no hidden fees. {scholarship_line}\n"
            f"Tone={req.tone}. Return only the JSON array."
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
                    messages = [str(m).strip() for m in parsed if str(m).strip()][: req.variants]
            except Exception:
                messages = []

        if not messages:
            if getattr(self, "AI_REQUIRED", False):
                # Enforce AI requirement for messaging
                raise RuntimeError("AI-required message generation failed")
            base = [
                f"The {req.plan_id} plan keeps costs predictable with zero interest; if eligible, your scholarship reduces the upfront/first payment by {self.SCHOLARSHIP_PCT}%.",
                f"Choose {req.plan_id} to fit your schedule without extra fees. Eligible learners get {self.SCHOLARSHIP_PCT}% off the initial payment.",
                f"{req.plan_id} offers a clear path with no hidden charges. A {self.SCHOLARSHIP_PCT}% scholarship may apply to your first payment.",
            ]
            messages = base[: req.variants]

        # Save to cache best-effort
        try:
            dbi = get_database()
            if dbi is not None:
                from datetime import datetime, timedelta
                col = dbi["pricesense_ai_cache"]
                expires_at = datetime.utcnow() + timedelta(seconds=self.CACHE_TTL_SECONDS)
                await col.update_one(
                    {"key": cache_key},
                    {"$set": {"key": cache_key, "messages": messages, "expires_at": expires_at}},
                    upsert=True,
                )
        except Exception:
            pass

        return messages

    # ---------------- AI-assisted tie-break and justification ----------------
    def _ai_reason(self, seg: Segment, plan: Plan) -> Optional[str]:
        client = self._openai_client()
        if client is None:
            return None
        try:
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            prompt = (
                "In one short professional sentence, justify why this plan fits the segment. "
                "Fields: source, device, engagement (low/med/high), geography (IN), plan name. No emojis.\n"
                f"source={seg.source}; device={seg.device}; engagement={seg.prior_engagement}; geography={seg.geography}; plan={plan.name}."
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

    def _ai_tiebreak_plans(self, seg: Segment, a: Plan, b: Plan) -> Optional[str]:
        client = self._openai_client()
        if client is None:
            return None
        try:
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            prompt = (
                "Two plans scored nearly equal. Choose the better fit based on segment fields only: "
                "source, device, engagement, geography. Reply with exactly the chosen plan id (e.g., 'FULL', '3M'). No explanation.\n\n"
                f"segment: source={seg.source}, device={seg.device}, engagement={seg.prior_engagement}, geography={seg.geography}.\n"
                f"A={a.id}; B={b.id}."
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
            if text in (a.id.upper(), b.id.upper()):
                return text
            return None
        except Exception:
            return None
