// Council Command Center Dashboard Data
// Last sync: 2026-02-06T22:34Z
// Auto-updated by scanner

const DASHBOARD_DATA = {
  balance: 500,
  target: 2399,
  startDate: "2026-02-04",
  lastUpdate: "2026-02-06T22:34:00Z",
  
  agents: {
    scanner: {
      status: "active",
      lastRun: "2026-02-06T22:34:00Z",
      runsToday: 1,
      hitsToday: 4
    },
    research: {
      status: "idle",
      lastRun: null,
      queueLength: 4
    }
  },
  
  income: {
    freelance: 0,
    trading: 0,
    other: 0
  },
  
  opportunities: [
    {
      id: "nvda-gap-001",
      type: "trade",
      title: "NVDA Gap Up +7.9%",
      source: "scanner",
      potentialValue: 100,
      status: "detected",
      detectedAt: "2026-02-06T22:34:00Z"
    },
    {
      id: "amd-gap-001",
      type: "trade", 
      title: "AMD Gap Up +8.3%",
      source: "scanner",
      potentialValue: 100,
      status: "detected",
      detectedAt: "2026-02-06T22:34:00Z"
    },
    {
      id: "pltr-gap-001",
      type: "trade",
      title: "PLTR Gap Up +4.5%",
      source: "scanner",
      potentialValue: 75,
      status: "detected",
      detectedAt: "2026-02-06T22:34:00Z"
    },
    {
      id: "smci-gap-001",
      type: "trade",
      title: "SMCI Gap Up +11.4%",
      source: "scanner",
      potentialValue: 150,
      status: "detected",
      detectedAt: "2026-02-06T22:34:00Z"
    }
  ],
  
  feed: [
    {
      timestamp: "2026-02-06T22:34:00Z",
      agent: "scanner",
      icon: "📈",
      message: "Trading scan complete - 4 alerts found"
    },
    {
      timestamp: "2026-02-06T22:34:00Z",
      agent: "scanner",
      icon: "⚡",
      message: "SMCI gap up +11.4% - strongest momentum"
    },
    {
      timestamp: "2026-02-06T22:34:00Z",
      agent: "scanner",
      icon: "⚡",
      message: "AMD gap up +8.3%"
    },
    {
      timestamp: "2026-02-06T22:34:00Z",
      agent: "scanner",
      icon: "⚡",
      message: "NVDA gap up +7.9%"
    },
    {
      timestamp: "2026-02-06T22:34:00Z",
      agent: "scanner",
      icon: "🔍",
      message: "Job scan complete - checking Upwork & Freelancer"
    },
    {
      timestamp: "2026-02-06T22:26:00Z",
      agent: "main",
      icon: "🚀",
      message: "Council Command Center deployed!"
    }
  ],
  
  nextActions: [
    "Review SMCI gap (+11.4%)",
    "Check AMD pre-market tomorrow",
    "Search for Make.com gigs manually"
  ]
};
