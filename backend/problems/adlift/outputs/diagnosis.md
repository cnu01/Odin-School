# AdLift Marketing Optimization - Problem Diagnosis

**Analysis Date**: August 13, 2025  
**Data Period**: July 20 - August 4, 2025 (16 days, 128 ad variations)  
**Business Context**: EdTech courses (DSA & Full-Stack) targeting Indian market

---

## Executive Summary

**Performance Variance Confirmed**: CTR ranges from 0.6% to 2.7% (4.2x variance) and CPQL from ₹335 to ₹4,825 (14.4x variance), validating the problem statement. Analysis identified two primary root causes requiring immediate action.

---

## Root Cause Analysis

### 1️⃣ **Copy-Intent Mismatch** (Primary Issue)
**Problem**: Low QPI performance on high-impression campaigns due to audience-creative misalignment

**Evidence**:
| Headline | Segment | Placement | Impressions | CTR | QPI | Keywords |
|----------|---------|-----------|-------------|-----|-----|----------|
| React + Node Bootcamp | Graduates | YouTube | 33,122 | 1.10% | 0.00033 | react, nodejs |
| React + Node Bootcamp | Graduates | YouTube | 31,005 | 0.93% | 0.00032 | react, nodejs |
| React + Node Bootcamp | Graduates | YouTube | 25,900 | 1.11% | 0.00031 | react, nodejs |

**Analysis**: YouTube placement with React/Node keywords shows 32 cases of high impressions but bottom-quartile QPI performance. Keywords "faang, coding interview" appear in 8 low-QPI instances each, indicating intent-creative mismatch.

### 2️⃣ **Qualification Gap** (Secondary Issue)  
**Problem**: Decent click-through rates but poor qualified lead conversion, indicating weak benefit clarity

**Evidence**:
| Headline | Description | Segment | CTR | CPQL | Qualified Rate |
|----------|-------------|---------|-----|------|----------------|
| Backend with Python | APIs and Databases | Working Professionals | 2.14% | ₹2,955 | 25.0% |
| Upskill to Data Roles | Weekend live classes | Working Professionals | 2.11% | ₹2,785 | 33.3% |
| Switch to Data Career | Job-ready capstone | Working Professionals | 0.88% | ₹1,795 | 20.0% |

**Analysis**: 11 cases show above-median CTR but top-quartile CPQL, with average qualified rate of only 33.4%. Suggests weak benefit articulation and CTA clarity.

---

## Creative Fatigue Detection

**Fatigued Creatives Identified**: 2 campaigns showing >25% performance degradation
- "Master DSA Fast" (Graduates): 74% of initial CTR after 16 days
- "React + Node Bootcamp" (Graduates): 75% of initial CTR after 16 days

---

## Rotation Policy Recommendation

### Decision Rules (Per Segment × Placement):
- **KEEP**: QPI ≥ 75th percentile AND CPQL ≤ median
- **PAUSE**: QPI ≤ 25th percentile OR CPQL ≥ 1.2× median  
- **REPLACE**: All PAUSE decisions + fatigue-flagged creatives

### Scoring Formula:
`Score = z(QPI) - 0.7 × z(CPQL)` (within segment context)

---

## Expected Impact (Conservative Estimates)

**Primary Metrics (30-day timeline)**:
- **CTR Improvement**: +15-25% through copy-intent realignment
- **CPQL Reduction**: -10-20% via better qualification messaging
- **Creative Lifespan**: Extend from 10 days to 15+ days through systematic rotation

**Business Impact**:
- Estimated 20-30% improvement in qualified lead volume
- 15-25% reduction in customer acquisition costs
- Enhanced campaign predictability and scalability

---

## Immediate Action Items

1. **Week 1**: Replace fatigued "Master DSA Fast" and "React + Node Bootcamp" creatives
2. **Week 1**: Generate YouTube-optimized variants for React/Node keywords  
3. **Week 2**: A/B test benefit-focused descriptions for Working Professionals segment
4. **Week 2**: Implement systematic rotation policy across all campaigns

**Confidence Level**: Medium-High (based on 128 data points, segment-wise analysis, statistical validation)

---

*Next: Generate AI-powered creative variants and implement rule-based rotation system*
