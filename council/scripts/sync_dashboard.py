#!/usr/bin/env python3
"""
Council Command Center - Dashboard Sync
Reads scanner output and generates dashboard/data.js
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
COUNCIL_DIR = SCRIPT_DIR.parent
ROOT_DIR = COUNCIL_DIR.parent
STATE_DIR = COUNCIL_DIR / "state"
DASHBOARD_DIR = ROOT_DIR / "dashboard"

OPPORTUNITIES_FILE = STATE_DIR / "opportunities.json"
DASHBOARD_STATE_FILE = STATE_DIR / "dashboard.json"
FEED_FILE = STATE_DIR / "feed.json"
DATA_JS_FILE = DASHBOARD_DIR / "data.js"


def read_json(path):
    """Read JSON file, return empty dict if not found."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def sync_dashboard():
    """Convert scanner output to dashboard data.js format."""
    
    # Read scanner output
    opps = read_json(OPPORTUNITIES_FILE)
    dashboard_state = read_json(DASHBOARD_STATE_FILE)
    feed_state = read_json(FEED_FILE)
    
    # Extract trading alerts and convert to opportunities
    opportunities = []
    trading = opps.get("trading", {})
    alerts = trading.get("alerts", [])
    analyzed = trading.get("analyzed", {})  # Research results
    
    for alert in alerts:
        symbol = alert['symbol']
        # Check if research has analyzed this alert
        research = analyzed.get(symbol, {})
        stage = research.get("stage", "detected")
        
        opp = {
            "id": f"{symbol.lower()}-{datetime.now().strftime('%Y%m%d')}",
            "name": f"{symbol} {alert['signal']} {alert['change_pct']:+.1f}%",
            "type": "trade",
            "amount": int(abs(alert['change_pct']) * 15),  # Rough potential value
            "stage": stage,
            "createdAt": opps.get("last_scan", datetime.now().isoformat())
        }
        
        # Add research data if available
        if research:
            opp["recommendation"] = research.get("recommendation")
            opp["confidence"] = research.get("confidence")
            opp["thesis"] = research.get("thesis", {})
        
        opportunities.append(opp)
    
    # Extract job opportunities
    jobs = opps.get("jobs", {})
    new_jobs = jobs.get("new_opportunities", [])
    
    for job in new_jobs:
        title = job.get("title", "").strip()
        # Skip jobs without titles
        if not title:
            continue
        opportunities.append({
            "id": job.get("id", "unknown"),
            "name": title[:50],
            "type": "gig",
            "amount": job.get("budget", 300),  # Use budget if available
            "stage": "detected",
            "createdAt": job.get("discovered_at", datetime.now().isoformat()),
            "url": job.get("url", "")
        })
    
    # Extract options plays
    options = opps.get("options", {})
    options_alerts = options.get("alerts", [])
    
    for opt in options_alerts:
        symbol = opt.get("symbol", "???")
        direction = opt.get("direction", "CALLS")
        strike = opt.get("strike", 0)
        expiry = opt.get("expiry", "")
        risk = opt.get("risk", "MEDIUM")
        
        opportunities.append({
            "id": f"opt-{symbol.lower()}-{strike}-{datetime.now().strftime('%Y%m%d')}",
            "name": f"🎰 {symbol} {direction} ${strike} ({expiry[:5]})",
            "type": "options",
            "amount": int(opt.get("premium", 1) * 100),  # Premium * 100 shares
            "stage": "ready",  # Options are immediately actionable
            "createdAt": options.get("scan_time", datetime.now().isoformat()),
            "risk": risk,
            "signal": opt.get("signal", ""),
            "iv": opt.get("iv", 0),
            "underlying_price": opt.get("underlying_price", 0)
        })
    
    # Build dashboard data
    now = datetime.now().isoformat() + "Z"
    
    balance = dashboard_state.get("balance", 500)
    target = dashboard_state.get("target", 2399)
    progress = round((balance / target) * 100, 1) if target > 0 else 0
    
    data = {
        "balance": balance,
        "target": target,
        "progress": progress,
        "startDate": dashboard_state.get("startDate", "2026-02-04"),
        "lastUpdate": now,
        "agents": {
            "scanner": {
                "status": "active" if alerts or new_jobs else "idle",
                "lastScan": opps.get("last_scan", now),
                "scansToday": dashboard_state.get("agents", {}).get("scanner", {}).get("runsToday", 1),
                "hitsToday": len(alerts) + len(new_jobs)
            },
            "research": {
                "status": "idle",
                "lastTask": "Awaiting opportunities",
                "queueCount": len(opportunities)
            }
        },
        "income": dashboard_state.get("income", {"freelance": 0, "trading": 0, "other": 0}),
        "opportunities": opportunities,
        "feed": feed_state.get("entries", [
            {
                "timestamp": now,
                "agent": "scanner",
                "icon": "📈",
                "message": f"Scan complete - {len(alerts)} alerts, {len(new_jobs)} jobs"
            }
        ])[-10:],  # Last 10 feed entries
        "nextActions": [
            {"text": f"Review {len(opportunities)} opportunities" if opportunities else "Run scanner for opportunities", "done": False},
            {"text": "Check market status", "done": False}
        ]
    }
    
    # Generate JavaScript
    js_content = f"""// Auto-generated by sync_dashboard.py
// Last sync: {now}

const DASHBOARD_DATA = {json.dumps(data, indent=2)};
"""
    
    # Write to data.js
    DATA_JS_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_JS_FILE, 'w') as f:
        f.write(js_content)
    
    print(f"✅ Dashboard synced: {len(opportunities)} opportunities")
    return data


if __name__ == "__main__":
    sync_dashboard()
