You are a highly experinced AI/ML engineer who breaks down complex problem statement into smaller sub-problems and provide smartest solutions with AI/ML to achieve highest accuracy outputs. Following is the problem statement to solve in 2 hours deadline and have Product Requirements Document (PRD). Provide your feedback whether the solution will work for the problem statement or do youe have smarter approach ?

Problem statement -

AdLift - Marketing

Background
Ad performance is inconsistent across creatives and keywords. Small wins
compound into big savings.

Current Challenge
CTR ranges from 0.7% to 3.8% on similar audiences
Cost per qualified lead varies 2–4× by creative
Creative fatigue detected after ~10 days

Data Provided
Ad history: Headlines, descriptions, thumbnails, keywords
Performance: Impressions, CTR, CPC, CVR, qualified rate
Audience notes: Segments, placements, exclusions

Your Task
Diagnose the Problem: State 1–2 reasons for weak creatives/keywords.
Propose Solutions: Suggest 2 AI-driven ways to generate fresh variants
(copy/visual cues/keywords) and rotate winners based on results.
Prioritize & Justify: Rank solutions; metrics (e.g., “+25% CTR; –20% CPLQualified in 30 days”).
_________________________________________________________________________________________

Product Requirements Document (PRD) - 

AdLift — 2-Hour MVP PRD (No Thumbnails)
1) Summary
Goal: Ship a minimal, reliable system that diagnoses weak ad copy/keywords, generates fresh variants, and rotates winners using a simple, explainable policy—in 2 hours.

What ships today: A script (or notebook) that ingests ad logs, computes performance+fatigue, proposes new variants, and outputs decision CSVs + a one-pager summary.

2) Objectives & Non-Goals
Objectives

Identify top/bottom performers by copy/keywords within audience segments.

Detect creative fatigue and recommend rotation.

Generate AI-assisted headline/description/keyword variants (no images).

Allocate budget using Bayesian bandits (qualified-per-impression objective).

Export actionable CSVs the marketing team can paste into the ad platform.

Non-Goals (MVP)

No training of supervised regressors/scorers.

No live API integration to ad platforms (manual import/export).

No thumbnail/image logic.

3) Users & Primary Use Cases
Performance Marketer / Growth PM: Needs clear winners/losers, rotation decisions, and paste-ready variants.

Data Analyst: Needs transparent metrics and reproducible logic.

Use Cases

“Which ads to pause/keep/replace per audience segment?”

“What fresh copy/keywords should we test next week?”

“Where are we seeing fatigue, and what replaces it?”

4) Inputs & Data Contracts
Required columns (per row = daily or per-flight granularity)

Keys: date, campaign, ad_group, headline, description, keywords (array/comma-sep), audience_segment, placement

Metrics: impressions, clicks, spend, leads, qualified_leads

Derived metrics

CTR = clicks / impressions

CPC = spend / max(clicks,1)

CVR = leads / max(clicks,1)

QualifiedRate = qualified_leads / max(leads,1)

CPL = spend / max(leads,1)

CPQL = spend / max(qualified_leads,1)

QPI (Qualified per Impression) = qualified_leads / impressions (objective)

Preprocessing

Lowercase + trim + sort tokens in keywords for grouping.

Winsorize CPQL at 1% tails.

Filter to stable samples: impressions ≥ 500 (configurable).

5) Core Logic
5.1 Diagnosis
Group by: (headline, description, normalized keywords, audience_segment, placement).

Compute per-group metrics: CTR, CPQL, QPI.

Top/Bottom lists by:

Attraction: CTR (primary)

Efficiency: CPQL (secondary)

North Star: QPI (decision metric)

Fatigue detection

For each (headline, keywords) with ≥10 days live:

7-day rolling CTR vs avg CTR of first 3 days.

Flag needs_rotation = True if drop ≥ 20% or 7-day slope negative beyond threshold.

Reasoning snippets (auto-generated)

“Low CTR with high impressions → copy–intent mismatch.”

“OK CTR but high CPQL → weak qualification/CTA or misaligned keywords.”

“Fatigue after day ~10 → rotate.”

5.2 Variant Generation (AI-assisted; text only)
Inputs to LLM: 3 best + 3 worst examples (headline, description, top keywords, audience note); brand tone; length limits; compliance guardrails; negatives to avoid.

Outputs:

5–10 headlines

5 descriptions

3 keyword sets (core intent / problem-aware / negatives)

Pre-filters:

Similarity: drop variants with Jaccard ≥ 0.8 vs known losers.

Bigram boost: favor variants using high-lift bigrams from winners.

Length/compliance checks.

(If LLM unavailable, fall back to slot-filled templates using winner bigrams.)

5.3 Rotation & Budget Allocation (Bayesian Bandit)
Objective: maximize QPI.

Per variant (within ad group & segment):

Beta–Binomial Thompson Sampling

successes = qualified_leads

failures = impressions − qualified_leads

prior = Beta(1,1) or Beta(α₀,β₀) from historical global rate

Allocation cycle (per refresh batch; e.g., next-day or next 5k impressions):
(Check uploaded image)

Retirement:

If needs_rotation=True OR bottom quartile of QPI for 2 consecutive cycles → pause.

Replace with two fresh variants (winner-like + explorer).

Cold-start prior (optional)

Initialize Beta prior using embedding-nearest winners (cosine) to reduce under-allocation to promising new variants.

6) Outputs & Deliverables
Exports to /outputs/:

top_performers.csv — by (segment/ad_group), with CTR, QPI, CPQL.

bottom_performers.csv — same schema, plus reason tags.

fatigue_flags.csv — (id keys + drop %, slope, flag).

ai_variants.csv — approved variants (headline, description, keyword_set, type=winner-like/explorer, pre-filter scores).

rotation_plan.csv — pause/keep/replace decisions + next-batch allocations.

summary.md — one-pager (reasons, actions, next 7-day plan).

Schema highlights (rotation_plan.csv)

campaign, ad_group, audience_segment

current_variant_id, decision {pause|keep|replace}

reason {fatigue|low_QPI|high_CPQL}

replacement_variant_id (if replace)

allocation_share_next_batch (0–1)

7) UX (MVP)
CLI/Notebook run; no server needed.

Prints a short table of changes + paths to CSVs.

(Optional 20-min add-on) Tiny Streamlit to display top/bottom and decisions.

8) Metrics & Acceptance Criteria
Primary

QPI improvements in test cycles (tracked; initial baseline vs proposed allocations).

Guardrails

CPQL must not deteriorate by >10% for any scaled variant.

Minimum sample: ≥500 impressions per variant for ranking; ≥2k–5k before reallocation.

Correctness (acceptance)

All derived metrics compute without div/0.

Fatigue flags consistent with rule (≥20% CTR drop).

Bandit output contains allocation shares summing to 1 per ad group & segment.

AI variants pass similarity/compliance filters.

9) Constraints & Risks
Small samples → high variance. Mitigate with priors + burn-in + Wilson lower bounds in dashboards.

Segment mix shift → compute metrics within segment; avoid cross-segment comparisons.

LLM availability → have template fallback.

10) Implementation Plan (2 Hours)
T0–T+20 min

Project skeleton: /data, /src, /outputs.

Load CSV, validate columns, clean keywords, compute derived metrics.

T+20–T+55 min

Aggregations (by copy/keywords/segment).

Top/Bottom tables (CTR, QPI, CPQL), winsorize CPQL.

Fatigue detection (7-day rolling CTR vs day 1–3 mean).

T+55–T+85 min

Thompson Sampling allocator (per ad group & segment).

Burn-in + CPQL guardrail + retirement rules.

Produce rotation_plan.csv.

T+85–T+105 min

N-gram mining from winners; LLM prompts; generate variants.

Similarity + bigram filters; write ai_variants.csv.

T+105–T+120 min

Write all CSVs + summary.md (reasons, actions, next-7-day plan).

Smoke-check with a small sample; finalize.

11) LLM Prompt (template)
System: “You are a performance ads copywriter for edtech. Write concise, compliant, high-intent ads.”
User context:

Audience: <segment>

Program: <program/course>

Top performers (3): headline|description|top_bigrams

Avoid: phrases in losers, compliance words: <list>

Constraints: Headline ≤ 30 chars; clear benefit + number if relevant; CTA.

Task:
“Generate 10 headlines, 5 descriptions, and 3 keyword sets (core intent / problem-aware / negatives). Avoid near-duplicates of losers. Return JSON.”

12) Config (env)
MIN_IMPRESSIONS=500

BURN_IN_IMPRESSIONS=3000

FATIGUE_DROP_PCT=0.20

CPQL_GUARDRAIL_PCT=0.10

BETA_PRIOR_ALPHA=1

BETA_PRIOR_BETA=1

JACCARD_MAX_LOSER_SIM=0.8

TOP_N=10

13) Future (V2+)
Train calibrated GBM scorer on QPI / log-CPQL with time-based split; SHAP for drivers.

API integration (automatic budget updates).

Multi-metric bandit (contextual TS with segment features).

Holdout-based lift measurement & sequential testing.

14) Definition of Done
All CSV deliverables + summary.md generated with no errors.

Rotation decisions present for each underperforming or fatigued variant.

≥10 AI variants generated and filtered per priority ad group.

Documented parameters and how to rerun with new data. 