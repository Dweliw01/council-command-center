#!/usr/bin/env python3
"""
Telegram notification module for Council Command Center.
Sends alerts with inline action buttons.
"""

import json
import os
from datetime import datetime

def format_trading_alert(alert):
    """Format a trading alert for Telegram."""
    symbol = alert["symbol"]
    price = alert["price"]
    change = alert["change_pct"]
    signal = alert["signal"]
    
    emoji = "🟢" if change > 0 else "🔴"
    direction = "↑" if change > 0 else "↓"
    
    return f"{emoji} **{symbol}** ${price:.2f} ({direction}{abs(change):.1f}%)\n   Signal: {signal}"

def format_job_alert(job):
    """Format a job opportunity for Telegram."""
    title = job.get("title", "Unknown")[:50]
    source = job.get("source", "unknown")
    url = job.get("url", "")
    
    return f"💼 **{title}**\n   Source: {source}\n   {url}"

def create_alert_message(scan_results):
    """Create a formatted alert message from scan results."""
    lines = []
    lines.append("🎯 **Council Scanner Alert**")
    lines.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC")
    lines.append("")
    
    # Trading alerts
    trading = scan_results.get("trading", {})
    alerts = trading.get("alerts", [])
    if alerts:
        lines.append(f"📈 **Trading Alerts** ({len(alerts)})")
        for alert in alerts[:5]:  # Top 5
            lines.append(format_trading_alert(alert))
        lines.append("")
    
    # Job alerts
    jobs = scan_results.get("jobs", {})
    new_jobs = jobs.get("new_opportunities", [])
    if new_jobs:
        lines.append(f"💼 **New Jobs** ({len(new_jobs)})")
        for job in new_jobs[:3]:  # Top 3
            lines.append(format_job_alert(job))
        lines.append("")
    
    if not alerts and not new_jobs:
        return None  # Nothing to report
    
    lines.append("📊 Dashboard: https://dashboard-six-sigma-48.vercel.app")
    
    return "\n".join(lines)

def should_alert(scan_results):
    """Determine if we should send an alert based on results."""
    trading = scan_results.get("trading", {})
    alerts = trading.get("alerts", [])
    
    jobs = scan_results.get("jobs", {})
    new_jobs = jobs.get("new_opportunities", [])
    
    # Alert if any trading signal > 5% or any new jobs
    high_momentum = any(abs(a.get("change_pct", 0)) > 5 for a in alerts)
    
    return high_momentum or len(new_jobs) > 0

if __name__ == "__main__":
    # Test with sample data
    sample = {
        "trading": {
            "alerts": [
                {"symbol": "SMCI", "price": 950.0, "change_pct": 11.4, "signal": "GAP_UP"},
                {"symbol": "AMD", "price": 208.0, "change_pct": 8.3, "signal": "GAP_UP"}
            ]
        },
        "jobs": {
            "new_opportunities": []
        }
    }
    
    msg = create_alert_message(sample)
    if msg:
        print(msg)
        print("\nShould alert:", should_alert(sample))
