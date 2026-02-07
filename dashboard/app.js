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

// Store opportunities globally for click access
window.opportunitiesData = [];

function renderPipeline(opportunities) {
  window.opportunitiesData = opportunities;
  
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
    const cards = items.map((opp, idx) => {
      
      return `
        <div class="opportunity-card ${opp.type} clickable" 
             onclick="showOpportunityDetail('${opp.id}')"
             data-id="${opp.id}">
          <div class="opp-name" title="${opp.name}">${opp.name}</div>
          <div class="opp-meta">
            <span class="opp-type">${opp.type}</span>
            <span class="opp-amount">${formatCurrency(opp.amount)}</span>
          </div>
          ${opp.recommendation ? `
          <div class="opp-meta" style="margin-top: 0.25rem;">
            <span class="recommendation ${opp.recommendation}">${opp.recommendation}</span>
            <span class="confidence">${opp.confidence || ''}</span>
          </div>
          ` : `
          <div class="opp-meta" style="margin-top: 0.25rem;">
            <span>${formatTime(opp.createdAt)}</span>
          </div>
          `}
        </div>
      `;
    }).join('');
    
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
    <div id="opportunity-modal" class="modal" onclick="closeModal(event)">
      <div class="modal-content" onclick="event.stopPropagation()">
        <span class="modal-close" onclick="closeModal()">&times;</span>
        <div id="modal-body"></div>
      </div>
    </div>
  `;
}

function showOpportunityDetail(id) {
  const opp = window.opportunitiesData.find(o => o.id === id);
  if (!opp) return;
  
  let html = `<h2>${opp.name}</h2>`;
  
  // Handle different types
  if (opp.type === 'trade' && opp.thesis) {
    // Trade with thesis
    const t = opp.thesis;
    html += `
      <div class="thesis-badge ${opp.recommendation || ''}">${opp.recommendation || 'ANALYZING'} ${opp.confidence ? '(' + opp.confidence + ')' : ''}</div>
      
      <div class="thesis-section">
        <h3>🐂 Bull Case</h3>
        <p>${t.bull_case || 'Momentum play based on price action'}</p>
      </div>
      
      <div class="thesis-section">
        <h3>🐻 Bear Case</h3>
        <p>${t.bear_case || 'Extended move may need consolidation'}</p>
      </div>
      
      <div class="thesis-levels">
        <div class="level entry">
          <span class="level-label">Entry</span>
          <span class="level-value">${t.entry ? '$' + t.entry.toFixed(2) : 'N/A'}</span>
        </div>
        <div class="level stop">
          <span class="level-label">Stop Loss</span>
          <span class="level-value">${t.stop_loss ? '$' + t.stop_loss.toFixed(2) : 'N/A'}</span>
        </div>
        <div class="level target">
          <span class="level-label">Target</span>
          <span class="level-value">${t.target ? '$' + t.target.toFixed(2) : 'N/A'}</span>
        </div>
      </div>
      
      <div class="thesis-rr">
        <strong>Risk/Reward:</strong> ${t.risk_reward || '2:1'}
      </div>
    `;
  } else if (opp.type === 'options') {
    // Options play
    html += `
      <div class="thesis-badge" style="background: #ff9800; color: #000;">OPTIONS PLAY</div>
      
      <div class="thesis-section">
        <h3>🎰 Signal</h3>
        <p>${opp.signal || 'Momentum-based options opportunity'}</p>
      </div>
      
      <div class="thesis-levels">
        <div class="level entry">
          <span class="level-label">Premium</span>
          <span class="level-value">$${(opp.amount / 100).toFixed(2)}</span>
        </div>
        <div class="level stop">
          <span class="level-label">IV</span>
          <span class="level-value">${opp.iv ? (opp.iv * 100).toFixed(1) + '%' : 'N/A'}</span>
        </div>
        <div class="level target">
          <span class="level-label">Risk</span>
          <span class="level-value">${opp.risk || 'MEDIUM'}</span>
        </div>
      </div>
      
      ${opp.underlying_price ? `
      <div class="thesis-rr">
        <strong>Underlying Price:</strong> $${opp.underlying_price.toFixed(2)}
      </div>
      ` : ''}
    `;
  } else if (opp.type === 'gig') {
    // Freelance gig
    html += `
      <div class="thesis-badge" style="background: #4CAF50; color: #fff;">FREELANCE GIG</div>
      
      <div class="thesis-section">
        <h3>💼 Opportunity</h3>
        <p>Potential freelance project worth ~$${opp.amount}</p>
      </div>
      
      <div class="thesis-levels">
        <div class="level entry" style="grid-column: span 3;">
          <span class="level-label">Estimated Value</span>
          <span class="level-value">$${opp.amount}</span>
        </div>
      </div>
      
      ${opp.url ? `
      <div style="margin-top: 1rem; text-align: center;">
        <a href="${opp.url}" target="_blank" style="color: #00d9ff; text-decoration: underline;">View on Platform →</a>
      </div>
      ` : ''}
    `;
  } else {
    // Generic fallback
    html += `
      <div class="thesis-section">
        <h3>📋 Details</h3>
        <p>Type: ${opp.type}</p>
        <p>Value: $${opp.amount}</p>
        <p>Stage: ${opp.stage}</p>
      </div>
    `;
  }
  
  document.getElementById('modal-body').innerHTML = html;
  document.getElementById('opportunity-modal').classList.add('show');
}
function closeModal(event) {
  if (event && event.target.id !== 'opportunity-modal') return;
  document.getElementById('opportunity-modal').classList.remove('show');
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
