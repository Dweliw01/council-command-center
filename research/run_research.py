#!/usr/bin/env python3
"""
Research Agent Orchestrator - Processes pending opportunities.

Reads detected opportunities from state, runs appropriate analyzers,
updates state with analysis results, and logs activity to feed.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from trade_analyzer import analyze_trade
from gig_analyzer import analyze_gig


# Paths
STATE_DIR = Path("/root/council-command-center/council/state")
OPPORTUNITIES_FILE = STATE_DIR / "opportunities.json"
FEED_FILE = STATE_DIR / "feed.json"


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file, return empty dict if not exists."""
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: Dict[str, Any]):
    """Save data to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def add_feed_entry(message: str, icon: str = "📊"):
    """Add entry to activity feed."""
    feed = load_json(FEED_FILE)
    
    if "entries" not in feed:
        feed["entries"] = []
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": "research",
        "icon": icon,
        "message": message
    }
    
    feed["entries"].insert(0, entry)
    
    # Keep last 100 entries
    feed["entries"] = feed["entries"][:100]
    
    save_json(FEED_FILE, feed)


def process_trading_alerts(opportunities: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process trading alerts and return analyzed items."""
    results = []
    trading = opportunities.get("trading", {})
    alerts = trading.get("alerts", [])
    
    # Check if already analyzed
    analyzed = trading.get("analyzed", {})
    
    for alert in alerts:
        symbol = alert.get("symbol", "")
        
        # Skip if already analyzed recently
        if symbol in analyzed:
            existing = analyzed[symbol]
            # Skip if analyzed within last hour
            analyzed_at = existing.get("analyzed_at", "")
            if analyzed_at:
                try:
                    analyzed_time = datetime.fromisoformat(analyzed_at.replace('Z', '+00:00'))
                    age_hours = (datetime.now().astimezone() - analyzed_time).total_seconds() / 3600
                    if age_hours < 1:
                        continue
                except:
                    pass
        
        # Analyze the trade
        print(f"📊 Analyzing trade: {symbol}...")
        analysis = analyze_trade(alert)
        
        # Store result
        analyzed[symbol] = analysis
        results.append(analysis)
        
        # Log to feed
        rec = analysis.get("recommendation", "WATCH")
        rr = analysis.get("thesis", {}).get("risk_reward", "N/A")
        add_feed_entry(
            f"Analyzed {symbol}: {rec} recommendation ({rr} R/R)",
            icon="📈" if rec in ["BUY_NOW", "BUY_DIP"] else "📊"
        )
        print(f"   → {rec} ({analysis.get('confidence', 'unknown')} confidence)")
    
    return results


def process_job_opportunities(opportunities: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process job opportunities and return analyzed items."""
    results = []
    jobs = opportunities.get("jobs", {})
    new_opps = jobs.get("new_opportunities", [])
    
    # Check existing analyzed jobs
    analyzed = jobs.get("analyzed", {})
    
    for job in new_opps:
        title = job.get("title", "")
        job_id = job.get("url", title)  # Use URL as ID if available
        
        # Skip if already analyzed
        if job_id in analyzed:
            continue
        
        # Analyze the gig
        print(f"💼 Analyzing gig: {title[:50]}...")
        analysis = analyze_gig(job)
        
        # Store result
        analyzed[job_id] = analysis
        results.append(analysis)
        
        # Log to feed
        rec = analysis.get("recommendation", "PASS")
        score = analysis.get("analysis", {}).get("relevance_score", 0)
        add_feed_entry(
            f"Analyzed gig: {title[:40]}... → {rec} (relevance: {score}/10)",
            icon="💼" if rec == "APPLY" else "📋"
        )
        print(f"   → {rec} ({analysis.get('confidence', 'unknown')} confidence)")
    
    return results


def run_research():
    """Main research orchestration."""
    print("🔬 Starting Research Agent...")
    print("=" * 50)
    
    # Load current opportunities
    opportunities = load_json(OPPORTUNITIES_FILE)
    
    if not opportunities:
        print("No opportunities file found. Run scanner first.")
        return
    
    # Process trading alerts
    trading = opportunities.get("trading", {})
    if "analyzed" not in trading:
        trading["analyzed"] = {}
    
    trade_results = process_trading_alerts(opportunities)
    
    # Update trading section with analyzed data
    opportunities["trading"] = trading
    opportunities["trading"]["analyzed"] = trading.get("analyzed", {})
    for result in trade_results:
        symbol = result.get("symbol", "")
        if symbol:
            opportunities["trading"]["analyzed"][symbol] = result
    
    # Process job opportunities
    jobs = opportunities.get("jobs", {})
    if "analyzed" not in jobs:
        jobs["analyzed"] = {}
    
    job_results = process_job_opportunities(opportunities)
    
    # Update jobs section with analyzed data
    opportunities["jobs"] = jobs
    for result in job_results:
        job_id = result.get("url", result.get("title", ""))
        if job_id:
            opportunities["jobs"]["analyzed"][job_id] = result
    
    # Update research timestamp
    opportunities["last_research"] = datetime.utcnow().isoformat() + "Z"
    
    # Calculate summary
    trade_ready = sum(
        1 for a in opportunities.get("trading", {}).get("analyzed", {}).values()
        if a.get("stage") == "ready"
    )
    gig_ready = sum(
        1 for a in opportunities.get("jobs", {}).get("analyzed", {}).values()
        if a.get("stage") == "ready"
    )
    
    opportunities["research_summary"] = {
        "trades_analyzed": len(trade_results),
        "gigs_analyzed": len(job_results),
        "trades_ready": trade_ready,
        "gigs_ready": gig_ready,
        "last_run": datetime.utcnow().isoformat() + "Z"
    }
    
    # Save updated opportunities
    save_json(OPPORTUNITIES_FILE, opportunities)
    
    # Print summary
    print("=" * 50)
    print("📊 Research Summary:")
    print(f"   Trades analyzed: {len(trade_results)}")
    print(f"   Gigs analyzed: {len(job_results)}")
    print(f"   Trades ready for action: {trade_ready}")
    print(f"   Gigs ready to apply: {gig_ready}")
    
    # Log completion to feed
    if trade_results or job_results:
        add_feed_entry(
            f"Research complete: {len(trade_results)} trades, {len(job_results)} gigs analyzed",
            icon="✅"
        )
    
    print("\n✅ Research complete!")
    return opportunities


def get_ready_opportunities(opportunities: Optional[Dict] = None) -> Dict[str, Any]:
    """Get all opportunities in 'ready' stage."""
    if opportunities is None:
        opportunities = load_json(OPPORTUNITIES_FILE)
    
    ready = {
        "trades": [],
        "gigs": []
    }
    
    # Get ready trades
    for symbol, analysis in opportunities.get("trading", {}).get("analyzed", {}).items():
        if analysis.get("stage") == "ready":
            ready["trades"].append(analysis)
    
    # Get ready gigs
    for job_id, analysis in opportunities.get("jobs", {}).get("analyzed", {}).items():
        if analysis.get("stage") == "ready":
            ready["gigs"].append(analysis)
    
    # Sort by confidence
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    ready["trades"].sort(key=lambda x: confidence_order.get(x.get("confidence", "low"), 3))
    ready["gigs"].sort(key=lambda x: confidence_order.get(x.get("confidence", "low"), 3))
    
    return ready


if __name__ == "__main__":
    run_research()
