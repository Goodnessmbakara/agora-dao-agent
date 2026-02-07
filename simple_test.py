#!/usr/bin/env python3
"""
Simple test of Agora governance analysis without external dependencies
"""

import json
from datetime import datetime
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class SentimentScore(Enum):
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2

def analyze_proposal_simple(title, description):
    """Simple heuristic-based proposal analysis"""
    
    title_lower = title.lower()
    desc_lower = description.lower()
    
    # Risk assessment
    risk_level = RiskLevel.MEDIUM
    risk_factors = []
    
    if any(word in desc_lower for word in ['treasury', 'fund', 'transfer', 'spend']):
        risk_level = RiskLevel.HIGH
        risk_factors.append("Financial impact")
    
    if any(word in desc_lower for word in ['emergency', 'critical', 'urgent', 'security']):
        risk_level = RiskLevel.CRITICAL
        risk_factors.append("Time-sensitive security concern")
    
    if any(word in desc_lower for word in ['parameter', 'config', 'setting']):
        risk_level = RiskLevel.LOW
        risk_factors.append("Configuration change")
    
    # Sentiment analysis
    sentiment = SentimentScore.NEUTRAL
    
    positive_words = ['improve', 'enhance', 'upgrade', 'benefit', 'growth']
    negative_words = ['problem', 'issue', 'fix', 'emergency', 'critical']
    
    positive_count = sum(1 for word in positive_words if word in desc_lower)
    negative_count = sum(1 for word in negative_words if word in desc_lower)
    
    if positive_count > negative_count:
        sentiment = SentimentScore.POSITIVE
    elif negative_count > positive_count:
        sentiment = SentimentScore.NEGATIVE
    
    # Automation recommendation
    if risk_level == RiskLevel.LOW and sentiment.value >= 0:
        recommendation = "auto_approve"
    elif risk_level == RiskLevel.CRITICAL:
        recommendation = "human_review"
    else:
        recommendation = "human_review"
    
    return {
        "title": title,
        "risk_level": risk_level.value,
        "risk_factors": risk_factors or ["Standard governance review required"],
        "sentiment_score": sentiment.value,
        "automation_recommendation": recommendation,
        "confidence": 0.75,
        "analysis_time": datetime.now().isoformat()
    }

def test_governance_analysis():
    """Test the governance analysis system"""
    
    print("🏛️  AGORA - Autonomous DAO Governance Agent")
    print("=" * 50)
    print("🧪 Testing Proposal Analysis System\n")
    
    test_proposals = [
        {
            "title": "Treasury Diversification Proposal",
            "description": "Allocate 20% of treasury to blue-chip tokens for risk management and long-term growth"
        },
        {
            "title": "Emergency Security Fix",
            "description": "Critical security patch for governance contract vulnerability discovered in audit"
        },
        {
            "title": "Community Event Funding", 
            "description": "Fund $5,000 for community meetup and educational events to improve engagement"
        },
        {
            "title": "Governance Parameter Update",
            "description": "Update voting period from 3 days to 5 days to improve participation rates"
        },
        {
            "title": "New Feature Development",
            "description": "Proposal to develop and implement new staking rewards mechanism to enhance user experience"
        }
    ]
    
    for i, proposal in enumerate(test_proposals, 1):
        print(f"📋 PROPOSAL {i}: {proposal['title']}")
        print(f"Description: {proposal['description']}")
        print()
        
        analysis = analyze_proposal_simple(proposal["title"], proposal["description"])
        
        print("🔍 ANALYSIS RESULTS:")
        print(f"   Risk Level: {analysis['risk_level'].upper()}")
        print(f"   Risk Factors: {', '.join(analysis['risk_factors'])}")
        print(f"   Sentiment Score: {analysis['sentiment_score']} ({get_sentiment_label(analysis['sentiment_score'])})")
        print(f"   Recommendation: {analysis['automation_recommendation'].upper()}")
        print(f"   Confidence: {analysis['confidence']:.1%}")
        
        # Show decision logic
        if analysis['automation_recommendation'] == 'auto_approve':
            print("   🟢 DECISION: Auto-approve (low risk, positive sentiment)")
        elif analysis['automation_recommendation'] == 'auto_reject':
            print("   🔴 DECISION: Auto-reject (high risk or negative sentiment)")
        else:
            print("   🟡 DECISION: Human review required")
        
        print("-" * 50)
        print()

def get_sentiment_label(score):
    """Convert sentiment score to human readable label"""
    labels = {
        -2: "Very Negative",
        -1: "Negative", 
        0: "Neutral",
        1: "Positive",
        2: "Very Positive"
    }
    return labels.get(score, "Unknown")

if __name__ == "__main__":
    test_governance_analysis()