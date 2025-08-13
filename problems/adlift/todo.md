# AdLift Marketing Optimization - Frontend + Backend MVP TODO Plan

## Problem Statement Alignment Check ✅
**Original Ask**: Diagnose 1-2 reasons → Propose AI-driven way to generate fresh variants & rotate winners → Prioritize with metrics
**This Plan**: One comprehensive solution (Copy Refresh + Rule-Based Rotation) with concrete, actionable outputs + Professional UI

---

## Core Deliverables (15 Minutes)

### 📋 **Backend + Frontend Integration**
1. **FastAPI Backend** — 2 endpoints (health + analyze) with content generation
2. **Single Page UI** — Upload CSV, display results, download files
3. **Dynamic Content** — Programmatically generated diagnosis + executive summary
4. **No LLM Required** — Template-based variants, rule-based decisions

---

### Phase 1: Backend Setup (5 min) ✅
- [x] **Create models/schemas.py** — Pydantic models for request/response
- [x] **Create services/analyzer.py** — Extract core logic from existing scripts
- [x] **Create routes/api.py** — Health check + analyze endpoints
- [x] **Test backend endpoints** — Verify FastAPI is working

### Phase 2: Frontend Development (7 min) 🚀
- [ ] **Create static/index.html** — Single page with upload + results sections
- [ ] **Create static/style.css** — Minimal, clean styling with loading states
- [ ] **Create static/script.js** — File upload, API calls, results display
- [ ] **Test frontend integration** — Verify file upload and display

### Phase 3: Integration & Polish (3 min)
- [ ] **Connect frontend to backend** — Test complete flow
- [ ] **Polish UI elements** — Ensure responsive design
- [ ] **Final testing** — End-to-end validation

---

## Success Criteria
- ✅ Professional single-page UI with file upload
- ✅ FastAPI backend with 2 working endpoints
- ✅ Dynamic content generation (no static files)
- ✅ All analysis results displayed beautifully
- ✅ Download functionality for CSV files
- ✅ Mobile-responsive design

## Why This Approach is Superior
- **No LLM dependency** — Template-based content generation
- **Instant results** — No external API calls or costs
- **Professional UI** — Marketing team can use immediately
- **Self-contained** — Works offline, no external dependencies

**Note**: Thompson Sampling/bandits = V2. Mention as future upgrade, not in MVP.
