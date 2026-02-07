#!/usr/bin/env python3
"""
Dynamic proposal generator using Bedrock Claude
Generates realistic DAO governance proposals on-demand
"""

import json
import random
from datetime import datetime
from typing import List, Dict
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from analyzer import ProposalAnalyzer

class DynamicProposalGenerator:
    """Generates realistic DAO proposals using AI"""
    
    DAOS = ["Mango DAO", "Jupiter DAO", "Marinade DAO", "Pyth DAO"]
    
    PROPOSAL_PROMPTS = [
        "A treasury management proposal to diversify holdings",
        "A protocol upgrade for improved security",
        "A community grant program proposal",
        "A parameter adjustment for fee structures",
        "A partnership proposal with another protocol",
        "An emergency security patch",
        "A tokenomics adjustment proposal",
        "A governance process improvement",
    ]
    
    def __init__(self):
        self.analyzer = ProposalAnalyzer()
    
    def generate_proposal_idea(self, dao: str) -> Dict[str, str]:
        """Generate a single proposal idea"""
        prompt_template = random.choice(self.PROPOSAL_PROMPTS)
        
        prompt = f"""Generate a realistic Solana DAO governance proposal for {dao}.

Context: {prompt_template}

Return ONLY a JSON object with these fields:
{{
    "title": "Brief proposal title (max 80 chars)",
    "description": "Detailed description (2-3 sentences)",
    "dao": "{dao}"
}}

Make it realistic and specific to Solana DeFi. Be concise."""

        try:
            # Use Bedrock Claude to generate proposal
            from litellm import completion
            
            response = completion(
                model="bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,  # Higher temp for creativity
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON from response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            proposal_data = json.loads(content)
            return proposal_data
            
        except Exception as e:
            print(f"⚠️ AI generation failed, using fallback: {e}")
            # Fallback to template-based generation
            return self._fallback_proposal(dao, prompt_template)
    
    def _fallback_proposal(self, dao: str, template: str) -> Dict[str, str]:
        """Fallback proposal generator if AI fails"""
        proposals = {
            "treasury": {
                "title": f"{dao} Treasury Diversification Strategy",
                "description": "Proposal to allocate 15% of treasury into blue-chip DeFi protocols for yield generation while maintaining liquidity for operations."
            },
            "security": {
                "title": f"{dao} Security Audit and Bug Bounty Program",
                "description": "Establish comprehensive security measures including quarterly audits and a $500K bug bounty program to enhance protocol security."
            },
            "grants": {
                "title": f"{dao} Developer Grant Program Q1 2026",
                "description": "Allocate 100K USDC for developer grants focused on building integrations, tooling, and educational content for the ecosystem."
            }
        }
        
        key = list(proposals.keys())[random.randint(0, 2)]
        return {**proposals[key], "dao": dao}
    
    def generate_proposals(self, count: int = 4) -> List[Dict]:
        """Generate multiple realistic proposals with AI analysis"""
        proposals = []
        daos_cycle = self.DAOS * ((count // len(self.DAOS)) + 1)
        
        for i in range(count):
            dao = daos_cycle[i]
            
            print(f"🤖 Generating proposal {i+1}/{count} for {dao}...")
            
            try:
                # Generate proposal idea
                proposal_data = self.generate_proposal_idea(dao)
                
                # Analyze with AI
                analysis = self.analyzer.analyze_proposal(
                    title=proposal_data["title"],
                    description=proposal_data["description"],
                    dao_context=dao
                )
                
                # Build complete proposal
                proposal = {
                    "id": f"ai-gen-{datetime.now().timestamp():.0f}-{i}",
                    "title": proposal_data["title"],
                    "dao": dao,
                    "status": "Voting",
                    "riskLevel": analysis.risk_level.value,
                    "sentiment": analysis.sentiment_score.value,
                    "decision": analysis.automation_recommendation,
                    "confidence": analysis.confidence_score,
                    "yesVotes": random.randint(500, 3000),
                    "noVotes": random.randint(100, 800),
                    "processed": datetime.now().isoformat()
                }
                
                proposals.append(proposal)
                print(f"  ✅ {proposal['title'][:60]}...")
                
            except Exception as e:
                print(f"  ❌ Error generating proposal: {e}")
                continue
        
        return proposals

def test_generator():
    """Test the dynamic proposal generator"""
    print("🧪 Testing Dynamic Proposal Generator\n")
    
    generator = DynamicProposalGenerator()
    proposals = generator.generate_proposals(count=4)
    
    print(f"\n✅ Generated {len(proposals)} proposals:\n")
    for p in proposals:
        print(f"📋 {p['dao']}")
        print(f"   {p['title']}")
        print(f"   Risk: {p['riskLevel']} | Decision: {p['decision']}")
        print()

if __name__ == "__main__":
    test_generator()
