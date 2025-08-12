# AdLift Marketing Optimization - Practical MVP TODO Plan

## Problem Statement Alignment Check ✅
**Original Ask**: Diagnose 1-2 reasons → Propose AI-driven way to generate fresh variants & rotate winners → Prioritize with metrics
**This Plan**: One comprehensive solution (Copy Refresh + Rule-Based Rotation) with concrete, actionable outputs

---

## Core Deliverables (2 Hours)

### 📋 **Output Files**
1. **diagnosis.md** — 1 page with 1-2 reasons + 2-3 evidence rows
2. **variants.csv** — 8-10 headlines, 4-5 descriptions, 3 keyword sets (core/problem-aware/negatives)  
3. **prioritization.csv** — per creative: QPI, CPQL, Score, decision {keep/pause/replace}, reason

---

### Phase 1: Problem Diagnosis (25-30 min)
- [ ] **Load ad data** (headline, description, keywords, segment, placement, impressions, CTR, CPC, CVR, qualified_rate)
- [ ] **Compute business-native metrics** (per segment × placement):
  - QPI = CTR × CVR × qualified_rate (quality per impression)
  - CPQL = CPC / (CVR × qualified_rate)
- [ ] **Fast sanity checks**:
  - Filter: impressions ≥ 500
  - Use segment medians & quartiles (no heavy significance tests)
- [ ] **Identify 1-2 root causes with evidence rows**:
  - Copy-intent mismatch → low QPI/CTR on specific keyword themes
  - Qualification gap → OK CTR but high CPQL (weak benefit/CTA clarity)
- [ ] **(Optional) Fatigue flag**: 7-day CTR ≤ 80% of first-3-day CTR

### Phase 2: Copy Refresh + Rule-Based Rotation (60 min)
- [ ] **LLM-assisted variant generation**:
  - Few-shot from top performers
  - Output: 8-10 headlines, 4-5 descriptions, 3 keyword sets
  - Filters: Jaccard < 0.8 vs losers, include ≥1 winning bigram, length/compliance, de-dupe
  - Export: variants.csv
- [ ] **Rule-based rotation** (per segment × placement):
  - **KEEP**: QPI ≥ Q3 and CPQL ≤ median
  - **PAUSE**: QPI ≤ Q1 or CPQL ≥ 1.2 × median
  - **REPLACE**: All PAUSE (and fatigue-flagged) with 2 variants → winner-like + explorer
  - **Score** (tie-break): Score = z(QPI) - 0.7 × z(CPQL) (within segment)
  - Export: prioritization.csv (include decision + reason)

### Phase 3: Prioritize & Write-Up (30 min)
- [ ] **Draft diagnosis.md** (≤1 page): reasons, evidence, rotation policy
- [ ] **Add expected impact**: +15-25% CTR, -10-20% CPQL in 30 days (conservative)
- [ ] **Quick QA**: no div/0, segment-wise quartiles, filters applied, CSV schemas correct

---

## Success Criteria
- ✅ Clear 1-2 data-backed reasons
- ✅ High-quality, filtered variants ready to launch
- ✅ Keep/Pause/Replace decisions with QPI/CPQL and Score
- ✅ Realistic targets stated; actions executable this week

## Why This Approach is Superior
- **Business-native KPIs** (QPI, CPQL) with segment context → reliable decisions
- **Explainable thresholds** beat fragile "quick ML" under time pressure  
- **Produces exactly what stakeholders need** to act tomorrow
- **One comprehensive solution** vs trying to build two separate systems

**Note**: Thompson Sampling/bandits = V2. Mention as future upgrade, not in MVP.
