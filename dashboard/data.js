const DASHBOARD_DATA = {
  balance: 500,
  target: 2399,
  startDate: "2026-02-04",
  
  agents: {
    scanner: {
      status: "active",
      lastScan: "2026-02-06T22:15:00Z",
      scansToday: 47,
      hitsToday: 3
    },
    research: {
      status: "idle",
      lastTask: "Analyzed Upwork Python gig",
      queueCount: 2
    }
  },
  
  opportunities: [
    { id: 1, name: "Upwork Python API", type: "gig", amount: 500, stage: "detected", createdAt: "2026-02-06T21:30:00Z" },
    { id: 2, name: "Fiverr Data Script", type: "gig", amount: 150, stage: "researching", createdAt: "2026-02-06T20:00:00Z" },
    { id: 3, name: "Discord Bot Fix", type: "gig", amount: 75, stage: "ready", createdAt: "2026-02-06T18:00:00Z" },
    { id: 4, name: "ETH Swing Trade", type: "trade", amount: 200, stage: "detected", createdAt: "2026-02-06T22:00:00Z" },
    { id: 5, name: "Web Scraper Job", type: "gig", amount: 300, stage: "researching", createdAt: "2026-02-06T19:00:00Z" }
  ],
  
  feed: [
    { timestamp: "2026-02-06T22:15:00Z", agent: "scanner", message: "🔍 Found: Upwork Python API job $500" },
    { timestamp: "2026-02-06T22:00:00Z", agent: "scanner", message: "🔍 Found: ETH swing opportunity $200" },
    { timestamp: "2026-02-06T21:45:00Z", agent: "research", message: "📊 Analyzed: Fiverr Data Script - viable" },
    { timestamp: "2026-02-06T21:30:00Z", agent: "scanner", message: "🔍 Scan complete: 12 platforms checked" },
    { timestamp: "2026-02-06T21:00:00Z", agent: "research", message: "📊 Discord Bot Fix ready for action" },
    { timestamp: "2026-02-06T20:30:00Z", agent: "scanner", message: "🔍 Found: Web Scraper Job $300" },
    { timestamp: "2026-02-06T20:00:00Z", agent: "research", message: "📊 Queue updated: 2 items pending" }
  ],
  
  income: {
    freelance: 0,
    trading: 0,
    other: 0
  },
  
  nextActions: [
    { text: "Apply to Discord Bot Fix", done: false },
    { text: "Research Upwork Python gig", done: false },
    { text: "Set up trading alerts", done: true }
  ]
};
