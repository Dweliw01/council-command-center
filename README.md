# Council Command Center 🎯

**Mission**: Earn $2,399 to buy the Mac Mini M4 Pro 64GB

An AI-powered council of agents working together to detect opportunities, analyze trades, find freelance gigs, and track progress toward the goal.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MAIN (Opus)                          │
│              Tech Lead & Orchestrator                   │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌──────────┐
│SCANNER │  │ RESEARCH │  │DASHBOARD │
│(Flash) │  │ (Haiku)  │  │  (Web)   │
└────────┘  └──────────┘  └──────────┘
```

## Components

- **`/dashboard`** - Vercel-hosted visual command center
- **`/scanner`** - Opportunity detection (jobs, trades, arbitrage)
- **`/research`** - Due diligence & analysis workflows  
- **`/council`** - Agent coordination, state, and memory
- **`/scripts`** - Utility scripts and tools

## Goal Tracking

| Metric | Value |
|--------|-------|
| Starting Balance | $500 |
| Target | $2,399 |
| Progress | 0% |

## Links

- **Dashboard**: TBD (Vercel)
- **Started**: February 4, 2026

---

*Built by Dubz and the Council* 🤖
