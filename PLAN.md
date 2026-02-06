# Master Plan: Council Command Center

**Goal**: Build an AI-powered system to earn $2,399 for the Mac Mini M4 Pro 64GB

---

## Phase 1: Foundation (Day 1-2)

### 1.1 Dashboard MVP
**Agent Task**: Build the visual command center

**Deliverables**:
- [ ] Static HTML/CSS/JS dashboard (Vercel-deployable)
- [ ] Progress bar toward $2,399 goal
- [ ] Agent status indicators (Scanner, Research, Main)
- [ ] Opportunity pipeline visualization
- [ ] Live feed of council activity
- [ ] Mobile-responsive design

**Data Contract** (`/council/state/dashboard.json`):
```json
{
  "balance": 500,
  "target": 2399,
  "agents": {
    "scanner": { "status": "active", "lastRun": "ISO8601" },
    "research": { "status": "idle", "lastRun": "ISO8601" }
  },
  "opportunities": [],
  "feed": []
}
```

### 1.2 State Management
**Agent Task**: Build the shared state layer

**Deliverables**:
- [ ] JSON state files for council coordination
- [ ] State update scripts (Python)
- [ ] State validation schema
- [ ] Backup/restore utilities

---

## Phase 2: Scanner System (Day 2-3)

### 2.1 Job Scanner
**Agent Task**: Build Upwork/freelance job detection

**Deliverables**:
- [ ] Exa API integration for job search
- [ ] Keyword matching for Make.com, automation, AI integration
- [ ] Budget filtering (>$300)
- [ ] Deduplication logic
- [ ] Alert formatting for Telegram

**Scan Targets**:
- Upwork (via Exa)
- Freelancer.com (direct scrape)
- Keywords: make.com, zapier, automation, n8n, AI integration, workflow

### 2.2 Trading Scanner  
**Agent Task**: Build stock opportunity detection

**Deliverables**:
- [ ] Pre-market scanner (7:30 AM EST)
- [ ] Post-market scanner (4:30 PM EST)
- [ ] Momentum detection (gap ups/downs >3%)
- [ ] Watchlist price alerts (NVDA, GOOG, AMD)
- [ ] Volume spike detection

### 2.3 Arbitrage Scanner
**Agent Task**: Build price differential detection

**Deliverables**:
- [ ] eBay vs retail price comparison
- [ ] GPU/electronics focus
- [ ] Profit margin calculation
- [ ] Alert threshold (>15% margin)

---

## Phase 3: Research System (Day 3-4)

### 3.1 Gig Qualification
**Agent Task**: Analyze job opportunities

**Deliverables**:
- [ ] Client history analysis
- [ ] Budget realism scoring
- [ ] Proposal draft generation
- [ ] Time estimate calculation
- [ ] Recommendation output

### 3.2 Trade Analysis
**Agent Task**: Generate trade theses

**Deliverables**:
- [ ] Bull/bear case builder
- [ ] Risk/reward calculator
- [ ] Entry/exit level suggestions
- [ ] News sentiment integration

---

## Phase 4: Integration (Day 4-5)

### 4.1 Cron Jobs
- [ ] Job scanner: Every 4 hours (6 AM, 10 AM, 2 PM, 6 PM, 10 PM EST)
- [ ] Trading scanner: 7:30 AM and 4:30 PM EST (weekdays)
- [ ] Dashboard state refresh: Every 30 minutes

### 4.2 Telegram Integration
- [ ] Inline action buttons for opportunities
- [ ] Quick approve/reject workflow
- [ ] Daily summary at 9 PM EST

### 4.3 Vercel Deployment
- [ ] Dashboard auto-deploy on push
- [ ] Environment variables setup
- [ ] Custom domain (optional)

---

## Task Assignment Template

```
### Task: [NAME]
**Assigned to**: Agent [X]
**Priority**: High/Medium/Low
**Estimated time**: X hours
**Dependencies**: None / Task Y

**Description**:
[What to build]

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

**Files to create/modify**:
- path/to/file.py
```

---

## Current Sprint

### Sprint 1: Dashboard MVP + State Layer
**Duration**: Today
**Tasks**:
1. Dashboard HTML/CSS/JS
2. State management scripts
3. Initial Vercel deployment

---

## Success Metrics

- Dashboard live and accessible
- Scanner running on schedule
- At least 1 qualified opportunity per day
- Progress toward $2,399 tracked accurately

---

*Plan created: February 6, 2026*
*Last updated: February 6, 2026*
