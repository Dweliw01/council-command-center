#!/usr/bin/env python3
"""
Scanner Runner - Orchestrates job and trading scanners
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Import scanners
from job_scanner import scan_jobs
from trading_scanner import scan_trading

# Output path for combined opportunities
OUTPUT_FILE = Path("/root/council-command-center/council/state/opportunities.json")


def run_all_scans() -> dict:
    """Run all scanners and combine results"""
    scan_time = datetime.utcnow().isoformat() + "Z"
    
    print("=" * 50)
    print(f"Scanner Run: {scan_time}")
    print("=" * 50)
    
    # Run job scanner
    print("\n📋 JOB SCANNER")
    print("-" * 30)
    try:
        job_results = scan_jobs()
        job_count = len(job_results.get("new_opportunities", []))
        print(f"Found {job_count} new job opportunities")
    except Exception as e:
        print(f"Job scanner error: {e}")
        job_results = {"scan_time": scan_time, "new_opportunities": [], "error": str(e)}
    
    # Run trading scanner
    print("\n📈 TRADING SCANNER")
    print("-" * 30)
    try:
        trading_results = scan_trading()
        alert_count = len(trading_results.get("alerts", []))
        print(f"Found {alert_count} trading alerts")
    except Exception as e:
        print(f"Trading scanner error: {e}")
        trading_results = {"scan_time": scan_time, "market_status": "unknown", "alerts": [], "error": str(e)}
    
    # Combine results
    combined = {
        "last_scan": scan_time,
        "jobs": job_results,
        "trading": trading_results,
        "summary": {
            "new_jobs": len(job_results.get("new_opportunities", [])),
            "trading_alerts": len(trading_results.get("alerts", [])),
            "market_status": trading_results.get("market_status", "unknown")
        }
    }
    
    # Save to state file
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(combined, f, indent=2)
        print(f"\n✅ Results saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"\n❌ Error saving results: {e}")
    
    # Auto-sync dashboard
    print("\n🔄 Syncing dashboard...")
    try:
        sync_script = "/root/council-command-center/council/scripts/sync_dashboard.py"
        subprocess.run(["python3", sync_script], check=True)
        print("✅ Dashboard synced")
    except Exception as e:
        print(f"❌ Dashboard sync failed: {e}")
    
    # After syncing dashboard, run research on new opportunities
    research_status = None
    if job_results.get("new_opportunities") or trading_results.get("alerts"):
        print("\n📊 Running research analysis...")
        try:
            research_script = "/root/council-command-center/research/run_research.py"
            result = subprocess.run(["python3", research_script], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print("✅ Research complete")
                print(result.stdout)
                research_status = "complete"
            else:
                print(f"❌ Research failed: {result.stderr}")
                research_status = "failed"
        except Exception as e:
            print(f"❌ Research error: {e}")
            research_status = "error"
    
    # Auto-deploy to Vercel if we have alerts
    deployed = False
    if job_results.get("new_opportunities") or trading_results.get("alerts"):
        print("\n🚀 Deploying dashboard to Vercel...")
        try:
            subprocess.run([
                "npx", "vercel", "--prod", "--yes",
                "--token", "yKnY7BLXwJ19Wvl8Z54TjWXl"
            ], cwd="/root/council-command-center/dashboard", check=True)
            print("✅ Dashboard deployed!")
            deployed = True
        except Exception as e:
            print(f"❌ Vercel deploy failed: {e}")
    
    # Add deployment and research status to summary
    combined["summary"]["deployed"] = deployed
    combined["summary"]["research"] = research_status
    
    # Print summary
    print("\n" + "=" * 50)
    print("SCAN SUMMARY")
    print("=" * 50)
    print(f"Time: {scan_time}")
    print(f"Market: {combined['summary']['market_status']}")
    print(f"New Jobs: {combined['summary']['new_jobs']}")
    print(f"Trading Alerts: {combined['summary']['trading_alerts']}")
    if research_status:
        print(f"Research: {'✅ Complete' if research_status == 'complete' else '❌ Failed'}")
    print(f"Deployed: {'✅ Yes' if deployed else '⏭️ No (no new alerts)'}")
    
    if trading_results.get("alerts"):
        print("\n⚡ TRADING ALERTS:")
        for alert in trading_results["alerts"]:
            print(f"  {alert['symbol']}: {alert['signal']} ({alert['change_pct']:+.1f}%) - {alert['note']}")
    
    if job_results.get("new_opportunities"):
        print("\n💼 NEW JOBS:")
        for job in job_results["new_opportunities"][:5]:  # Show first 5
            print(f"  [{job['source']}] {job['title'][:50]}...")
    
    return combined


def main():
    """Entry point"""
    try:
        result = run_all_scans()
        # Exit with error code if there were errors
        if result["jobs"].get("error") or result["trading"].get("error"):
            sys.exit(1)
        return result
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
