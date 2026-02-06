#!/usr/bin/env python3
"""
Trade Analyzer - Analyzes trading alerts and generates thesis.

Uses yfinance to fetch price history, volume, and calculates
support/resistance levels for trade recommendations.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def analyze_trade(alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a trading alert and generate investment thesis.
    
    Args:
        alert: Trading alert dict with symbol, price, change_pct, signal
        
    Returns:
        Analysis dict with thesis, recommendation, confidence
    """
    symbol = alert.get("symbol", "")
    current_price = alert.get("price", 0)
    change_pct = alert.get("change_pct", 0)
    signal = alert.get("signal", "")
    volume_ratio = alert.get("volume_ratio", 1.0)
    
    # Fetch recent data from yfinance
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        
        if hist.empty:
            return _create_error_analysis(symbol, "No price data available")
        
        # Calculate key metrics
        prices = hist['Close'].values
        volumes = hist['Volume'].values
        highs = hist['High'].values
        lows = hist['Low'].values
        
        # Support/Resistance from recent highs/lows
        recent_high = float(max(highs))
        recent_low = float(min(lows))
        avg_volume = float(volumes.mean()) if len(volumes) > 0 else 0
        
        # Calculate entry, stop loss, and target
        entry, stop_loss, target = _calculate_levels(
            current_price, recent_high, recent_low, change_pct, signal
        )
        
        # Risk/Reward calculation
        risk = entry - stop_loss
        reward = target - entry
        rr_ratio = f"{reward/risk:.1f}:1" if risk > 0 else "N/A"
        
        # Generate thesis
        bull_case, bear_case = _generate_thesis(
            symbol, current_price, change_pct, signal, 
            recent_high, recent_low, volume_ratio
        )
        
        # Determine recommendation
        recommendation, confidence = _determine_recommendation(
            change_pct, volume_ratio, risk, reward, signal
        )
        
        return {
            "symbol": symbol,
            "thesis": {
                "bull_case": bull_case,
                "bear_case": bear_case,
                "risk_reward": rr_ratio,
                "entry": round(entry, 2),
                "stop_loss": round(stop_loss, 2),
                "target": round(target, 2),
                "support": round(recent_low, 2),
                "resistance": round(recent_high, 2)
            },
            "recommendation": recommendation,
            "confidence": confidence,
            "stage": "ready" if confidence in ["high", "medium"] else "researching",
            "analyzed_at": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        return _create_error_analysis(symbol, str(e))


def _calculate_levels(price: float, high: float, low: float, 
                      change_pct: float, signal: str) -> tuple:
    """Calculate entry, stop loss, and target levels."""
    
    # For gap ups, look for pullback entry
    if signal == "GAP_UP":
        # Entry on a pullback (2-3% below current)
        entry = price * 0.98
        # Stop below recent support or 5% below entry
        stop_loss = max(low * 0.98, entry * 0.95)
        # Target: next resistance or 2x the risk
        risk = entry - stop_loss
        target = price * 1.05  # 5% above current as minimum
        if (target - entry) < (2 * risk):
            target = entry + (2 * risk)
    
    elif signal == "VOLUME_SPIKE":
        entry = price * 0.99
        stop_loss = low * 0.98
        target = high * 1.02
    
    elif signal == "BREAKOUT":
        entry = price  # Chase the breakout
        stop_loss = high * 0.97  # Below breakout level
        target = price * 1.10  # 10% target
    
    else:
        # Default levels
        entry = price * 0.99
        stop_loss = low * 0.98
        target = high * 1.03
    
    return entry, stop_loss, target


def _generate_thesis(symbol: str, price: float, change_pct: float,
                     signal: str, high: float, low: float, 
                     volume_ratio: float) -> tuple:
    """Generate bull and bear case narratives."""
    
    bull_points = []
    bear_points = []
    
    # Momentum analysis
    if change_pct > 5:
        bull_points.append(f"Strong momentum with {change_pct:.1f}% move")
        bear_points.append("Extended move may need consolidation")
    elif change_pct > 2:
        bull_points.append(f"Healthy momentum at {change_pct:.1f}%")
    
    # Volume analysis
    if volume_ratio > 1.5:
        bull_points.append(f"High conviction with {volume_ratio:.1f}x average volume")
    elif volume_ratio < 0.8:
        bear_points.append(f"Low volume ({volume_ratio:.1f}x avg) suggests weak conviction")
    
    # Signal-specific analysis
    if signal == "GAP_UP":
        bull_points.append("Gap up signals strong buyer interest")
        bear_points.append("Gaps often partially fill - wait for pullback")
    elif signal == "BREAKOUT":
        bull_points.append("Breakout above resistance is bullish")
        bear_points.append("False breakouts common - watch for confirmation")
    
    # Price level analysis
    range_pct = ((high - low) / low) * 100
    if price > high * 0.98:
        bull_points.append("Trading near highs shows strength")
        bear_points.append("Near resistance - may face selling pressure")
    
    bull_case = ". ".join(bull_points) if bull_points else "Neutral setup"
    bear_case = ". ".join(bear_points) if bear_points else "Limited downside risks identified"
    
    return bull_case, bear_case


def _determine_recommendation(change_pct: float, volume_ratio: float,
                              risk: float, reward: float, 
                              signal: str) -> tuple:
    """Determine trade recommendation and confidence level."""
    
    # Calculate score
    score = 0
    
    # Reward/Risk ratio
    if risk > 0:
        rr = reward / risk
        if rr >= 3:
            score += 3
        elif rr >= 2:
            score += 2
        elif rr >= 1.5:
            score += 1
    
    # Volume confirmation
    if volume_ratio >= 1.5:
        score += 2
    elif volume_ratio >= 1.0:
        score += 1
    elif volume_ratio < 0.7:
        score -= 1
    
    # Momentum
    if 2 <= change_pct <= 8:
        score += 2  # Sweet spot
    elif change_pct > 8:
        score += 1  # Extended but strong
    
    # Signal quality
    if signal in ["BREAKOUT", "VOLUME_SPIKE"]:
        score += 1
    
    # Determine recommendation
    if change_pct > 6:
        # Extended - wait for dip
        recommendation = "BUY_DIP" if score >= 3 else "WATCH"
    elif score >= 5:
        recommendation = "BUY_NOW"
    elif score >= 3:
        recommendation = "BUY_DIP"
    elif score >= 1:
        recommendation = "WATCH"
    else:
        recommendation = "PASS"
    
    # Confidence level
    if score >= 5:
        confidence = "high"
    elif score >= 2:
        confidence = "medium"
    else:
        confidence = "low"
    
    return recommendation, confidence


def _create_error_analysis(symbol: str, error: str) -> Dict[str, Any]:
    """Create an error analysis response."""
    return {
        "symbol": symbol,
        "thesis": {
            "bull_case": "Unable to analyze",
            "bear_case": "Unable to analyze",
            "risk_reward": "N/A",
            "entry": 0,
            "stop_loss": 0,
            "target": 0,
            "error": error
        },
        "recommendation": "PASS",
        "confidence": "low",
        "stage": "error",
        "analyzed_at": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    # Test with sample alert
    test_alert = {
        "symbol": "NVDA",
        "price": 185.41,
        "change_pct": 7.87,
        "volume_ratio": 1.11,
        "signal": "GAP_UP"
    }
    
    result = analyze_trade(test_alert)
    import json
    print(json.dumps(result, indent=2))
