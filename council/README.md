# Council Command Center - State Management

Shared state layer for all Council agents to read/write to.

## Directory Structure

```
council/
├── README.md           # This file
├── state/              # JSON state files
│   ├── dashboard.json  # Main dashboard state (balance, agents, income)
│   ├── opportunities.json  # Opportunity pipeline
│   └── feed.json       # Activity log
└── scripts/            # Python utilities
    ├── update_state.py # State management functions
    ├── sync_dashboard.py  # Sync state to dashboard
    └── requirements.txt   # Dependencies
```

## State Files

### dashboard.json
Main dashboard state including:
- `balance` - Current balance
- `target` - Target amount ($2399)
- `startDate` - Challenge start date
- `agents` - Agent statuses (scanner, research)
- `income` - Income breakdown by category

### opportunities.json
Opportunity pipeline with stages:
- `detected` - Newly discovered opportunities
- `researching` - Being researched for viability
- `ready` - Ready to pursue
- `won` - Successfully completed

### feed.json
Activity log with entries containing:
- `timestamp` - ISO8601 timestamp
- `agent` - Which agent logged it
- `icon` - Emoji icon
- `message` - Log message

## Usage

### Python API

```python
from council.scripts.update_state import (
    add_opportunity,
    move_opportunity,
    log_activity,
    update_agent_status,
    update_balance,
    add_income,
    get_dashboard_data
)

# Add a new opportunity
opp_id = add_opportunity({
    "type": "gig",
    "title": "Make.com automation project",
    "source": "upwork",
    "url": "https://upwork.com/job/123",
    "potentialValue": 500
})

# Move through pipeline
move_opportunity(opp_id, "researching")
move_opportunity(opp_id, "ready")
move_opportunity(opp_id, "won")

# Log activity
log_activity("scanner", "🔍", "Found Upwork job: Make.com specialist $500")

# Update agent status
update_agent_status("scanner", "running", {"runsToday": 5, "hitsToday": 3})

# Update balance
update_balance(650)

# Add income (automatically updates balance)
add_income("freelance", 150)

# Get merged dashboard data
data = get_dashboard_data()
print(f"Progress: {data['progress']}%")
```

### CLI

```bash
# Show dashboard status
python scripts/update_state.py status

# Log activity
python scripts/update_state.py log scanner 🔍 "Found new opportunity"

# Update balance
python scripts/update_state.py balance 650

# Show pipeline
python scripts/update_state.py pipeline

# Sync to dashboard
python scripts/sync_dashboard.py

# Sync with HTML fallback generation
python scripts/sync_dashboard.py --with-html
```

## Agent Integration

### Scanner Agent
```python
from council.scripts.update_state import add_opportunity, log_activity, update_agent_status

# On scan start
update_agent_status("scanner", "running")

# On opportunity found
opp_id = add_opportunity({...})
log_activity("scanner", "🔍", f"Found: {title}")

# On scan complete
update_agent_status("scanner", "idle", {
    "lastRun": datetime.utcnow().isoformat() + "Z",
    "runsToday": runs + 1,
    "hitsToday": hits
})
```

### Research Agent
```python
from council.scripts.update_state import move_opportunity, log_activity, update_agent_status

# Pick up opportunity
move_opportunity(opp_id, "researching")
update_agent_status("research", "running", {"queueLength": len(queue)})

# After research
move_opportunity(opp_id, "ready")  # or "passed"
log_activity("research", "📊", f"Researched: {title} - viable!")
```

## File Locking

All state operations use file locking (`fcntl`) to ensure safe concurrent access from multiple agents.

## Dashboard Sync

After modifying state, run `sync_dashboard.py` to update the web dashboard:

```bash
python scripts/sync_dashboard.py
```

This generates `dashboard/data.js` which the dashboard HTML loads.
