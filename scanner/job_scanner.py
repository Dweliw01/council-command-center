#!/usr/bin/env python3
"""
Job Scanner - Finds freelance opportunities using Exa API
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Configuration
EXA_API_KEY = "751fc9de-338a-4f56-b6c7-3517adf49936"
EXA_ENDPOINT = "https://api.exa.ai/search"
STATE_FILE = Path(__file__).parent / "state" / "seen_jobs.json"

# Search queries to run
SEARCH_QUERIES = [
    ("site:upwork.com make.com automation", ["make.com", "automation"]),
    ("site:upwork.com n8n automation specialist", ["n8n", "automation"]),
    ("site:upwork.com AI integration workflow", ["AI", "integration", "workflow"]),
    ("site:freelancer.com make.com", ["make.com", "freelancer"]),
]


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
    else:
        return "other"


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
    """Main scanning function"""
    scan_time = datetime.utcnow().isoformat() + "Z"
    seen_jobs = load_seen_jobs()
    new_opportunities = []
    
    for query, keywords in SEARCH_QUERIES:
        print(f"Searching: {query}")
        results = search_exa(query)
        
        for result in results:
            url = result.get("url", "")
            title = result.get("title", "Untitled")
            published = result.get("publishedDate", "")
            
            # Skip if not recent
            if not is_recent(published):
                continue
            
            # Generate unique ID
            job_id = generate_job_id(url)
            
            # Skip if already seen
            if job_id in seen_jobs:
                continue
            
            # Add to new opportunities
            opportunity = {
                "id": job_id,
                "title": title,
                "url": url,
                "source": extract_source(url),
                "keywords_matched": keywords,
                "discovered_at": scan_time
            }
            new_opportunities.append(opportunity)
            seen_jobs.add(job_id)
    
    # Save updated seen jobs
    save_seen_jobs(seen_jobs)
    
    # Deduplicate by ID (in case same job matched multiple queries)
    unique_opps = {opp["id"]: opp for opp in new_opportunities}
    
    return {
        "scan_time": scan_time,
        "new_opportunities": list(unique_opps.values())
    }


def main():
    """Entry point"""
    result = scan_jobs()
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
