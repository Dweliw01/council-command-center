# 🔬 Research Agent

Automated research system that analyzes opportunities found by the Scanner.

## Overview

The Research Agent takes raw opportunities (trading alerts, job postings) from the Scanner and performs deep analysis to determine actionability. It generates trade theses with risk/reward calculations and drafts proposals for gig opportunities.

## Components

### 1. `trade_analyzer.py`
Analyzes trading alerts using yfinance data:
- Fetches 5-day price history
- Calculates support/resistance levels
- Determines entry, stop-loss, and target prices
- Generates bull/bear thesis narratives
- Outputs recommendations: `BUY_NOW`, `BUY_DIP`, `WATCH`, or `PASS`

### 2. `gig_analyzer.py`
Analyzes job opportunities:
- Matches against skills profile (automation, AI/ML, Python, etc.)
- Calculates relevance score (1-10)
- Estimates hours and suggested rate
- Generates tailored proposal drafts
- Outputs recommendations: `APPLY`, `MAYBE`, or `PASS`

### 3. `run_research.py`
Main orchestrator:
- Reads from `/council/state/opportunities.json`
- Processes items in "detected" stage
- Runs appropriate analyzer
- Updates state with analysis
- Moves to "ready" if high confidence
- Logs activity to feed

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run research on all pending opportunities
python run_research.py
```

## Output Format

### Trade Analysis
```json
{
  "symbol": "NVDA",
  "thesis": {
    "bull_case": "Strong momentum with 7.9% move. High conviction with 1.1x average volume",
    "bear_case": "Extended move may need consolidation. Near resistance",
    "risk_reward": "2.1:1",
    "entry": 183.00,
    "stop_loss": 178.00,
    "target": 195.00
  },
  "recommendation": "BUY_DIP",
  "confidence": "medium",
  "stage": "ready"
}
```

### Gig Analysis
```json
{
  "title": "Make.com Automation Specialist",
  "analysis": {
    "relevance_score": 9,
    "estimated_hours": 10,
    "suggested_rate": 75,
    "competition_level": "low"
  },
  "proposal_draft": "Hi! I specialize in Make.com automation...",
  "recommendation": "APPLY",
  "confidence": "high",
  "stage": "ready"
}
```

## State Updates

The research agent updates `/council/state/opportunities.json` with:
- `analyzed` sections under `trading` and `jobs`
- `research_summary` with counts
- `last_research` timestamp

Activity is logged to `/council/state/feed.json`:
```json
{
  "timestamp": "2026-02-06T22:00:00Z",
  "agent": "research",
  "icon": "📊",
  "message": "Analyzed NVDA: BUY_DIP recommendation (2:1 R/R)"
}
```

## Skills Profile

The gig analyzer uses a configurable skills profile in `gig_analyzer.py`:
- **automation**: Make.com, Zapier, n8n workflows
- **ai_ml**: OpenAI, Claude, LLM integrations
- **python**: Django, FastAPI, scripting
- **web_dev**: React, Node.js, frontend/backend
- **data**: SQL, ETL, analytics
- **devops**: AWS, Docker, CI/CD
- **bots**: Telegram, Discord, Slack bots
- **scraping**: Web scraping, Selenium

Customize weights and rates as needed.

## Integration

Part of the Council Command Center pipeline:
```
Scanner → Research → Dashboard
         ↓
   opportunities.json (analyzed)
```
