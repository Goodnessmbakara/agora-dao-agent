#!/usr/bin/env python3
"""
Agora Proposal Analyzer using Amazon Bedrock Claude
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

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

@dataclass
class ProposalAnalysis:
    """Analysis results for a proposal"""
    proposal_id: str
    risk_level: RiskLevel
    risk_factors: List[str]
    sentiment_score: SentimentScore
    key_points: List[str]
    estimated_impact: str
    automation_recommendation: str
    confidence_score: float
    
    def to_dict(self):
        return {
            "proposal_id": self.proposal_id,
            "risk_level": self.risk_level.value,
            "risk_factors": self.risk_factors,
            "sentiment_score": self.sentiment_score.value,
            "key_points": self.key_points,
            "estimated_impact": self.estimated_impact,
            "automation_recommendation": self.automation_recommendation,
            "confidence_score": self.confidence_score
        }

class ProposalAnalyzer:
    """Analyze DAO proposals using Amazon Bedrock Claude"""
    
    def __init__(self, model: str = "bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0"):
        self.model = model
        
        # Try importing LiteLLM for Bedrock support
        try:
            import litellm
            self.litellm = litellm
            
            # Set AWS region from environment
            if not os.getenv("AWS_REGION"):
                os.environ["AWS_REGION"] = "us-east-2"
            
            self.available = True
            logger.info(f"✅ Bedrock analyzer ready: {model}")
        except ImportError:
            logger.warning("⚠️ LiteLLM not available - using heuristic analysis")
            self.litellm = None
            self.available = False
    
    def analyze_proposal(self, title: str, description: str, dao_context: str = "") -> ProposalAnalysis:
        """Analyze a DAO governance proposal"""
        
        if self.available and self.litellm:
            try:
                return self._analyze_with_ai(title, description, dao_context)
            except Exception as e:
                logger.warning(f"AI analysis failed, using heuristics: {e}")
                return self._analyze_heuristic(title, description)
        else:
            return self._analyze_heuristic(title, description)
    
    def _analyze_with_ai(self, title: str, description: str, dao_context: str) -> ProposalAnalysis:
        """AI-powered analysis using Bedrock Claude"""
        
        prompt = f"""Analyze this DAO governance proposal:

Title: {title}
Description: {description}
DAO: {dao_context}

Provide analysis in this exact JSON format:
{{
  "risk_level": "low|medium|high|critical",
  "risk_factors": ["factor1", "factor2"],
  "sentiment_score": -2|-1|0|1|2,
  "key_points": ["point1", "point2", "point3"],
  "estimated_impact": "brief impact description",
  "automation_recommendation": "auto_approve|auto_reject|human_review",
  "confidence_score": 0.0-1.0
}}

Risk levels:
- low: Routine parameter changes
- medium: Significant changes
- high: Treasury movements, protocol changes
- critical: Emergency/security issues

Respond ONLY with valid JSON, no markdown or explanation."""

        response = self.litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        # Parse JSON response
        analysis_data = json.loads(content)
        
        return ProposalAnalysis(
            proposal_id=title[:50],
            risk_level=RiskLevel(analysis_data.get("risk_level", "medium")),
            risk_factors=analysis_data.get("risk_factors", []),
            sentiment_score=SentimentScore(analysis_data.get("sentiment_score", 0)),
            key_points=analysis_data.get("key_points", []),
            estimated_impact=analysis_data.get("estimated_impact", ""),
            automation_recommendation=analysis_data.get("automation_recommendation", "human_review"),
            confidence_score=float(analysis_data.get("confidence_score", 0.5))
        )
    
    def _analyze_heuristic(self, title: str, description: str) -> ProposalAnalysis:
        """Fallback heuristic analysis"""
        
        title_lower = title.lower()
        desc_lower = description.lower()
        
        # Risk assessment
        if any(word in title_lower or word in desc_lower for word in ["treasury", "fund", "million", "allocation"]):
            risk_level = RiskLevel.HIGH
            risk_factors = ["Financial impact on treasury"]
        elif any(word in title_lower or word in desc_lower for word in ["emergency", "critical", "security"]):
            risk_level = RiskLevel.CRITICAL
            risk_factors = ["Emergency security concern"]
        elif any(word in title_lower or word in desc_lower for word in ["parameter", "config", "setting"]):
            risk_level = RiskLevel.LOW
            risk_factors = ["Configuration change"]
        else:
            risk_level = RiskLevel.MEDIUM
            risk_factors = ["Standard governance review required"]
        
        # Sentiment analysis
        positive_words = ["improve", "enhance", "benefit", "growth", "optimize"]
        negative_words = ["problem", "fix", "emergency", "critical", "issue"]
        
        positive_count = sum(1 for word in positive_words if word in title_lower or word in desc_lower)
        negative_count = sum(1 for word in negative_words if word in title_lower or word in desc_lower)
        
        if positive_count > negative_count:
            sentiment = SentimentScore.POSITIVE
        elif negative_count > positive_count:
            sentiment = SentimentScore.NEGATIVE
        else:
            sentiment = SentimentScore.NEUTRAL
        
        # Automation recommendation
        if risk_level == RiskLevel.LOW and sentiment.value >= 0:
            automation_rec = "auto_approve"
        elif risk_level == RiskLevel.CRITICAL:
            automation_rec = "human_review"
        else:
            automation_rec = "human_review"
        
        return ProposalAnalysis(
            proposal_id=title[:50],
            risk_level=risk_level,
            risk_factors=risk_factors,
            sentiment_score=sentiment,
            key_points=[f"Heuristic analysis: {risk_level.value} risk detected"],
            estimated_impact="Requires detailed review",
            automation_recommendation=automation_rec,
            confidence_score=0.65
        )

# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = ProposalAnalyzer()
    
    test_proposal = {
        "title": "Treasury Diversification - Allocate 25% to SOL",
        "description": "Proposal to diversify DAO treasury by allocating 25% of funds to SOL for better risk management and exposure to Solana ecosystem growth"
    }
    
    print("🧪 Testing Bedrock Claude analysis...")
    result = analyzer.analyze_proposal(
        test_proposal["title"],
        test_proposal["description"],
        "Mango DAO"
    )
    
    print("\n📊 Analysis Result:")
    print(json.dumps(result.to_dict(), indent=2))
