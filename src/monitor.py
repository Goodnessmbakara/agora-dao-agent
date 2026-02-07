#!/usr/bin/env python3
"""
Agora DAO Governance Monitor
Continuously monitors Solana governance programs for new proposals
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Proposal:
    """Represents a DAO proposal"""
    id: str
    dao_name: str
    title: str
    description: str
    status: str
    created_at: datetime
    voting_ends: Optional[datetime]
    proposer: str
    program_id: str
    proposal_address: str
    
    def to_dict(self):
        return asdict(self)

class GovernanceMonitor:
    """Monitors Solana governance programs for proposals"""
    
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.rpc_url = rpc_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.known_proposals: Dict[str, Proposal] = {}
        
        # Known governance programs to monitor
        self.governance_programs = {
            "GovER5Lthms3bLBqWub97yVrMmEogzX7xNjdXpPPCVZw": "Realms",  # SPL Governance
            "JPGov2SBA6f7XSJF5R4Si5jEJekGiyrwP2m7gSEqLUs": "Jupiter DAO",
            # Add more governance programs here
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_program_accounts(self, program_id: str) -> List[Dict]:
        """Get all accounts for a governance program"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getProgramAccounts",
            "params": [
                program_id,
                {
                    "encoding": "base64",
                    "filters": [
                        {"memcmp": {"offset": 0, "bytes": "1"}}  # Filter for proposals
                    ]
                }
            ]
        }
        
        async with self.session.post(self.rpc_url, json=payload) as response:
            data = await response.json()
            return data.get("result", [])
    
    async def parse_proposal(self, account_data: Dict, program_name: str) -> Optional[Proposal]:
        """Parse proposal data from account"""
        try:
            # This is a simplified parser - would need proper borsh deserialization
            pubkey = account_data["pubkey"]
            
            # For demo, create a mock proposal
            proposal = Proposal(
                id=pubkey,
                dao_name=program_name,
                title=f"Proposal {pubkey[:8]}...",
                description="Proposal details would be parsed from account data",
                status="Active",
                created_at=datetime.now(),
                voting_ends=None,
                proposer="Unknown",
                program_id=pubkey,
                proposal_address=pubkey
            )
            
            return proposal
            
        except Exception as e:
            logger.error(f"Failed to parse proposal: {e}")
            return None
    
    async def check_for_new_proposals(self) -> List[Proposal]:
        """Check all governance programs for new proposals"""
        new_proposals = []
        
        for program_id, program_name in self.governance_programs.items():
            try:
                logger.info(f"Checking {program_name} ({program_id}) for proposals...")
                accounts = await self.get_program_accounts(program_id)
                
                for account_data in accounts:
                    proposal = await self.parse_proposal(account_data, program_name)
                    if proposal and proposal.id not in self.known_proposals:
                        new_proposals.append(proposal)
                        self.known_proposals[proposal.id] = proposal
                        logger.info(f"Found new proposal: {proposal.title}")
                        
            except Exception as e:
                logger.error(f"Error checking {program_name}: {e}")
        
        return new_proposals
    
    async def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring loop"""
        logger.info("Starting governance monitoring...")
        
        while True:
            try:
                new_proposals = await self.check_for_new_proposals()
                
                if new_proposals:
                    logger.info(f"Found {len(new_proposals)} new proposals")
                    await self.process_new_proposals(new_proposals)
                else:
                    logger.info("No new proposals found")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def process_new_proposals(self, proposals: List[Proposal]):
        """Process newly discovered proposals"""
        for proposal in proposals:
            logger.info(f"Processing proposal: {proposal.title}")
            
            # Here we would:
            # 1. Analyze the proposal content
            # 2. Check against automation rules
            # 3. Store in database
            # 4. Trigger alerts if needed
            
            # For now, just log the proposal
            print(f"NEW PROPOSAL: {proposal.dao_name} - {proposal.title}")
            print(f"Description: {proposal.description}")
            print(f"Status: {proposal.status}")
            print("---")

async def main():
    """Main monitoring loop"""
    async with GovernanceMonitor() as monitor:
        await monitor.start_monitoring(interval=60)  # Check every minute

if __name__ == "__main__":
    asyncio.run(main())