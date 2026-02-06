// Council Command Center Dashboard

function formatCurrency(amount) {
  return '$' + amount.toLocaleString();
}

function formatTime(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  
  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString();
}

function formatTimeShort(isoString) {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function getDaysElapsed(startDate) {
  const start = new Date(startDate);
  const now = new Date();
  return Math.floor((now - start) / (1000 * 60 * 60 * 24));
}

function calculateDailyTarget(remaining, daysLeft = 30) {
  return Math.ceil(remaining / daysLeft);
}

function renderProgressHeader(data) {
  const progress = (data.balance / data.target) * 100;
  const remaining = data.target - data.balance;
  const daysElapsed = getDaysElapsed(data.startDate);
  const dailyTarget = calculateDailyTarget(remaining, 30 - daysElapsed);
  
  return `
    <div class="progress-header">
      <div class="progress-title">
        <h1>🎯 Council Command Center</h1>
        <span class="progress-amount">${formatCurrency(data.balance)} / ${formatCurrency(data.target)}</span>
      </div>
      <div class="progress-bar-container">
        <div class="progress-bar" style="width: ${Math.min(progress, 100)}%">
          ${progress.toFixed(1)}%
        </div>
      </div>
      <div class="progress-stats">
        <div class="stat-item">
          <span class="stat-label">Days Elapsed</span>
          <span class="stat-value">${daysElapsed}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Remaining</span>
          <span class="stat-value">${formatCurrency(remaining)}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Daily Target</span>
          <span class="stat-value">${formatCurrency(dailyTarget)}/day</span>
        </div>
      </div>
    </div>
  `;
}

function renderAgentCards(agents) {
  return `
    <div class="agents-grid">
      <div class="agent-card scanner">
        <div class="agent-header">
          <span class="agent-name"><span class="agent-icon">🔍</span> Scanner</span>
          <span class="status-badge ${agents.scanner.status}">${agents.scanner.status}</span>
        </div>
        <div class="agent-stats">
          <div class="agent-stat">
            <span class="agent-stat-label">Last Scan</span>
            <span class="agent-stat-value">${formatTime(agents.scanner.lastScan)}</span>
          </div>
          <div class="agent-stat">
            <span class="agent-stat-label">Scans Today</span>
            <span class="agent-stat-value">${agents.scanner.scansToday}</span>
          </div>
          <div class="agent-stat">
            <span class="agent-stat-label">Hits Today</span>
            <span class="agent-stat-value">${agents.scanner.hitsToday}</span>
          </div>
        </div>
      </div>
      
      <div class="agent-card research">
        <div class="agent-header">
          <span class="agent-name"><span class="agent-icon">📊</span> Research</span>
          <span class="status-badge ${agents.research.status}">${agents.research.status}</span>
        </div>
        <div class="agent-stats">
          <div class="agent-stat">
            <span class="agent-stat-label">Last Task</span>
            <span class="agent-stat-value">${agents.research.lastTask}</span>
          </div>
          <div class="agent-stat">
            <span class="agent-stat-label">Queue</span>
            <span class="agent-stat-value">${agents.research.queueCount} items</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderPipeline(opportunities) {
  const stages = ['detected', 'researching', 'ready', 'won'];
  const stageLabels = {
    detected: 'Detected',
    researching: 'Researching',
    ready: 'Ready',
    won: 'Won'
  };
  
  const grouped = stages.reduce((acc, stage) => {
    acc[stage] = opportunities.filter(o => o.stage === stage);
    return acc;
  }, {});
  
  const columns = stages.map(stage => {
    const items = grouped[stage];
    const cards = items.map(opp => `
      <div class="opportunity-card ${opp.type}">
        <div class="opp-name" title="${opp.name}">${opp.name}</div>
        <div class="opp-meta">
          <span class="opp-type">${opp.type}</span>
          <span class="opp-amount">${formatCurrency(opp.amount)}</span>
        </div>
        <div class="opp-meta" style="margin-top: 0.25rem;">
          <span>${formatTime(opp.createdAt)}</span>
        </div>
      </div>
    `).join('');
    
    return `
      <div class="pipeline-column">
        <div class="column-header">
          ${stageLabels[stage]}
          <span class="column-count">${items.length}</span>
        </div>
        ${cards}
      </div>
    `;
  }).join('');
  
  return `
    <div class="pipeline-section">
      <h2 class="section-title">📋 Opportunity Pipeline</h2>
      <div class="pipeline">
        ${columns}
      </div>
    </div>
  `;
}

function renderFeed(feed) {
  const items = feed.map(item => `
    <div class="feed-item ${item.agent}">
      <span class="feed-time">${formatTimeShort(item.timestamp)}</span>
      <span class="feed-message">${item.message}</span>
    </div>
  `).join('');
  
  return `
    <div class="feed-section">
      <h2 class="section-title">📡 Live Feed</h2>
      <div class="feed-container">
        ${items}
      </div>
    </div>
  `;
}

function renderBottomStats(data) {
  const total = data.income.freelance + data.income.trading + data.income.other;
  
  const actionItems = data.nextActions.map(action => `
    <div class="checklist-item ${action.done ? 'done' : ''}">
      <div class="checkbox"></div>
      <span>${action.text}</span>
    </div>
  `).join('');
  
  return `
    <div class="bottom-stats">
      <div class="income-tracker">
        <h2 class="section-title">💰 Income Tracker</h2>
        <div class="income-grid">
          <div class="income-item">
            <div class="income-label">Freelance</div>
            <div class="income-value">${formatCurrency(data.income.freelance)}</div>
          </div>
          <div class="income-item">
            <div class="income-label">Trading</div>
            <div class="income-value">${formatCurrency(data.income.trading)}</div>
          </div>
          <div class="income-item">
            <div class="income-label">Total</div>
            <div class="income-value total">${formatCurrency(total)}</div>
          </div>
        </div>
      </div>
      
      <div class="next-actions">
        <h2 class="section-title">✅ Next Actions</h2>
        <div class="checklist">
          ${actionItems}
        </div>
      </div>
    </div>
  `;
}

function renderDashboard() {
  const app = document.getElementById('app');
  
  app.innerHTML = `
    <div class="container">
      ${renderProgressHeader(DASHBOARD_DATA)}
      ${renderAgentCards(DASHBOARD_DATA.agents)}
      ${renderPipeline(DASHBOARD_DATA.opportunities)}
      ${renderFeed(DASHBOARD_DATA.feed)}
      ${renderBottomStats(DASHBOARD_DATA)}
    </div>
  `;
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', renderDashboard);

// Auto-refresh every 30 seconds (for when data updates)
setInterval(renderDashboard, 30000);
