from typing import Dict, List, Any, Optional
from database import get_database
from ml.refermore_model import predict_referral_likelihood, generate_personalized_message, generate_synthetic_training_data, refermore_model
from .models import (
    ReferralProfile, ScoreResponse, MessageResponse,
    TrainRequest, AnalyticsRequest, AnalyticsResponse, EvaluationResponse, CandidatesResponse,
    TrackEvent, ProgressMessageRequest, AnalyticsInsightsRequest
)
from services.aws import get_bedrock_service
import json
from datetime import datetime


class RefermoreService:
    """ReferMore service using the ML model and MongoDB where applicable"""

    def __init__(self):
        self.db = get_database()

    async def get_status(self) -> Dict[str, Any]:
        return {
            "system": "ReferMore",
            "status": "active",
            "model_trained": refermore_model.is_trained or refermore_model.load_model(),
            "database_connected": self.db is not None,
            "model_info": refermore_model.get_model_info(),
        }

    async def train(self, size: int = 2000) -> Dict[str, Any]:
        data = generate_synthetic_training_data(size)
        metrics = await refermore_model.train(data, target_column="made_referral")
        return {"message": "trained", "metrics": metrics}

    async def score_referral_propensity(self, profiles: List[ReferralProfile]) -> ScoreResponse:
        results: List[Dict[str, Any]] = []
        total = 0.0
        for p in profiles:
            pred = await predict_referral_likelihood(p.model_dump())
            results.append(pred)
            total += pred.get("propensity_score", 0) / 100.0
        avg = round(total / max(1, len(profiles)), 3)
        return ScoreResponse(results=results, total_processed=len(profiles), avg_propensity=avg)

    async def candidates(self, limit: int = 20, threshold: float = 0.6) -> CandidatesResponse:
        # Generate synthetic candidates on the fly (can be replaced with DB query later)
        data = generate_synthetic_training_data(limit * 2)
        picked: List[Dict[str, Any]] = []
        for row in data:
            pred = await predict_referral_likelihood(row)
            if (pred.get("propensity_score", 0) / 100.0) >= threshold:
                picked.append({"profile": row, **pred})
            if len(picked) >= limit:
                break
        return CandidatesResponse(candidates=picked, total_candidates=len(picked), threshold=threshold)

    async def message(self, profile: ReferralProfile, message_type: str = "referral_invite") -> MessageResponse:
        pred = await predict_referral_likelihood(profile.model_dump())
        msg = await generate_personalized_message(profile.model_dump(), pred)
        return MessageResponse(message=msg, insights=pred.get("insights", {}), confidence=float(pred.get("confidence", 0.7)))

    async def analytics(self, sample_size: int = 500) -> AnalyticsResponse:
        data = generate_synthetic_training_data(sample_size)
        scores = []
        for row in data:
            pred = await predict_referral_likelihood(row)
            scores.append(pred.get("propensity_score", 0))
        n = max(1, len(scores))
        avg = sum(scores) / n
        high = sum(1 for s in scores if s >= 70) / n
        med = sum(1 for s in scores if 40 <= s < 70) / n
        low = sum(1 for s in scores if s < 40) / n
        return AnalyticsResponse(
            avg_propensity=round(avg, 2),
            high_bucket_ratio=round(high, 3),
            medium_bucket_ratio=round(med, 3),
            low_bucket_ratio=round(low, 3),
            sample_size=len(scores),
        )

    async def evaluate(self, sample_size: int = 100) -> EvaluationResponse:
        # Simple evaluation proxy based on training metadata
        info = refermore_model.get_model_info()
        trained = info.get("is_trained", False)
        acc = info.get("metadata", {}).get("metrics", {}).get("accuracy", 0.75 if trained else 0.0)
        return EvaluationResponse(accuracy=float(acc or 0.0), test_samples=sample_size, trained=bool(trained), model_name=refermore_model.model_name)

    # --- Tracking store (in-memory fallback) ---
    _PROGRESS_MEM: Dict[str, Dict[str, Any]] = {}

    def _progress_key(self, referrer_id: str) -> str:
        return f"refermore:referrer:{referrer_id}"

    def _read_progress(self, referrer_id: str) -> Dict[str, Any]:
        key = self._progress_key(referrer_id)
        rec = self._PROGRESS_MEM.get(key, {})
        return {
            "referrer_id": referrer_id,
            "invites": int(rec.get("invites", 0)),
            "clicks": int(rec.get("clicks", 0)),
            "signups": int(rec.get("signups", 0)),
            "conversions": int(rec.get("conversions", 0)),
            "payouts_total": float(rec.get("payouts_total", 0.0)),
            "updated_at": rec.get("updated_at"),
        }

    def _write_progress(self, referrer_id: str, field: str, inc: float, is_float: bool = False):
        key = self._progress_key(referrer_id)
        rec = self._PROGRESS_MEM.setdefault(key, {})
        now = datetime.utcnow().isoformat()
        if is_float:
            rec[field] = float(rec.get(field, 0.0)) + float(inc)
        else:
            rec[field] = int(rec.get(field, 0)) + int(inc)
        rec["updated_at"] = now

    def _list_all_progress_keys(self) -> List[str]:
        prefix = "refermore:referrer:"
        return [k for k in self._PROGRESS_MEM.keys() if k.startswith(prefix)]

    async def track_event(self, event: TrackEvent) -> Dict[str, Any]:
        if event.event == "invite":
            self._write_progress(event.referrer_id, "invites", 1)
        elif event.event == "click":
            self._write_progress(event.referrer_id, "clicks", 1)
        elif event.event == "signup":
            self._write_progress(event.referrer_id, "signups", 1)
        elif event.event == "converted":
            self._write_progress(event.referrer_id, "conversions", 1)
        elif event.event == "payout":
            self._write_progress(event.referrer_id, "payouts_total", float(event.amount or 0.0), is_float=True)
        else:
            raise ValueError("Invalid event type")

        progress = self._read_progress(event.referrer_id)
        threshold = 5
        pct = min(1.0, progress["signups"] / threshold if threshold else 0.0)
        stage = (
            "Converted" if progress["conversions"] > 0 else
            "Signups" if progress["signups"] > 0 else
            "Clicked" if progress["clicks"] > 0 else
            "Invited" if progress["invites"] > 0 else
            "New"
        )
        return {
            "referrer_id": event.referrer_id,
            "event": event.event,
            "progress": progress,
            "reward": {"threshold_signups": threshold, "progress_fraction": round(pct, 3), "stage": stage},
        }

    async def progress_message(self, req: ProgressMessageRequest) -> Dict[str, Any]:
        progress = self._read_progress(req.referrer_id)
        threshold = 5
        remaining = max(0, threshold - progress["signups"])
        base_context = {
            "name": req.name or "there",
            "invites": progress["invites"],
            "clicks": progress["clicks"],
            "signups": progress["signups"],
            "conversions": progress["conversions"],
            "payouts_total": progress["payouts_total"],
            "remaining_to_reward": remaining,
            "threshold_signups": threshold,
        }

        message: Optional[str] = None
        if req.use_llm:
            bedrock = get_bedrock_service()
            try:
                if getattr(bedrock, "bedrock_runtime", None) is not None and bedrock.is_configured():
                    prompt = (
                        "You are a product assistant. Craft a friendly, concise progress nudge under 50 words. "
                        "Include a clear call to action to send more invites. Context (JSON):\n" + json.dumps(base_context)
                    )
                    message = await bedrock.generate_text(prompt, max_tokens=120)
            except Exception:
                message = None

        if not message:
            if remaining > 0:
                message = (
                    f"Hey {base_context['name']}, you’re {remaining} signup(s) away from your next reward. "
                    f"You have {base_context['clicks']} clicks and {base_context['signups']} signups so far—send a few more invites today!"
                )
            else:
                message = (
                    f"Awesome work {base_context['name']}! You’ve hit the reward threshold. Keep the momentum with a few more invites."
                )

        return {"message": message.strip(), "progress": progress, "threshold_signups": threshold}

    async def analytics_summary(self, sample_size: int = 500) -> Dict[str, Any]:
        data = generate_synthetic_training_data(sample_size)
        if not refermore_model.is_trained:
            await refermore_model.train(data, target_column="made_referral")
        scores = []
        for row in data:
            pred = await predict_referral_likelihood(row)
            scores.append(pred.get("propensity_score", 0))
        distribution = {
            "sample_size": sample_size,
            "avg_propensity": round(sum(scores) / max(1, len(scores)), 1) if scores else 0,
            "high_share": round((sum(1 for s in scores if s >= 70) / max(1, len(scores))) * 100, 1) if scores else 0,
            "medium_share": round((sum(1 for s in scores if 40 <= s < 70) / max(1, len(scores))) * 100, 1) if scores else 0,
            "low_share": round((sum(1 for s in scores if s < 40) / max(1, len(scores))) * 100, 1) if scores else 0,
        }

        # ROI metrics from tracked progress
        revenue_per_conversion = 50.0
        total_invites = total_clicks = total_signups = total_conversions = 0
        payouts_total = 0.0
        keys = self._list_all_progress_keys()
        for k in keys:
            rid = k.split(":")[-1]
            p = self._read_progress(rid)
            total_invites += p["invites"]
            total_clicks += p["clicks"]
            total_signups += p["signups"]
            total_conversions += p["conversions"]
            payouts_total += p["payouts_total"]

        est_revenue = total_conversions * revenue_per_conversion
        roi_net = est_revenue - payouts_total
        roi_multiple = (est_revenue / payouts_total) if payouts_total > 0 else None

        summary = {
            "distribution": distribution,
            "roi": {
                "referrers_tracked": len(keys),
                "totals": {
                    "invites": total_invites,
                    "clicks": total_clicks,
                    "signups": total_signups,
                    "conversions": total_conversions,
                    "payouts_total": round(payouts_total, 2),
                },
                "est_revenue": round(est_revenue, 2),
                "revenue_per_conversion": revenue_per_conversion,
                "roi_net": round(roi_net, 2),
                "roi_multiple": round(roi_multiple, 2) if roi_multiple is not None else None,
            },
            "last_updated": datetime.utcnow().isoformat(),
        }
        return summary

    async def evaluate_detailed(self, sample_size: int = 5) -> Dict[str, Any]:
        # Ensure model is trained
        if not refermore_model.is_trained:
            train_data = generate_synthetic_training_data(num_samples=2000)
            await refermore_model.train(train_data, target_column="made_referral")

        eval_data = generate_synthetic_training_data(num_samples=sample_size)
        correct = 0
        tp = tn = fp = fn = 0
        samples = []
        for row in eval_data:
            res = await predict_referral_likelihood(row)
            pred_label = bool(res.get("prediction"))
            true_label = bool(row.get("made_referral"))
            if pred_label == true_label:
                correct += 1
                if pred_label:
                    tp += 1
                else:
                    tn += 1
            else:
                if pred_label:
                    fp += 1
                else:
                    fn += 1
            samples.append({
                "student_id": row.get("student_id"),
                "true": true_label,
                "pred": pred_label,
                "propensity": res.get("propensity_score", 0),
            })

        eval_accuracy = round(correct / max(1, sample_size), 3)
        precision = round(tp / max(1, (tp + fp)), 3)
        recall = round(tp / max(1, (tp + fn)), 3)
        f1 = round((2 * precision * recall) / max(1e-9, (precision + recall)), 3) if (precision + recall) > 0 else 0.0
        model_info = refermore_model.get_model_info()
        trained_acc = None
        try:
            trained_acc = model_info["metadata"]["metrics"].get("accuracy")
        except Exception:
            trained_acc = None

        return {
            "sample_size": sample_size,
            "evaluation_accuracy": eval_accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "model_training_accuracy": trained_acc,
            "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
            "samples": samples,
        }
