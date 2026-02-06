#!/usr/bin/env python3
"""
Gig Analyzer - Analyzes job opportunities and drafts proposals.

Evaluates job listings based on skills match, estimates effort,
and generates tailored proposal drafts.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional


# Core skills profile - customize based on actual capabilities
SKILLS_PROFILE = {
    "automation": {
        "keywords": ["make.com", "zapier", "n8n", "automation", "workflow", "integromat"],
        "weight": 10,
        "rate": 75
    },
    "ai_ml": {
        "keywords": ["ai", "machine learning", "gpt", "chatgpt", "openai", "claude", "llm", "nlp"],
        "weight": 9,
        "rate": 100
    },
    "python": {
        "keywords": ["python", "django", "flask", "fastapi", "pandas", "scripting"],
        "weight": 9,
        "rate": 85
    },
    "web_dev": {
        "keywords": ["javascript", "react", "node", "nodejs", "typescript", "frontend", "backend"],
        "weight": 7,
        "rate": 70
    },
    "data": {
        "keywords": ["data", "sql", "database", "etl", "analytics", "spreadsheet", "excel"],
        "weight": 6,
        "rate": 65
    },
    "devops": {
        "keywords": ["aws", "docker", "kubernetes", "ci/cd", "devops", "cloud"],
        "weight": 6,
        "rate": 80
    },
    "bots": {
        "keywords": ["bot", "telegram", "discord", "slack", "chatbot"],
        "weight": 8,
        "rate": 75
    },
    "scraping": {
        "keywords": ["scraping", "web scraping", "selenium", "beautifulsoup", "crawler"],
        "weight": 7,
        "rate": 70
    }
}

# Proposal templates
PROPOSAL_TEMPLATES = {
    "automation": """Hi! I specialize in {platform} automation with 5+ years of experience building complex workflows.

For your project, I can help with:
{specific_points}

I've delivered similar projects including automated data pipelines, multi-step workflows, and API integrations. I pride myself on clean, maintainable automations with proper error handling.

Happy to discuss your requirements in more detail!""",

    "ai_ml": """Hi! I'm an AI/ML specialist with hands-on experience building production AI systems.

For your project, I can help with:
{specific_points}

I've worked with OpenAI, Claude, and custom models for various applications including chatbots, content generation, and data analysis pipelines.

Let's discuss how I can help you achieve your goals!""",

    "python": """Hi! I'm a Python developer with 5+ years of experience building robust applications.

For your project, I can help with:
{specific_points}

I write clean, well-documented code with proper testing. My work includes APIs, automation scripts, data processing, and web applications.

Looking forward to discussing your requirements!""",

    "default": """Hi! I'm a versatile developer with experience in automation, Python, and AI/ML.

For your project, I can help with:
{specific_points}

I focus on delivering clean, working solutions with clear communication throughout the project.

Happy to discuss your needs in more detail!"""
}


def analyze_gig(opportunity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a job opportunity and generate proposal.
    
    Args:
        opportunity: Job dict with title, description, url, source
        
    Returns:
        Analysis dict with relevance_score, proposal, recommendation
    """
    title = opportunity.get("title", "").lower()
    description = opportunity.get("description", "").lower()
    url = opportunity.get("url", "")
    source = opportunity.get("source", "unknown")
    budget = opportunity.get("budget", "")
    
    # Combine title and description for analysis
    full_text = f"{title} {description}"
    
    # Match against skills
    skill_matches = _match_skills(full_text)
    
    # Calculate relevance score (1-10)
    relevance_score = _calculate_relevance(skill_matches)
    
    # Estimate hours based on keywords
    estimated_hours = _estimate_hours(full_text, budget)
    
    # Determine best rate
    suggested_rate = _calculate_rate(skill_matches)
    
    # Assess competition
    competition_level = _assess_competition(source, relevance_score)
    
    # Generate proposal
    primary_skill = skill_matches[0][0] if skill_matches else "default"
    proposal_draft = _generate_proposal(
        opportunity.get("title", ""),
        full_text,
        primary_skill,
        skill_matches
    )
    
    # Determine recommendation
    recommendation, confidence = _determine_recommendation(
        relevance_score, competition_level, estimated_hours, suggested_rate
    )
    
    return {
        "title": opportunity.get("title", "Unknown"),
        "url": url,
        "source": source,
        "analysis": {
            "relevance_score": relevance_score,
            "estimated_hours": estimated_hours,
            "suggested_rate": suggested_rate,
            "competition_level": competition_level,
            "matched_skills": [s[0] for s in skill_matches[:3]]
        },
        "proposal_draft": proposal_draft,
        "recommendation": recommendation,
        "confidence": confidence,
        "stage": "ready" if recommendation == "APPLY" else "researching",
        "analyzed_at": datetime.utcnow().isoformat() + "Z"
    }


def _match_skills(text: str) -> List[tuple]:
    """Match text against skills and return sorted matches."""
    matches = []
    
    for skill_name, skill_data in SKILLS_PROFILE.items():
        keyword_count = sum(
            1 for kw in skill_data["keywords"] 
            if kw.lower() in text
        )
        if keyword_count > 0:
            # Score = keyword matches * skill weight
            score = keyword_count * skill_data["weight"]
            matches.append((skill_name, score, skill_data["rate"]))
    
    # Sort by score descending
    return sorted(matches, key=lambda x: x[1], reverse=True)


def _calculate_relevance(matches: List[tuple]) -> int:
    """Calculate relevance score from 1-10."""
    if not matches:
        return 1
    
    # Get top match score
    top_score = matches[0][1]
    
    # Normalize to 1-10 scale
    if top_score >= 30:
        return 10
    elif top_score >= 20:
        return 9
    elif top_score >= 15:
        return 8
    elif top_score >= 10:
        return 7
    elif top_score >= 7:
        return 6
    elif top_score >= 5:
        return 5
    elif top_score >= 3:
        return 4
    else:
        return 3


def _estimate_hours(text: str, budget: str) -> int:
    """Estimate project hours based on description."""
    hours = 10  # Default
    
    # Keywords suggesting complexity
    if any(word in text for word in ["complex", "large", "enterprise", "full"]):
        hours += 15
    if any(word in text for word in ["simple", "small", "quick", "basic"]):
        hours -= 5
    if any(word in text for word in ["ongoing", "monthly", "maintenance"]):
        hours += 20
    if any(word in text for word in ["api", "integration", "multiple"]):
        hours += 5
    
    # Try to parse budget for hints
    if budget:
        try:
            # Extract numbers from budget string
            nums = re.findall(r'\d+', str(budget).replace(',', ''))
            if nums:
                max_budget = max(int(n) for n in nums)
                # Rough estimate: $75/hour
                hours = max(hours, max_budget // 75)
        except:
            pass
    
    return max(5, min(hours, 100))  # Clamp between 5-100


def _calculate_rate(matches: List[tuple]) -> int:
    """Calculate suggested hourly rate based on skill matches."""
    if not matches:
        return 60
    
    # Average of top 2 skill rates
    rates = [m[2] for m in matches[:2]]
    return int(sum(rates) / len(rates))


def _assess_competition(source: str, relevance: int) -> str:
    """Assess competition level."""
    # Higher relevance = we're a better fit = lower effective competition
    if relevance >= 8:
        return "low"  # We're a great fit, fewer true competitors
    elif relevance >= 5:
        return "medium"
    else:
        return "high"  # Generic job, many can apply


def _generate_proposal(title: str, text: str, primary_skill: str,
                       matches: List[tuple]) -> str:
    """Generate a tailored proposal draft."""
    
    # Get appropriate template
    template = PROPOSAL_TEMPLATES.get(primary_skill, PROPOSAL_TEMPLATES["default"])
    
    # Generate specific points based on detected needs
    points = []
    
    if "automation" in text or "workflow" in text:
        points.append("• Building reliable, scalable automation workflows")
    if "api" in text or "integration" in text:
        points.append("• API integration and data synchronization")
    if "bot" in text or "chatbot" in text:
        points.append("• Interactive bot development with proper UX")
    if "data" in text or "scraping" in text:
        points.append("• Data extraction and processing pipelines")
    if "ai" in text or "gpt" in text or "llm" in text:
        points.append("• AI/LLM integration and prompt engineering")
    
    # Add generic points if needed
    if len(points) < 2:
        points.append("• Implementing your specific requirements")
        points.append("• Providing documentation and support")
    
    specific_points = "\n".join(points[:4])
    
    # Determine platform for automation jobs
    platform = "automation"
    if "make.com" in text or "integromat" in text:
        platform = "Make.com"
    elif "zapier" in text:
        platform = "Zapier"
    elif "n8n" in text:
        platform = "n8n"
    
    return template.format(
        platform=platform,
        specific_points=specific_points
    )


def _determine_recommendation(relevance: int, competition: str,
                             hours: int, rate: int) -> tuple:
    """Determine apply recommendation and confidence."""
    
    score = 0
    
    # Relevance score contribution
    if relevance >= 8:
        score += 4
    elif relevance >= 6:
        score += 2
    elif relevance >= 4:
        score += 1
    
    # Competition contribution
    if competition == "low":
        score += 2
    elif competition == "medium":
        score += 1
    
    # Effort vs reward
    potential_earnings = hours * rate
    if potential_earnings >= 1000:
        score += 2
    elif potential_earnings >= 500:
        score += 1
    
    # Sweet spot hours (not too small, not too big)
    if 10 <= hours <= 40:
        score += 1
    
    # Recommendation
    if score >= 6:
        recommendation = "APPLY"
        confidence = "high"
    elif score >= 4:
        recommendation = "APPLY"
        confidence = "medium"
    elif score >= 2:
        recommendation = "MAYBE"
        confidence = "medium"
    else:
        recommendation = "PASS"
        confidence = "low"
    
    return recommendation, confidence


if __name__ == "__main__":
    # Test with sample opportunity
    test_job = {
        "title": "Make.com Automation Specialist Needed",
        "description": "Looking for someone to build automated workflows connecting our CRM with email marketing platform. Need API integration and data sync.",
        "url": "https://upwork.com/jobs/test",
        "source": "upwork"
    }
    
    result = analyze_gig(test_job)
    import json
    print(json.dumps(result, indent=2))
