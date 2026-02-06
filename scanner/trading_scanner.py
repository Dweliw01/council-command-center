#!/usr/bin/env python3
"""
Trading Scanner - Detects momentum plays using yfinance
"""

import json
from datetime import datetime
import yfinance as yf
import pytz

# Configuration
WATCHLIST = ["NVDA", "GOOG", "AMD", "PLTR", "META", "SMCI"]
GAP_THRESHOLD = 3.0  # Percent
VOLUME_THRESHOLD = 2.0  # Multiplier vs average


def get_market_status() -> str:
    """Determine current market status"""
    ny_tz = pytz.timezone("America/New_York")
    now = datetime.now(ny_tz)
    
    # Weekend check
    if now.weekday() >= 5:
        return "closed"
    
    hour = now.hour
    minute = now.minute
    time_decimal = hour + minute / 60
    
    if time_decimal < 4:
        return "closed"
    elif time_decimal < 9.5:
        return "pre-market"
    elif time_decimal < 16:
        return "open"
    elif time_decimal < 20:
        return "after-hours"
    else:
        return "closed"


def analyze_stock(symbol: str) -> dict | None:
    """Analyze a single stock for momentum signals"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get recent price data
        hist = ticker.history(period="5d")
        if len(hist) < 2:
            return None
        
        # Current price (most recent close or live)
        current_price = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2]
        
        # Calculate gap percentage
        gap_pct = ((current_price - prev_close) / prev_close) * 100
        
        # Calculate volume ratio
        current_volume = hist["Volume"].iloc[-1]
        avg_volume = hist["Volume"].mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Determine if this is an alert-worthy situation
        signals = []
        notes = []
        
        if gap_pct >= GAP_THRESHOLD:
            signals.append("GAP_UP")
            notes.append(f"Gap up {gap_pct:.1f}%")
        elif gap_pct <= -GAP_THRESHOLD:
            signals.append("GAP_DOWN")
            notes.append(f"Gap down {gap_pct:.1f}%")
        
        if volume_ratio >= VOLUME_THRESHOLD:
            signals.append("HIGH_VOLUME")
            notes.append(f"Volume {volume_ratio:.1f}x average")
        
        # Only return if there's a signal
        if not signals:
            return None
        
        return {
            "symbol": symbol,
            "price": round(current_price, 2),
            "change_pct": round(gap_pct, 2),
            "volume_ratio": round(volume_ratio, 2),
            "signal": signals[0],  # Primary signal
            "all_signals": signals,
            "note": "; ".join(notes)
        }
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None


def scan_trading() -> dict:
    """Main trading scan function"""
    scan_time = datetime.utcnow().isoformat() + "Z"
    market_status = get_market_status()
    alerts = []
    
    print(f"Market status: {market_status}")
    print(f"Scanning {len(WATCHLIST)} stocks...")
    
    for symbol in WATCHLIST:
        print(f"  Analyzing {symbol}...")
        result = analyze_stock(symbol)
        if result:
            alerts.append(result)
            print(f"    ⚡ ALERT: {result['signal']} - {result['note']}")
    
    return {
        "scan_time": scan_time,
        "market_status": market_status,
        "alerts": alerts
    }


def main():
    """Entry point"""
    result = scan_trading()
    print("\n" + json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
