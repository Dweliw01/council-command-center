#!/usr/bin/env python3
"""
Options Scanner - Find quick options plays for the Mac Mini Challenge
Focuses on: weekly options, high IV plays, momentum setups
"""

import yfinance as yf
from datetime import datetime, timedelta

# Watchlist for options scanning
WATCHLIST = ["NVDA", "AMD", "TSLA", "META", "AAPL", "SPY", "QQQ", "SMCI", "PLTR"]

def scan_options():
    """
    Scan for options opportunities:
    1. Stocks with >5% move today (momentum)
    2. High implied volatility (premium selling)
    3. Near support/resistance (bounce plays)
    4. Upcoming earnings (IV crush plays)
    
    Returns list of options alerts
    """
    alerts = []
    
    for symbol in WATCHLIST:
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current data
            hist = ticker.history(period="5d")
            if hist.empty:
                continue
                
            current = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current
            change_pct = ((current - prev_close) / prev_close) * 100
            
            # Get options chain for nearest expiry
            try:
                expirations = ticker.options
                if not expirations:
                    continue
                nearest_exp = expirations[0]  # Nearest weekly/monthly
                
                chain = ticker.option_chain(nearest_exp)
                calls = chain.calls
                puts = chain.puts
                
                # Find ATM options
                atm_strike = round(current / 5) * 5  # Round to nearest $5
                
                # Look for high IV opportunities
                atm_calls = calls[calls['strike'] == atm_strike]
                atm_puts = puts[puts['strike'] == atm_strike]
                
                if not atm_calls.empty:
                    iv = atm_calls['impliedVolatility'].iloc[0]
                    premium = atm_calls['lastPrice'].iloc[0]
                    
                    # Generate alert based on conditions
                    if abs(change_pct) > 5:
                        # Big move - look for continuation or fade
                        direction = "CALLS" if change_pct > 0 else "PUTS"
                        alerts.append({
                            "symbol": symbol,
                            "type": "momentum",
                            "direction": direction,
                            "strike": atm_strike,
                            "expiry": nearest_exp,
                            "premium": premium,
                            "iv": iv,
                            "underlying_price": current,
                            "change_pct": change_pct,
                            "signal": f"Big move {change_pct:+.1f}% - {direction} play",
                            "risk": "HIGH" if abs(change_pct) > 8 else "MEDIUM"
                        })
                        
            except Exception as e:
                pass  # No options available
                
        except Exception as e:
            continue
    
    return alerts

def format_options_alert(alert):
    """Format an options alert for display"""
    return {
        "symbol": alert["symbol"],
        "play": f"{alert['direction']} ${alert['strike']} {alert['expiry']}",
        "premium": f"${alert['premium']:.2f}",
        "iv": f"{alert['iv']*100:.1f}%",
        "signal": alert["signal"],
        "risk": alert["risk"],
        "type": "options"
    }

if __name__ == "__main__":
    print("🎰 Options Scanner")
    print("=" * 50)
    
    alerts = scan_options()
    
    if alerts:
        print(f"\nFound {len(alerts)} options plays:\n")
        for alert in alerts:
            formatted = format_options_alert(alert)
            print(f"  {formatted['symbol']}: {formatted['play']}")
            print(f"    Signal: {formatted['signal']}")
            print(f"    Premium: {formatted['premium']} | IV: {formatted['iv']} | Risk: {formatted['risk']}")
            print()
    else:
        print("\nNo options plays found right now.")
