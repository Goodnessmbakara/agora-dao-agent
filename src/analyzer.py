#!/usr/bin/env python3
"""
Agora Proposal Analyzer
LLM-powered analysis of DAO proposals for content, risk, and sentiment
"""

import json
import openai
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
    """AI-powered proposal analysis engine"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        if openai_api_key:
            openai.api_key = openai_api_key
        
        self.analysis_prompt = """
You are an expert DAO governance analyst. Analyze the following proposal and provide:

1. RISK ASSESSMENT (low/medium/high/critical):
   - Financial impact
   - Protocol changes
   - Security implications
   - Community controversy

2. RISK FACTORS (list specific concerns):
   - What could go wrong?
   - Dependencies and assumptions
   - Potential negative outcomes

3. SENTIMENT ANALYSIS (-2 to +2):
   - Community reception
   - Proposal tone and clarity
   - Likely supporter/opposition dynamics

4. KEY POINTS (3-5 bullet points):
   - Main proposal objectives
   - Critical implementation details
   - Success metrics

5. IMPACT ESTIMATION:
   - Expected outcomes if passed
   - Timeline and implementation complexity

6. AUTOMATION RECOMMENDATION:
   - Should this be auto-voted based on predefined rules?
   - Or does it require human review?
   - Confidence level in recommendation

Respond in JSON format with the structure provided.

Proposal to analyze:
"""

    async def analyze_proposal(self, proposal_title: str, proposal_description: str, 
                             dao_context: Optional[str] = None) -> ProposalAnalysis:
        """Analyze a single proposal using LLM"""
        
        try:
            # Construct analysis prompt
            full_prompt = self.analysis_prompt + f"""
Title: {proposal_title}
Description: {proposal_description}
DAO Context: {dao_context or 'General DAO'}

Provide analysis in this JSON structure:
{{
    "risk_level": "low|medium|high|critical",
    "risk_factors": ["factor1", "factor2", ...],
    "sentiment_score": -2|-1|0|1|2,
    "key_points": ["point1", "point2", ...],
    "estimated_impact": "description of expected impact",
    "automation_recommendation": "auto_approve|auto_reject|human_review|abstain",
    "confidence_score": 0.0-1.0
}}
"""
            
            # For demo purposes, return mock analysis
            # In production, this would call the LLM API
            mock_analysis = self._generate_mock_analysis(proposal_title, proposal_description)
            
            return mock_analysis
            
        except Exception as e:
            logger.error(f"Analysis failed for proposal {proposal_title}: {e}")
            return self._fallback_analysis(proposal_title)
    
    def _generate_mock_analysis(self, title: str, description: str) -> ProposalAnalysis:
        """Generate mock analysis for demonstration"""
        
        # Simple heuristics for demo
        risk_level = RiskLevel.MEDIUM
        if "treasury" in description.lower() or "fund" in description.lower():
            risk_level = RiskLevel.HIGH
        elif "parameter" in description.lower() or "config" in description.lower():
            risk_level = RiskLevel.LOW
        
        sentiment = SentimentScore.NEUTRAL
        if "improve" in description.lower() or "enhance" in description.lower():
            sentiment = SentimentScore.POSITIVE
        elif "emergency" in description.lower() or "urgent" in description.lower():
            sentiment = SentimentScore.NEGATIVE
        
        # Determine automation recommendation
        automation_rec = "human_review"
        if risk_level == RiskLevel.LOW and sentiment.value >= 0:
            automation_rec = "auto_approve"
        elif risk_level == RiskLevel.CRITICAL:
            automation_rec = "human_review"
        
        return ProposalAnalysis(
            proposal_id=title[:8],
            risk_level=risk_level,
            risk_factors=[
                "Requires community consensus",
                "Implementation complexity unknown",
                "Potential for unintended consequences"
            ],
            sentiment_score=sentiment,
            key_points=[
                f"Proposal: {title}",
                "Requires careful evaluation",
                "Impact assessment needed"
            ],
            estimated_impact="Moderate impact on DAO operations",
            automation_recommendation=automation_rec,
            confidence_score=0.75
        )
    
    def _fallback_analysis(self, proposal_id: str) -> ProposalAnalysis:
        """Fallback analysis when LLM fails"""
        return ProposalAnalysis(
            proposal_id=proposal_id,
            risk_level=RiskLevel.MEDIUM,
            risk_factors=["Analysis failed - manual review required"],
            sentiment_score=SentimentScore.NEUTRAL,
            key_points=["Manual analysis needed"],
            estimated_impact="Unknown - requires human review",
            automation_recommendation="human_review",
            confidence_score=0.0
        )
    
    async def batch_analyze(self, proposals: List[Dict]) -> List[ProposalAnalysis]:
        """Analyze multiple proposals in batch"""
        analyses = []
        
        for proposal in proposals:
            analysis = await self.analyze_proposal(
                proposal.get("title", ""),
                proposal.get("description", ""),
                proposal.get("dao_name", "")
            )
            analyses.append(analysis)
        
        return analyses

# Example usage
async def main():
    analyzer = ProposalAnalyzer()
    
    sample_proposal = {
        "title": "Treasury Diversification Proposal",
        "description": "Proposal to diversify DAO treasury by allocating 20% to blue-chip tokens",
        "dao_name": "Example DAO"
    }
    
    analysis = await analyzer.analyze_proposal(
        sample_proposal["title"],
        sample_proposal["description"], 
        sample_proposal["dao_name"]
    )
    
    print("Analysis Result:")
    print(json.dumps(analysis.to_dict(), indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())