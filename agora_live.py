#!/usr/bin/env python3
"""
Agora Live - Production governance monitoring with real Solana data
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict
import click

try:
    from src.governance_engine import GovernanceEngine
    from src.solana_client import SolanaGovernanceClient
except ImportError:
    # Fallback for development
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from src.governance_engine import GovernanceEngine  
    from src.solana_client import SolanaGovernanceClient

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgoraLiveAgent:
    """Production Agora agent with real Solana integration"""
    
    def __init__(self, config_file: str = None):
        self.config = self.load_config(config_file)
        self.engine = GovernanceEngine(self.config)
        self.setup_callbacks()
        self.stats = {
            "started_at": datetime.now().isoformat(),
            "proposals_processed": 0,
            "decisions_made": 0,
            "automated_actions": 0
        }
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from file or use defaults"""
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config {config_file}: {e}")
        
        # Default production config
        return {
            "automation": {
                "enabled": True,
                "auto_approve": {
                    "max_risk_level": "low",
                    "min_sentiment": 1,  # Only positive sentiment
                    "min_confidence": 0.85  # High confidence required
                },
                "auto_reject": {
                    "min_risk_level": "critical",
                    "max_sentiment": -2
                },
                "treasury_threshold": 25000,
                "emergency_keywords": ["emergency", "critical", "urgent", "hack", "exploit", "security"]
            },
            "monitoring": {
                "interval": 180,  # 3 minutes for production
                "max_proposals_per_scan": 100
            },
            "alerts": {
                "discord_webhook": None,  # Would be configured in production
                "email_alerts": False,
                "console_only": True
            }
        }
    
    def setup_callbacks(self):
        """Setup event callbacks for governance events"""
        
        # Track all events for statistics
        async def track_stats(event_type, data):
            if event_type == "new_proposal":
                self.stats["proposals_processed"] += 1
            elif event_type in ["auto_approve", "auto_reject"]:
                self.stats["decisions_made"] += 1
                self.stats["automated_actions"] += 1
            elif event_type == "human_review":
                self.stats["decisions_made"] += 1
        
        # New proposal alerts
        async def on_new_proposal(data):
            proposal = data["proposal"]
            self.send_alert(
                f"🏛️ NEW PROPOSAL: {proposal.name} in {proposal.realm}",
                f"Status: {proposal.state} | Link: {proposal.description_link}"
            )
            await track_stats("new_proposal", data)
        
        # Auto-approval alerts
        async def on_auto_approve(data):
            proposal_data = data["proposal"]
            analysis = data["analysis"]
            self.send_alert(
                f"✅ AUTO-APPROVED: {proposal_data['name']}",
                f"DAO: {proposal_data['realm']} | Risk: {analysis['risk_level']} | Confidence: {analysis['confidence_score']:.1%}"
            )
            await track_stats("auto_approve", data)
        
        # Auto-rejection alerts
        async def on_auto_reject(data):
            proposal_data = data["proposal"]
            analysis = data["analysis"]
            self.send_alert(
                f"❌ AUTO-REJECTED: {proposal_data['name']}",
                f"DAO: {proposal_data['realm']} | Risk: {analysis['risk_level']} | Reason: {data['decision']['reason']}"
            )
            await track_stats("auto_reject", data)
        
        # Human review alerts
        async def on_human_review(data):
            proposal_data = data["proposal"]
            analysis = data["analysis"]
            decision = data["decision"]
            self.send_alert(
                f"👤 HUMAN REVIEW REQUIRED: {proposal_data['name']}",
                f"DAO: {proposal_data['realm']} | Risk: {analysis['risk_level']} | Sentiment: {analysis['sentiment_score']} | Reason: {decision['reason']}"
            )
            await track_stats("human_review", data)
        
        # Register callbacks
        self.engine.add_callback("new_proposal", on_new_proposal)
        self.engine.add_callback("auto_approve", on_auto_approve)
        self.engine.add_callback("auto_reject", on_auto_reject)
        self.engine.add_callback("human_review", on_human_review)
    
    def send_alert(self, title: str, message: str):
        """Send alert through configured channels"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        if self.config["alerts"]["console_only"]:
            print(f"\n🚨 ALERT [{timestamp}]")
            print(f"   {title}")
            print(f"   {message}")
            print("-" * 60)
        
        # In production, would also send to Discord/email/etc
        logger.info(f"ALERT: {title} - {message}")
    
    async def run_continuous(self):
        """Run continuous governance monitoring"""
        logger.info("🚀 Starting Agora Live Agent...")
        
        print("🏛️  AGORA LIVE - Autonomous DAO Governance Agent")
        print("=" * 60)
        print("🔗 Connecting to Solana mainnet...")
        print(f"📊 Monitoring {len(self.engine.solana_client.KNOWN_REALMS)} DAOs")
        print(f"⚙️  Automation: {'ENABLED' if self.config['automation']['enabled'] else 'DISABLED'}")
        print(f"⏱️  Scan interval: {self.config['monitoring']['interval']}s")
        print("-" * 60)
        
        try:
            await self.engine.start_monitoring()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Agora Live Agent...")
            self.print_final_stats()
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            print(f"💥 Fatal error: {e}")
    
    async def run_scan(self):
        """Run a single governance scan"""
        print("🔍 Running single governance scan...")
        
        async with self.engine.solana_client:
            proposals = await self.engine.solana_client.discover_all_proposals()
            print(f"📋 Found {len(proposals)} active proposals")
            
            if proposals:
                print("\nProcessing proposals:")
                for i, proposal in enumerate(proposals[:5], 1):  # Process first 5
                    print(f"  {i}. {proposal.name} ({proposal.realm})")
                    result = await self.engine.process_proposal(proposal)
                    await asyncio.sleep(0.5)  # Brief pause between proposals
                
                # Show final statistics
                stats = self.engine.get_statistics()
                print(f"\n📈 SCAN RESULTS:")
                print(f"   Processed: {stats['total_proposals']}")
                print(f"   Auto-approved: {stats['auto_approved']}")
                print(f"   Auto-rejected: {stats['auto_rejected']}")
                print(f"   Human review: {stats['human_review']}")
                print(f"   Automation rate: {stats['automation_rate']:.1%}")
            else:
                print("   No active proposals found")
    
    def print_final_stats(self):
        """Print final statistics on shutdown"""
        runtime = datetime.now().fromisoformat(self.stats["started_at"].replace("Z", "+00:00"))
        duration = datetime.now() - runtime
        
        print("\n📊 FINAL STATISTICS")
        print("-" * 30)
        print(f"Runtime: {duration}")
        print(f"Proposals processed: {self.stats['proposals_processed']}")
        print(f"Decisions made: {self.stats['decisions_made']}")
        print(f"Automated actions: {self.stats['automated_actions']}")
        if self.stats['decisions_made'] > 0:
            automation_rate = self.stats['automated_actions'] / self.stats['decisions_made']
            print(f"Automation rate: {automation_rate:.1%}")

@click.command()
@click.option('--live', is_flag=True, help='Run continuous monitoring')
@click.option('--scan', is_flag=True, help='Run single scan')
@click.option('--config', help='Configuration file path')
def main(live, scan, config):
    """Agora Live - Production DAO Governance Agent"""
    
    agent = AgoraLiveAgent(config)
    
    if live:
        asyncio.run(agent.run_continuous())
    elif scan:
        asyncio.run(agent.run_scan())
    else:
        print("🏛️  Agora Live - Autonomous DAO Governance Agent")
        print("\nUsage:")
        print("  --live    Run continuous monitoring")
        print("  --scan    Run single governance scan")
        print("  --config  Specify config file")
        print("\nExample:")
        print("  python agora_live.py --scan")
        print("  python agora_live.py --live")

if __name__ == "__main__":
    main()