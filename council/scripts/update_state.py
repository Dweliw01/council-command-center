#!/usr/bin/env python3
"""
Council Command Center - State Management

Provides functions to read/write shared state that all agents use.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import fcntl

# Paths
STATE_DIR = Path(__file__).parent.parent / "state"
DASHBOARD_FILE = STATE_DIR / "dashboard.json"
OPPORTUNITIES_FILE = STATE_DIR / "opportunities.json"
FEED_FILE = STATE_DIR / "feed.json"

# Feed size limit
MAX_FEED_ENTRIES = 100


def _read_json(path: Path) -> Dict:
    """Read JSON file with file locking for safety."""
    with open(path, 'r') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data


def _write_json(path: Path, data: Dict) -> None:
    """Write JSON file with file locking for safety."""
    with open(path, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, indent=2)
        f.write('\n')
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _now_iso() -> str:
    """Return current UTC time in ISO8601 format."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ============================================================
# OPPORTUNITY MANAGEMENT
# ============================================================

def add_opportunity(opp_data: Dict[str, Any]) -> str:
    """
    Add a new opportunity to the 'detected' stage.
    
    Args:
        opp_data: Dict with keys: type, title, source, url, potentialValue, notes (optional)
    
    Returns:
        The generated opportunity ID
    """
    opps = _read_json(OPPORTUNITIES_FILE)
    
    opp_id = str(uuid.uuid4())[:8]
    opportunity = {
        "id": opp_id,
        "type": opp_data.get("type", "gig"),
        "title": opp_data["title"],
        "source": opp_data.get("source", "scanner"),
        "url": opp_data.get("url", ""),
        "potentialValue": opp_data.get("potentialValue", 0),
        "detectedAt": _now_iso(),
        "status": "detected",
        "notes": opp_data.get("notes", "")
    }
    
    opps["pipeline"]["detected"].append(opportunity)
    opps["lastUpdate"] = _now_iso()
    
    _write_json(OPPORTUNITIES_FILE, opps)
    return opp_id


def move_opportunity(opp_id: str, new_status: str) -> bool:
    """
    Move an opportunity between pipeline stages.
    
    Args:
        opp_id: The opportunity ID
        new_status: One of: detected, researching, ready, won, passed
    
    Returns:
        True if moved successfully, False if not found
    """
    opps = _read_json(OPPORTUNITIES_FILE)
    
    valid_stages = ["detected", "researching", "ready", "won", "passed"]
    if new_status not in valid_stages:
        raise ValueError(f"Invalid status: {new_status}. Must be one of: {valid_stages}")
    
    # Find and remove from current stage
    found_opp = None
    for stage in ["detected", "researching", "ready", "won"]:
        for i, opp in enumerate(opps["pipeline"].get(stage, [])):
            if opp["id"] == opp_id:
                found_opp = opps["pipeline"][stage].pop(i)
                break
        if found_opp:
            break
    
    if not found_opp:
        return False
    
    # Update status and add to new stage
    found_opp["status"] = new_status
    
    # 'passed' opportunities are discarded (not tracked in pipeline)
    if new_status != "passed":
        opps["pipeline"][new_status].append(found_opp)
    
    opps["lastUpdate"] = _now_iso()
    _write_json(OPPORTUNITIES_FILE, opps)
    return True


def get_opportunity(opp_id: str) -> Optional[Dict]:
    """Get an opportunity by ID."""
    opps = _read_json(OPPORTUNITIES_FILE)
    
    for stage in ["detected", "researching", "ready", "won"]:
        for opp in opps["pipeline"].get(stage, []):
            if opp["id"] == opp_id:
                return opp
    return None


def get_pipeline() -> Dict[str, List[Dict]]:
    """Get the full opportunity pipeline."""
    opps = _read_json(OPPORTUNITIES_FILE)
    return opps["pipeline"]


# ============================================================
# ACTIVITY FEED
# ============================================================

def log_activity(agent: str, icon: str, message: str) -> None:
    """
    Add an entry to the activity feed.
    
    Args:
        agent: The agent name (scanner, research, main)
        icon: Emoji icon for the entry
        message: Log message
    """
    feed = _read_json(FEED_FILE)
    
    entry = {
        "timestamp": _now_iso(),
        "agent": agent,
        "icon": icon,
        "message": message
    }
    
    # Add to beginning (newest first)
    feed["entries"].insert(0, entry)
    
    # Trim old entries
    if len(feed["entries"]) > MAX_FEED_ENTRIES:
        feed["entries"] = feed["entries"][:MAX_FEED_ENTRIES]
    
    _write_json(FEED_FILE, feed)


def get_feed(limit: int = 20) -> List[Dict]:
    """Get recent feed entries."""
    feed = _read_json(FEED_FILE)
    return feed["entries"][:limit]


# ============================================================
# AGENT STATUS
# ============================================================

def update_agent_status(agent: str, status: str, stats: Optional[Dict] = None) -> None:
    """
    Update an agent's status and stats.
    
    Args:
        agent: Agent name (scanner, research)
        status: Status string (idle, running, error)
        stats: Optional dict with agent-specific stats (lastRun, runsToday, hitsToday, queueLength)
    """
    dashboard = _read_json(DASHBOARD_FILE)
    
    if agent not in dashboard["agents"]:
        dashboard["agents"][agent] = {"status": "idle"}
    
    dashboard["agents"][agent]["status"] = status
    
    if stats:
        dashboard["agents"][agent].update(stats)
    
    dashboard["lastUpdate"] = _now_iso()
    _write_json(DASHBOARD_FILE, dashboard)


def get_agent_status(agent: str) -> Optional[Dict]:
    """Get an agent's current status."""
    dashboard = _read_json(DASHBOARD_FILE)
    return dashboard["agents"].get(agent)


# ============================================================
# BALANCE & INCOME
# ============================================================

def update_balance(new_balance: float) -> Dict:
    """
    Update the current balance.
    
    Args:
        new_balance: The new balance amount
    
    Returns:
        Dict with balance, target, and progress percentage
    """
    dashboard = _read_json(DASHBOARD_FILE)
    
    dashboard["balance"] = new_balance
    dashboard["lastUpdate"] = _now_iso()
    
    _write_json(DASHBOARD_FILE, dashboard)
    
    progress = (new_balance / dashboard["target"]) * 100 if dashboard["target"] > 0 else 0
    
    return {
        "balance": new_balance,
        "target": dashboard["target"],
        "progress": round(progress, 1)
    }


def add_income(category: str, amount: float) -> float:
    """
    Add income to a category and update balance.
    
    Args:
        category: Income category (freelance, trading, other)
        amount: Amount to add
    
    Returns:
        New total balance
    """
    dashboard = _read_json(DASHBOARD_FILE)
    
    if category not in dashboard["income"]:
        dashboard["income"][category] = 0
    
    dashboard["income"][category] += amount
    dashboard["balance"] += amount
    dashboard["lastUpdate"] = _now_iso()
    
    _write_json(DASHBOARD_FILE, dashboard)
    return dashboard["balance"]


# ============================================================
# DASHBOARD DATA
# ============================================================

def get_dashboard_data() -> Dict:
    """
    Get merged state for the dashboard.
    
    Returns:
        Dict containing all dashboard data merged together
    """
    dashboard = _read_json(DASHBOARD_FILE)
    opps = _read_json(OPPORTUNITIES_FILE)
    feed = _read_json(FEED_FILE)
    
    # Calculate pipeline counts
    pipeline_counts = {
        stage: len(items) for stage, items in opps["pipeline"].items()
    }
    
    # Calculate total pipeline value
    total_pipeline_value = sum(
        opp["potentialValue"]
        for stage in opps["pipeline"].values()
        for opp in stage
    )
    
    # Calculate progress
    progress = (dashboard["balance"] / dashboard["target"]) * 100 if dashboard["target"] > 0 else 0
    
    return {
        "balance": dashboard["balance"],
        "target": dashboard["target"],
        "progress": round(progress, 1),
        "startDate": dashboard["startDate"],
        "lastUpdate": dashboard["lastUpdate"],
        "agents": dashboard["agents"],
        "income": dashboard["income"],
        "pipeline": opps["pipeline"],
        "pipelineCounts": pipeline_counts,
        "pipelineValue": total_pipeline_value,
        "feed": feed["entries"][:20]
    }


# ============================================================
# CLI INTERFACE
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: update_state.py <command> [args]")
        print("\nCommands:")
        print("  status              - Show dashboard status")
        print("  log <agent> <icon> <msg> - Log activity")
        print("  balance <amount>    - Update balance")
        print("  pipeline            - Show pipeline counts")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        data = get_dashboard_data()
        print(f"💰 Balance: ${data['balance']} / ${data['target']} ({data['progress']}%)")
        print(f"📊 Pipeline: {data['pipelineCounts']} (${data['pipelineValue']} potential)")
        for agent, info in data['agents'].items():
            print(f"🤖 {agent}: {info['status']}")
    
    elif cmd == "log" and len(sys.argv) >= 5:
        agent, icon, message = sys.argv[2], sys.argv[3], " ".join(sys.argv[4:])
        log_activity(agent, icon, message)
        print(f"✅ Logged: {icon} [{agent}] {message}")
    
    elif cmd == "balance" and len(sys.argv) >= 3:
        new_balance = float(sys.argv[2])
        result = update_balance(new_balance)
        print(f"✅ Balance updated: ${result['balance']} ({result['progress']}% of target)")
    
    elif cmd == "pipeline":
        pipeline = get_pipeline()
        for stage, items in pipeline.items():
            value = sum(o["potentialValue"] for o in items)
            print(f"{stage}: {len(items)} opportunities (${value})")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
