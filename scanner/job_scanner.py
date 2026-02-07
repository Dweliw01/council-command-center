#!/usr/bin/env python3
"""
Job Scanner - Finds short-term freelance gig opportunities using Exa API
"""

import json
import hashlib
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Configuration
EXA_API_KEY = "751fc9de-338a-4f56-b6c7-3517adf49936"
EXA_ENDPOINT = "https://api.exa.ai/search"
STATE_FILE = Path(__file__).parent / "state" / "seen_jobs.json"

# Search queries focused on short-term/quick gigs
SEARCH_QUERIES = [
    ("site:upwork.com Make.com automation quick project", ["make.com", "automation", "quick"]),
    ("site:upwork.com n8n workflow one-time", ["n8n", "workflow", "one-time"]),
    ("site:upwork.com Zapier integration small project", ["zapier", "integration", "small"]),
    ("site:upwork.com AI chatbot setup budget", ["AI", "chatbot", "budget"]),
    ("site:fiverr.com make automation", ["make", "automation", "fiverr"]),
    ("site:freelancer.com automation quick job", ["automation", "quick", "freelancer"]),
]

# Keywords that indicate full-time/long-term positions (exclude these)
FULLTIME_INDICATORS = [
    "full-time", "full time", "fulltime",
    "permanent", "salary", "benefits", "401k",
    "long-term hire", "ongoing position", "w-2",
    "employee", "in-house", "on-site required"
]

# Keywords that indicate short-term/gig work (prioritize these)
GIG_INDICATORS = [
    "project", "one-time", "quick", "budget",
    "hourly", "fixed price", "small task",
    "short-term", "freelance", "contract",
    "asap", "urgent", "simple", "fast turnaround"
]

# Ideal budget range for quick gigs
IDEAL_BUDGET_MIN = 100
IDEAL_BUDGET_MAX = 1000


def load_seen_jobs() -> set:
    """Load previously seen job IDs"""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("seen", []))
    return set()


def save_seen_jobs(seen_ids: set):
    """Save seen job IDs to state file"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"seen": list(seen_ids)}, f, indent=2)


def generate_job_id(url: str) -> str:
    """Generate a unique ID from URL"""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def extract_source(url: str) -> str:
    """Extract source platform from URL"""
    if "upwork.com" in url:
        return "upwork"
    elif "freelancer.com" in url:
        return "freelancer"
    elif "fiverr.com" in url:
        return "fiverr"
    else:
        return "other"


def is_fulltime_job(title: str, description: str = "") -> bool:
    """Check if job contains full-time/permanent indicators"""
    text = f"{title} {description}".lower()
    for indicator in FULLTIME_INDICATORS:
        if indicator.lower() in text:
            return True
    return False


def extract_budget(text: str) -> tuple:
    """Extract budget amount from text, returns (min, max) or (None, None)"""
    # Match patterns like $500, $100-$500, $1,000
    patterns = [
        r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $100-$500
        r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $500
    ]
    
    text = text.replace(",", "")
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                return (float(groups[0]), float(groups[1]))
            elif len(groups) == 1:
                val = float(groups[0])
                return (val, val)
    return (None, None)


def analyze_job(title: str, description: str = "", url: str = "") -> dict:
    """Analyze a job posting and return scoring info for short-term gigs"""
    text = f"{title} {description}".lower()
    
    analysis = {
        "is_gig": True,
        "score": 0,
        "reasons": [],
        "budget": None,
        "duration_type": "unknown"
    }
    
    # Check for full-time indicators (disqualifying)
    if is_fulltime_job(title, description):
        analysis["is_gig"] = False
        analysis["reasons"].append("Contains full-time/permanent indicators")
        return analysis
    
    # Count gig indicators (positive signals)
    gig_matches = []
    for indicator in GIG_INDICATORS:
        if indicator.lower() in text:
            gig_matches.append(indicator)
            analysis["score"] += 10
    
    if gig_matches:
        analysis["reasons"].append(f"Gig indicators: {', '.join(gig_matches)}")
    
    # Check for budget in ideal range
    budget_min, budget_max = extract_budget(text)
    if budget_min is not None:
        analysis["budget"] = (budget_min, budget_max)
        if IDEAL_BUDGET_MIN <= budget_min <= IDEAL_BUDGET_MAX:
            analysis["score"] += 20
            analysis["reasons"].append(f"Budget in ideal range: ${budget_min}-${budget_max}")
        elif budget_min > IDEAL_BUDGET_MAX:
            analysis["score"] += 10  # Higher budget is still good
            analysis["reasons"].append(f"Higher budget: ${budget_min}-${budget_max}")
    
    # Check for duration indicators
    if any(word in text for word in ["days", "day", "hours", "hour", "week"]):
        if not any(word in text for word in ["months", "month", "year"]):
            analysis["duration_type"] = "short"
            analysis["score"] += 15
            analysis["reasons"].append("Short duration (days/weeks)")
    elif any(word in text for word in ["months", "month", "year"]):
        analysis["duration_type"] = "long"
        analysis["score"] -= 10
        analysis["reasons"].append("Long duration indicated")
    
    # Fixed price bonus
    if "fixed" in text or "fixed price" in text:
        analysis["score"] += 10
        analysis["reasons"].append("Fixed price project")
    
    # Fiverr and quick job platforms get bonus
    if "fiverr.com" in url:
        analysis["score"] += 15
        analysis["reasons"].append("Fiverr listing (typically short gigs)")
    
    return analysis


def search_exa(query: str) -> list:
    """Search Exa API for jobs"""
    headers = {
        "Authorization": f"Bearer {EXA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Search for recent results (last 48 hours)
    payload = {
        "query": query,
        "numResults": 20,
        "useAutoprompt": True,
        "type": "neural",
        "contents": {
            "text": {"maxCharacters": 500}
        }
    }
    
    try:
        response = requests.post(EXA_ENDPOINT, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"Error searching Exa: {e}")
        return []


def is_recent(published_date: str, hours: int = 48) -> bool:
    """Check if a result is recent enough"""
    if not published_date:
        return True  # Assume recent if no date
    try:
        pub_date = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
        cutoff = datetime.now(pub_date.tzinfo) - timedelta(hours=hours)
        return pub_date > cutoff
    except (ValueError, TypeError):
        return True  # Assume recent if can't parse


def scan_jobs() -> dict:
    """Main scanning function - finds short-term gigs only"""
    scan_time = datetime.utcnow().isoformat() + "Z"
    seen_jobs = load_seen_jobs()
    new_opportunities = []
    skipped_fulltime = 0
    
    for query, keywords in SEARCH_QUERIES:
        print(f"Searching: {query}")
        results = search_exa(query)
        
        for result in results:
            url = result.get("url", "")
            title = result.get("title", "Untitled")
            text = result.get("text", "")
            published = result.get("publishedDate", "")
            
            # Skip if not recent
            if not is_recent(published):
                continue
            
            # Generate unique ID
            job_id = generate_job_id(url)
            
            # Skip if already seen
            if job_id in seen_jobs:
                continue
            
            # Analyze the job for gig suitability
            analysis = analyze_job(title, text, url)
            
            # Skip full-time/permanent positions
            if not analysis["is_gig"]:
                skipped_fulltime += 1
                seen_jobs.add(job_id)  # Mark as seen so we don't re-check
                continue
            
            # Add to new opportunities
            opportunity = {
                "id": job_id,
                "title": title,
                "url": url,
                "source": extract_source(url),
                "keywords_matched": keywords,
                "discovered_at": scan_time,
                "gig_score": analysis["score"],
                "budget": analysis["budget"],
                "duration_type": analysis["duration_type"],
                "analysis_reasons": analysis["reasons"]
            }
            new_opportunities.append(opportunity)
            seen_jobs.add(job_id)
    
    # Save updated seen jobs
    save_seen_jobs(seen_jobs)
    
    # Deduplicate by ID (in case same job matched multiple queries)
    unique_opps = {opp["id"]: opp for opp in new_opportunities}
    
    # Sort by gig score (highest first)
    sorted_opps = sorted(unique_opps.values(), key=lambda x: x["gig_score"], reverse=True)
    
    return {
        "scan_time": scan_time,
        "new_opportunities": sorted_opps,
        "stats": {
            "total_found": len(sorted_opps),
            "skipped_fulltime": skipped_fulltime
        }
    }


def main():
    """Entry point"""
    result = scan_jobs()
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
