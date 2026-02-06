# Scanner System

Automated scanners for job opportunities and trading momentum plays.

## Components

### 1. Job Scanner (`job_scanner.py`)
Searches for freelance opportunities using the Exa API.

**Features:**
- Searches Upwork and Freelancer for automation/AI jobs
- Filters by recency (last 48 hours)
- Deduplicates against previously seen jobs
- Stores state in `state/seen_jobs.json`

**Keywords searched:**
- make.com automation
- n8n automation specialist
- AI integration workflow

### 2. Trading Scanner (`trading_scanner.py`)
Monitors watchlist stocks for momentum signals using yfinance.

**Watchlist:** NVDA, GOOG, AMD, PLTR, META, SMCI

**Signals:**
- `GAP_UP` - Gap > 3% from previous close
- `GAP_DOWN` - Gap < -3% from previous close
- `HIGH_VOLUME` - Volume > 2x average

**Market Status Detection:**
- Pre-market (4:00-9:30 ET)
- Open (9:30-16:00 ET)
- After-hours (16:00-20:00 ET)
- Closed (weekends, overnight)

### 3. Scanner Runner (`run_scan.py`)
Orchestrates both scanners and saves combined results.

**Output:** `/council/state/opportunities.json`

## Installation

```bash
cd scanner
pip install -r requirements.txt
```

## Usage

### Run Individual Scanners
```bash
# Job scanner only
python job_scanner.py

# Trading scanner only
python trading_scanner.py
```

### Run All Scanners
```bash
python run_scan.py
```

### Cron Setup
Add to crontab for automated scanning:

```bash
# Run every 30 minutes during market hours (Mon-Fri, 9am-4pm ET)
*/30 9-16 * * 1-5 cd /root/council-command-center/scanner && python run_scan.py >> /var/log/scanner.log 2>&1

# Run job scanner 3x daily
0 8,14,20 * * * cd /root/council-command-center/scanner && python job_scanner.py >> /var/log/job_scanner.log 2>&1
```

## Output Format

### Job Scanner
```json
{
  "scan_time": "2024-01-15T10:30:00Z",
  "new_opportunities": [
    {
      "id": "abc123def456",
      "title": "Make.com Automation Expert Needed",
      "url": "https://upwork.com/...",
      "source": "upwork",
      "keywords_matched": ["make.com", "automation"],
      "discovered_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Trading Scanner
```json
{
  "scan_time": "2024-01-15T10:30:00Z",
  "market_status": "open",
  "alerts": [
    {
      "symbol": "NVDA",
      "price": 183.50,
      "change_pct": 4.2,
      "volume_ratio": 2.5,
      "signal": "GAP_UP",
      "note": "Gap up 4.2%; Volume 2.5x average"
    }
  ]
}
```

## State Files

- `state/seen_jobs.json` - Tracks seen job IDs to avoid duplicates
- `/council/state/opportunities.json` - Combined scan output

## Environment

No environment variables required. API keys are embedded (update in source if needed).
