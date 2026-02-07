#!/usr/bin/env python3
"""
Agora - Autonomous DAO Governance Agent
Main entry point for the governance automation system
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List
import click

from src.monitor import GovernanceMonitor
from src.analyzer import ProposalAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgoraAgent:
    """Main Agora governance agent"""
    
    def __init__(self):
        self.monitor = None
        self.analyzer = ProposalAnalyzer()
        self.governance_rules = self.load_governance_rules()
        
    def load_governance_rules(self) -> Dict:
        """Load governance automation rules"""
        # Default rules - would be configurable per DAO
        return {
            "auto_approve": {
                "max_risk_level": "low",
                "min_sentiment": 1,
                "required_confidence": 0.8
            },
            "auto_reject": {
                "min_risk_level": "critical",
                "max_sentiment": -2
            },
            "treasury_threshold": 10000,  # USD value requiring manual review
            "quorum_monitoring": True,
            "deadline_alerts": True
        }
    
    async def process_proposal(self, proposal):
        """Process a single proposal through the automation pipeline"""
        logger.info(f"Processing proposal: {proposal.title}")
        
        # Analyze the proposal
        analysis = await self.analyzer.analyze_proposal(
            proposal.title,
            proposal.description,
            proposal.dao_name
        )
        
        # Apply governance rules
        decision = self.apply_governance_rules(analysis)
        
        # Log the decision
        self.log_decision(proposal, analysis, decision)
        
        # Execute if automated
        if decision["action"] in ["auto_approve", "auto_reject"]:
            await self.execute_vote(proposal, decision)
        
        return {
            "proposal": proposal.to_dict(),
            "analysis": analysis.to_dict(),
            "decision": decision
        }
    
    def apply_governance_rules(self, analysis) -> Dict:
        """Apply predefined governance rules to determine action"""
        rules = self.governance_rules
        
        # Check for auto-approval
        if (analysis.risk_level.value == "low" and 
            analysis.sentiment_score.value >= rules["auto_approve"]["min_sentiment"] and
            analysis.confidence_score >= rules["auto_approve"]["required_confidence"]):
            return {
                "action": "auto_approve",
                "reason": "Low risk, positive sentiment, high confidence",
                "confidence": analysis.confidence_score
            }
        
        # Check for auto-rejection  
        if (analysis.risk_level.value == "critical" or
            analysis.sentiment_score.value <= rules["auto_reject"]["max_sentiment"]):
            return {
                "action": "auto_reject", 
                "reason": "High risk or very negative sentiment",
                "confidence": analysis.confidence_score
            }
        
        # Default to human review
        return {
            "action": "human_review",
            "reason": "Requires manual evaluation",
            "confidence": analysis.confidence_score
        }
    
    async def execute_vote(self, proposal, decision):
        """Execute the voting decision on-chain"""
        logger.info(f"Executing {decision['action']} for proposal {proposal.id}")
        
        # This would integrate with Solana governance programs
        # For demo, just log the action
        print(f"🗳️  VOTE EXECUTED: {decision['action'].upper()}")
        print(f"   Proposal: {proposal.title}")
        print(f"   Reason: {decision['reason']}")
        print(f"   Confidence: {decision['confidence']:.2f}")
        print("---")
    
    def log_decision(self, proposal, analysis, decision):
        """Log decision for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "proposal_id": proposal.id,
            "dao": proposal.dao_name,
            "title": proposal.title,
            "risk_level": analysis.risk_level.value,
            "sentiment": analysis.sentiment_score.value,
            "action": decision["action"],
            "reason": decision["reason"],
            "confidence": decision["confidence"]
        }
        
        # In production, this would write to database
        logger.info(f"Decision logged: {json.dumps(log_entry, indent=2)}")
    
    async def run(self):
        """Main agent loop"""
        logger.info("🏛️  Agora DAO Governance Agent starting...")
        
        async with GovernanceMonitor() as monitor:
            self.monitor = monitor
            
            # Start monitoring loop
            while True:
                try:
                    # Check for new proposals
                    new_proposals = await monitor.check_for_new_proposals()
                    
                    # Process each proposal
                    for proposal in new_proposals:
                        await self.process_proposal(proposal)
                    
                    # Wait before next check
                    await asyncio.sleep(60)  # Check every minute
                    
                except KeyboardInterrupt:
                    logger.info("Shutting down Agora agent...")
                    break
                except Exception as e:
                    logger.error(f"Agent error: {e}")
                    await asyncio.sleep(30)

@click.command()
@click.option('--daemon', is_flag=True, help='Run as daemon')
@click.option('--test', is_flag=True, help='Run test mode')
def main(daemon, test):
    """Agora - Autonomous DAO Governance Agent"""
    
    if test:
        # Run test analysis
        asyncio.run(test_analysis())
    else:
        # Run the main agent
        agent = AgoraAgent()
        asyncio.run(agent.run())

async def test_analysis():
    """Test the analysis system"""
    print("🧪 Testing Agora Analysis System...")
    
    analyzer = ProposalAnalyzer()
    
    test_proposals = [
        {
            "title": "Treasury Diversification Proposal", 
            "description": "Allocate 20% of treasury to blue-chip tokens for risk management",
            "dao_name": "Test DAO"
        },
        {
            "title": "Emergency Security Fix",
            "description": "Critical security patch for governance contract vulnerability", 
            "dao_name": "Test DAO"
        },
        {
            "title": "Community Event Funding",
            "description": "Fund $5,000 for community meetup and educational events",
            "dao_name": "Test DAO"
        }
    ]
    
    for proposal in test_proposals:
        print(f"\n📋 Analyzing: {proposal['title']}")
        analysis = await analyzer.analyze_proposal(
            proposal["title"],
            proposal["description"],
            proposal["dao_name"]
        )
        
        print(f"   Risk Level: {analysis.risk_level.value}")
        print(f"   Sentiment: {analysis.sentiment_score.value}")
        print(f"   Recommendation: {analysis.automation_recommendation}")
        print(f"   Confidence: {analysis.confidence_score:.2f}")

if __name__ == "__main__":
    main()