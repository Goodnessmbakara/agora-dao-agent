#!/usr/bin/env python3
"""
Agora Governance Engine
Integrates Solana monitoring with AI analysis and automated decision making
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
import logging

from .solana_client import SolanaGovernanceClient, RealmsProposal
from .analyzer import ProposalAnalyzer, ProposalAnalysis, RiskLevel

logger = logging.getLogger(__name__)

class GovernanceEngine:
    """Main governance automation engine"""
    
    def __init__(self, config: Dict = None):
        self.config = config or self.default_config()
        self.solana_client = SolanaGovernanceClient()
        self.analyzer = ProposalAnalyzer()
        self.processed_proposals: Dict[str, Dict] = {}
        
        # Callbacks for different events
        self.callbacks = {
            "new_proposal": [],
            "auto_approve": [],
            "auto_reject": [], 
            "human_review": [],
            "analysis_complete": []
        }
    
    def default_config(self) -> Dict:
        """Default governance configuration"""
        return {
            "automation": {
                "enabled": True,
                "auto_approve": {
                    "max_risk_level": "low",
                    "min_sentiment": 0,
                    "min_confidence": 0.8
                },
                "auto_reject": {
                    "min_risk_level": "critical",
                    "max_sentiment": -2
                },
                "treasury_threshold": 50000,  # USD value requiring human review
                "emergency_keywords": ["emergency", "critical", "urgent", "hack", "exploit"]
            },
            "monitoring": {
                "interval": 300,  # 5 minutes
                "max_proposals_per_scan": 50
            },
            "analysis": {
                "sentiment_weight": 0.3,
                "risk_weight": 0.7,
                "confidence_threshold": 0.6
            }
        }
    
    def add_callback(self, event_type: str, callback: Callable):
        """Add callback for governance events"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    async def emit_event(self, event_type: str, data: Dict):
        """Emit governance event to all registered callbacks"""
        for callback in self.callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Callback error for {event_type}: {e}")
    
    async def analyze_proposal(self, proposal: RealmsProposal) -> ProposalAnalysis:
        """Analyze a Realms proposal"""
        
        # Fetch full metadata if needed
        metadata = await self.solana_client.get_proposal_metadata(proposal.description_link)
        
        # Run AI analysis
        analysis = await self.analyzer.analyze_proposal(
            title=metadata.get("title", proposal.name),
            description=metadata.get("description", "No description available"),
            dao_context=proposal.realm
        )
        
        # Update analysis with Solana-specific data
        analysis.proposal_id = proposal.public_key
        
        # Apply DAO-specific adjustments
        analysis = self.apply_dao_specific_rules(proposal, analysis)
        
        return analysis
    
    def apply_dao_specific_rules(self, proposal: RealmsProposal, analysis: ProposalAnalysis) -> ProposalAnalysis:
        """Apply DAO-specific governance rules"""
        
        # Emergency detection
        emergency_keywords = self.config["automation"]["emergency_keywords"]
        description = proposal.description_link.lower()
        
        if any(keyword in description for keyword in emergency_keywords):
            analysis.risk_level = RiskLevel.CRITICAL
            analysis.risk_factors.append("Emergency proposal detected")
        
        # Treasury threshold check
        if "treasury" in description or "fund" in description:
            # In real implementation, would parse actual amounts
            analysis.risk_level = RiskLevel.HIGH
            analysis.risk_factors.append("Treasury impact requires review")
        
        # Voting deadline urgency
        if proposal.start_voting_at and proposal.voting_completed_at:
            # Check if voting period is very short
            pass  # Would implement time-based urgency rules
        
        return analysis
    
    async def make_governance_decision(self, proposal: RealmsProposal, analysis: ProposalAnalysis) -> Dict:
        """Make automated governance decision"""
        
        config = self.config["automation"]
        
        if not config["enabled"]:
            return {
                "action": "human_review",
                "reason": "Automation disabled",
                "confidence": 1.0
            }
        
        # Auto-approve criteria
        auto_approve = config["auto_approve"]
        if (analysis.risk_level.value == auto_approve["max_risk_level"] and
            analysis.sentiment_score.value >= auto_approve["min_sentiment"] and
            analysis.confidence_score >= auto_approve["min_confidence"]):
            
            return {
                "action": "auto_approve",
                "reason": f"Low risk ({analysis.risk_level.value}), positive sentiment ({analysis.sentiment_score.value}), high confidence ({analysis.confidence_score:.2f})",
                "confidence": analysis.confidence_score,
                "vote": "approve"
            }
        
        # Auto-reject criteria
        auto_reject = config["auto_reject"]
        if (analysis.risk_level.value == auto_reject["min_risk_level"] or
            analysis.sentiment_score.value <= auto_reject["max_sentiment"]):
            
            return {
                "action": "auto_reject",
                "reason": f"High risk ({analysis.risk_level.value}) or negative sentiment ({analysis.sentiment_score.value})",
                "confidence": analysis.confidence_score,
                "vote": "reject"
            }
        
        # Default to human review
        return {
            "action": "human_review",
            "reason": f"Medium risk ({analysis.risk_level.value}) requires human judgment",
            "confidence": analysis.confidence_score,
            "vote": None
        }
    
    async def process_proposal(self, proposal: RealmsProposal) -> Dict:
        """Process a single proposal through the full pipeline"""
        
        logger.info(f"Processing proposal: {proposal.name} from {proposal.realm}")
        
        try:
            # Analyze proposal
            analysis = await self.analyze_proposal(proposal)
            
            # Make governance decision
            decision = await self.make_governance_decision(proposal, analysis)
            
            # Create full processing result
            result = {
                "proposal": {
                    "public_key": proposal.public_key,
                    "realm": proposal.realm,
                    "name": proposal.name,
                    "state": proposal.state,
                    "yes_votes": proposal.yes_votes_count,
                    "no_votes": proposal.no_votes_count
                },
                "analysis": analysis.to_dict(),
                "decision": decision,
                "processed_at": datetime.now().isoformat()
            }
            
            # Store result
            self.processed_proposals[proposal.public_key] = result
            
            # Emit events
            await self.emit_event("analysis_complete", result)
            await self.emit_event(decision["action"], result)
            
            # Log decision
            self.log_governance_decision(proposal, analysis, decision)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process proposal {proposal.public_key}: {e}")
            return {
                "proposal": {"public_key": proposal.public_key},
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    def log_governance_decision(self, proposal: RealmsProposal, analysis: ProposalAnalysis, decision: Dict):
        """Log governance decision for audit trail"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "proposal_id": proposal.public_key,
            "realm": proposal.realm,
            "proposal_name": proposal.name,
            "analysis": {
                "risk_level": analysis.risk_level.value,
                "sentiment": analysis.sentiment_score.value,
                "confidence": analysis.confidence_score
            },
            "decision": decision["action"],
            "reason": decision["reason"],
            "vote": decision.get("vote")
        }
        
        # In production, would write to database/audit log
        logger.info(f"GOVERNANCE DECISION: {json.dumps(log_entry, indent=2)}")
        
        # Print human-readable summary
        print(f"\n🏛️  GOVERNANCE DECISION")
        print(f"   Proposal: {proposal.name}")
        print(f"   DAO: {proposal.realm}")
        print(f"   Risk: {analysis.risk_level.value.upper()}")
        print(f"   Sentiment: {analysis.sentiment_score.value}")
        print(f"   Decision: {decision['action'].upper()}")
        print(f"   Reason: {decision['reason']}")
        if decision.get("vote"):
            print(f"   Vote: {decision['vote'].upper()}")
        print(f"   Confidence: {analysis.confidence_score:.1%}")
        print("-" * 50)
    
    async def handle_new_proposals(self, proposals: List[RealmsProposal]):
        """Handle newly discovered proposals"""
        
        logger.info(f"Processing {len(proposals)} new proposals")
        
        for proposal in proposals:
            await self.emit_event("new_proposal", {
                "proposal": proposal,
                "discovered_at": datetime.now().isoformat()
            })
            
            # Process proposal
            result = await self.process_proposal(proposal)
            
            # Rate limiting to avoid overwhelming the system
            await asyncio.sleep(1)
    
    async def start_monitoring(self):
        """Start continuous governance monitoring"""
        
        logger.info("🏛️  Starting Agora Governance Engine...")
        
        async with self.solana_client:
            # Set up monitoring callback
            await self.solana_client.monitor_governance(
                callback_func=self.handle_new_proposals,
                interval=self.config["monitoring"]["interval"]
            )
    
    def get_statistics(self) -> Dict:
        """Get governance processing statistics"""
        
        total = len(self.processed_proposals)
        if total == 0:
            return {"total_proposals": 0}
        
        decisions = [p["decision"]["action"] for p in self.processed_proposals.values() if "decision" in p]
        
        stats = {
            "total_proposals": total,
            "auto_approved": decisions.count("auto_approve"),
            "auto_rejected": decisions.count("auto_reject"),
            "human_review": decisions.count("human_review"),
            "automation_rate": (decisions.count("auto_approve") + decisions.count("auto_reject")) / max(len(decisions), 1)
        }
        
        return stats

# Example usage and testing
async def test_governance_engine():
    """Test the governance engine"""
    print("🧪 Testing Governance Engine...")
    
    engine = GovernanceEngine()
    
    # Add some test callbacks
    async def on_new_proposal(data):
        print(f"📋 NEW: {data['proposal'].name} in {data['proposal'].realm}")
    
    async def on_auto_approve(data):
        print(f"✅ AUTO-APPROVED: {data['proposal']['name']}")
    
    async def on_human_review(data):
        print(f"👤 HUMAN REVIEW: {data['proposal']['name']}")
    
    engine.add_callback("new_proposal", on_new_proposal)
    engine.add_callback("auto_approve", on_auto_approve)
    engine.add_callback("human_review", on_human_review)
    
    # Test with real Solana data
    print("🔗 Connecting to Solana and scanning for proposals...")
    
    try:
        async with engine.solana_client:
            proposals = await engine.solana_client.discover_all_proposals()
            print(f"📊 Found {len(proposals)} active proposals")
            
            # Process first few proposals
            for proposal in proposals[:3]:
                await engine.process_proposal(proposal)
            
            # Show statistics
            stats = engine.get_statistics()
            print(f"\n📈 PROCESSING STATS:")
            print(f"   Total: {stats['total_proposals']}")
            print(f"   Auto-approved: {stats['auto_approved']}")
            print(f"   Auto-rejected: {stats['auto_rejected']}")  
            print(f"   Human review: {stats['human_review']}")
            print(f"   Automation rate: {stats['automation_rate']:.1%}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_governance_engine())