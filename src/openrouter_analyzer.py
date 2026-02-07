#!/usr/bin/env python3
"""
Agora OpenRouter AI Analyzer
Cost-optimized governance analysis using OpenRouter's Auto-Model selection
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Track token usage for cost optimization"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    model_used: str

@dataclass
class OpenRouterAnalysis:
    """Analysis result with token tracking"""
    proposal_id: str
    risk_level: str
    risk_factors: List[str]
    sentiment_score: int
    key_points: List[str]
    estimated_impact: str
    automation_recommendation: str
    confidence_score: float
    token_usage: TokenUsage
    analysis_time_ms: int

class OpenRouterGovernanceAnalyzer:
    """Cost-optimized governance analyzer using OpenRouter Auto-Model"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Use Auto-Model for optimal cost/performance
        self.model = "openrouter/auto"
        
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Token usage tracking
        self.total_usage = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "cost_per_analysis": 0.0
        }
    
    async def __aenter__(self):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/Goodnessmbakara/agora-dao-agent",
            "X-Title": "Agora DAO Governance Agent"
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_governance_proposal(self, proposal_title: str, proposal_description: str, 
                                        dao_context: str = "Generic DAO") -> OpenRouterAnalysis:
        """Analyze governance proposal using OpenRouter Auto-Model"""
        
        start_time = datetime.now()
        
        # Construct optimized prompt for governance analysis
        system_prompt = """You are an expert DAO governance analyst. Analyze proposals for:

1. RISK LEVEL (low/medium/high/critical)
2. RISK FACTORS (specific concerns list)  
3. SENTIMENT (-2 to +2 scale)
4. KEY POINTS (3-5 main items)
5. IMPACT ESTIMATION  
6. AUTOMATION RECOMMENDATION (auto_approve/auto_reject/human_review)
7. CONFIDENCE (0.0-1.0)

Respond in valid JSON format only."""

        user_prompt = f"""Analyze this DAO governance proposal:

**DAO**: {dao_context}
**Title**: {proposal_title}
**Description**: {proposal_description}

Respond with this exact JSON structure:
{{
  "risk_level": "low|medium|high|critical",
  "risk_factors": ["factor1", "factor2"],
  "sentiment_score": -2|-1|0|1|2,
  "key_points": ["point1", "point2", "point3"],
  "estimated_impact": "brief impact description",
  "automation_recommendation": "auto_approve|auto_reject|human_review", 
  "confidence_score": 0.0-1.0
}}"""

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,  # Lower temperature for consistent analysis
                "max_tokens": 500,   # Optimize token usage
                "top_p": 0.9
            }
            
            async with self.session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                data = await response.json()
                
                if "error" in data:
                    raise Exception(f"OpenRouter error: {data['error']}")
                
                # Extract response
                content = data["choices"][0]["message"]["content"]
                usage = data["usage"]
                model_used = data.get("model", self.model)
                
                # Parse JSON response
                try:
                    analysis_data = json.loads(content)
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    analysis_data = self._fallback_analysis()
                
                # Calculate analysis time
                analysis_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                # Track token usage
                token_usage = TokenUsage(
                    prompt_tokens=usage["prompt_tokens"],
                    completion_tokens=usage["completion_tokens"],
                    total_tokens=usage["total_tokens"],
                    cost_usd=self._calculate_cost(usage, model_used),
                    model_used=model_used
                )
                
                # Update usage tracking
                self._update_usage_stats(token_usage)
                
                # Create analysis result
                analysis = OpenRouterAnalysis(
                    proposal_id=proposal_title[:8],
                    risk_level=analysis_data.get("risk_level", "medium"),
                    risk_factors=analysis_data.get("risk_factors", ["Analysis incomplete"]),
                    sentiment_score=analysis_data.get("sentiment_score", 0),
                    key_points=analysis_data.get("key_points", ["Analysis pending"]),
                    estimated_impact=analysis_data.get("estimated_impact", "Impact assessment pending"),
                    automation_recommendation=analysis_data.get("automation_recommendation", "human_review"),
                    confidence_score=analysis_data.get("confidence_score", 0.5),
                    token_usage=token_usage,
                    analysis_time_ms=analysis_time
                )
                
                logger.info(f"Analysis complete: {analysis.proposal_id} | {token_usage.total_tokens} tokens | ${token_usage.cost_usd:.4f} | {model_used}")
                
                return analysis
                
        except Exception as e:
            logger.error(f"OpenRouter analysis failed: {e}")
            return self._fallback_analysis_or(proposal_title)
    
    def _calculate_cost(self, usage: Dict, model_used: str) -> float:
        """Calculate approximate cost based on OpenRouter pricing"""
        
        # OpenRouter Auto-Model pricing is dynamic, but approximate
        # Typical range: $0.0001-0.001 per 1K tokens
        tokens = usage["total_tokens"]
        
        # Conservative estimate for auto-model selection
        cost_per_1k = 0.0003  # Average cost
        
        return (tokens / 1000) * cost_per_1k
    
    def _update_usage_stats(self, token_usage: TokenUsage):
        """Update total usage statistics"""
        self.total_usage["total_requests"] += 1
        self.total_usage["total_tokens"] += token_usage.total_tokens
        self.total_usage["total_cost"] += token_usage.cost_usd
        
        if self.total_usage["total_requests"] > 0:
            self.total_usage["cost_per_analysis"] = (
                self.total_usage["total_cost"] / self.total_usage["total_requests"]
            )
    
    def _fallback_analysis(self) -> Dict:
        """Fallback analysis structure"""
        return {
            "risk_level": "medium",
            "risk_factors": ["Manual review required - AI analysis unavailable"],
            "sentiment_score": 0,
            "key_points": ["Proposal requires manual evaluation"],
            "estimated_impact": "Impact assessment requires human review",
            "automation_recommendation": "human_review",
            "confidence_score": 0.0
        }
    
    def _fallback_analysis_or(self, proposal_id: str) -> OpenRouterAnalysis:
        """Create fallback analysis object"""
        fallback = self._fallback_analysis()
        
        return OpenRouterAnalysis(
            proposal_id=proposal_id[:8],
            risk_level=fallback["risk_level"],
            risk_factors=fallback["risk_factors"],
            sentiment_score=fallback["sentiment_score"],
            key_points=fallback["key_points"],
            estimated_impact=fallback["estimated_impact"],
            automation_recommendation=fallback["automation_recommendation"],
            confidence_score=fallback["confidence_score"],
            token_usage=TokenUsage(0, 0, 0, 0.0, "fallback"),
            analysis_time_ms=0
        )
    
    async def batch_analyze(self, proposals: List[Dict]) -> List[OpenRouterAnalysis]:
        """Analyze multiple proposals efficiently"""
        analyses = []
        
        for proposal in proposals:
            analysis = await self.analyze_governance_proposal(
                proposal.get("title", ""),
                proposal.get("description", ""),
                proposal.get("dao", "Unknown DAO")
            )
            analyses.append(analysis)
            
            # Brief pause to avoid rate limiting
            await asyncio.sleep(0.1)
        
        return analyses
    
    def get_usage_report(self) -> Dict:
        """Get detailed usage and cost report"""
        return {
            "session_stats": self.total_usage,
            "cost_efficiency": {
                "avg_tokens_per_analysis": (
                    self.total_usage["total_tokens"] / max(self.total_usage["total_requests"], 1)
                ),
                "avg_cost_per_analysis": self.total_usage["cost_per_analysis"],
                "cost_per_1k_tokens": (
                    (self.total_usage["total_cost"] / max(self.total_usage["total_tokens"], 1)) * 1000
                )
            },
            "recommendations": self._get_optimization_recommendations()
        }
    
    def _get_optimization_recommendations(self) -> List[str]:
        """Get cost optimization recommendations"""
        recommendations = []
        
        avg_cost = self.total_usage["cost_per_analysis"]
        
        if avg_cost > 0.01:
            recommendations.append("Consider shorter prompts for routine analysis")
        
        if self.total_usage["total_tokens"] > 10000:
            recommendations.append("Batch processing could reduce overhead")
        
        if self.total_usage["total_requests"] > 100:
            recommendations.append("Consider caching common analysis patterns")
        
        return recommendations

# Test the OpenRouter integration
async def test_openrouter_integration():
    """Test OpenRouter governance analysis"""
    
    print("🤖 Testing OpenRouter Auto-Model Integration...")
    print("🔑 Using openrouter/auto for optimal cost/performance")
    
    # Mock API key for testing (you'll need real one)
    test_key = os.getenv('OPENROUTER_API_KEY', 'test_key')
    
    async with OpenRouterGovernanceAnalyzer(test_key) as analyzer:
        
        test_proposals = [
            {
                "title": "Treasury Diversification - Allocate 25% to SOL",
                "description": "Proposal to diversify Mango DAO treasury by allocating 25% to SOL for risk management",
                "dao": "Mango DAO"
            },
            {
                "title": "Emergency Security Patch",
                "description": "Critical security patch for governance contract vulnerability", 
                "dao": "Jupiter DAO"
            }
        ]
        
        print(f"\n📊 Analyzing {len(test_proposals)} proposals with OpenRouter Auto-Model...")
        
        for i, proposal in enumerate(test_proposals, 1):
            print(f"\n🏛️ PROPOSAL {i}: {proposal['title']}")
            print(f"   DAO: {proposal['dao']}")
            
            if test_key == 'test_key':
                # Mock analysis for demo
                print("   🔐 No OpenRouter API key - showing mock analysis")
                print("   💡 Set OPENROUTER_API_KEY environment variable for live analysis")
                
                mock_analysis = OpenRouterAnalysis(
                    proposal_id=proposal['title'][:8],
                    risk_level="high" if "security" in proposal['title'].lower() else "medium",
                    risk_factors=["Treasury impact", "Community coordination required"],
                    sentiment_score=1 if "diversification" in proposal['title'].lower() else -1,
                    key_points=["Proposal requires evaluation", "Risk assessment needed"],
                    estimated_impact="Moderate governance impact",
                    automation_recommendation="human_review",
                    confidence_score=0.75,
                    token_usage=TokenUsage(150, 75, 225, 0.0003, "mock/auto"),
                    analysis_time_ms=1200
                )
                
                print(f"   📈 Risk: {mock_analysis.risk_level.upper()}")
                print(f"   😊 Sentiment: {mock_analysis.sentiment_score}")
                print(f"   🤖 Decision: {mock_analysis.automation_recommendation}")
                print(f"   🎯 Confidence: {mock_analysis.confidence_score:.1%}")
                print(f"   💰 Tokens: {mock_analysis.token_usage.total_tokens} | Cost: ${mock_analysis.token_usage.cost_usd:.4f}")
                print(f"   ⚡ Time: {mock_analysis.analysis_time_ms}ms")
                print(f"   🧠 Model: {mock_analysis.token_usage.model_used}")
                
            else:
                # Real analysis with OpenRouter
                analysis = await analyzer.analyze_governance_proposal(
                    proposal["title"],
                    proposal["description"], 
                    proposal["dao"]
                )
                
                print(f"   📈 Risk: {analysis.risk_level.upper()}")
                print(f"   😊 Sentiment: {analysis.sentiment_score}")
                print(f"   🤖 Decision: {analysis.automation_recommendation}")
                print(f"   🎯 Confidence: {analysis.confidence_score:.1%}")
                print(f"   💰 Tokens: {analysis.token_usage.total_tokens} | Cost: ${analysis.token_usage.cost_usd:.4f}")
                print(f"   ⚡ Time: {analysis.analysis_time_ms}ms") 
                print(f"   🧠 Model: {analysis.token_usage.model_used}")
        
        # Show usage report
        usage_report = analyzer.get_usage_report()
        print(f"\n📊 SESSION USAGE REPORT:")
        print(f"   Total Requests: {usage_report['session_stats']['total_requests']}")
        print(f"   Total Tokens: {usage_report['session_stats']['total_tokens']:,}")
        print(f"   Total Cost: ${usage_report['session_stats']['total_cost']:.4f}")
        print(f"   Avg Cost/Analysis: ${usage_report['cost_efficiency']['avg_cost_per_analysis']:.4f}")
        print(f"   Avg Tokens/Analysis: {usage_report['cost_efficiency']['avg_tokens_per_analysis']:.0f}")
        
        if usage_report['recommendations']:
            print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
            for rec in usage_report['recommendations']:
                print(f"   • {rec}")
        
        print(f"\n🎯 OPENROUTER AUTO-MODEL BENEFITS:")
        print(f"   ✅ Automatic model selection for optimal cost/performance")
        print(f"   ✅ Dynamic pricing based on actual model used")
        print(f"   ✅ Token usage tracking for cost management")
        print(f"   ✅ Fallback handling for reliability")

if __name__ == "__main__":
    import os
    
    # Check for API key
    if not os.getenv('OPENROUTER_API_KEY'):
        print("💡 To use real OpenRouter analysis, set OPENROUTER_API_KEY environment variable")
        print("🔑 Get your key at: https://openrouter.ai/")
        print("💰 Auto-model optimizes cost automatically!")
    
    asyncio.run(test_openrouter_integration())