#!/usr/bin/env python3
"""
Production dashboard server for Agora governance monitoring
Connected to live Solana governance data
"""

import http.server
import socketserver
import json
import os
import sys
from datetime import datetime
import webbrowser
import asyncio

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.solana_client import SolanaGovernanceMonitor
from src.governance_engine import GovernanceEngine

class AgoraDashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for Agora dashboard with live data"""
    
    # Shared state for live data
    live_proposals = []
    live_stats = {}
    last_update = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/api/proposals':
            self.serve_api_proposals()
            return
        elif self.path == '/api/stats':
            self.serve_api_stats()
            return
        
        super().do_GET()
    
    def serve_api_proposals(self):
        """Serve live proposal data from Solana"""
        
        # Use live data if available, fallback to demo
        proposals = self.live_proposals if self.live_proposals else self._get_demo_proposals()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "proposals": proposals,
            "timestamp": datetime.now().isoformat(),
            "source": "live" if self.live_proposals else "demo",
            "lastUpdate": self.last_update.isoformat() if self.last_update else None
        }
        self.wfile.write(json.dumps(response).encode())
    
    def serve_api_stats(self):
        """Serve governance statistics"""
        
        # Use live stats if available
        stats = self.live_stats if self.live_stats else self._get_demo_stats()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(stats).encode())
    
    def _get_demo_proposals(self):
        """Demo data fallback"""
        return [
            {
                "id": "demo_mango_001",
                "title": "Treasury Diversification - Allocate 25% to SOL",
                "dao": "Mango DAO",
                "status": "Voting",
                "riskLevel": "high",
                "sentiment": 0,
                "decision": "human-review",
                "confidence": 0.85,
                "yesVotes": 1250,
                "noVotes": 340,
                "processed": datetime.now().isoformat()
            },
            {
                "id": "demo_jupiter_001", 
                "title": "Emergency Security Patch for Swap Router",
                "dao": "Jupiter DAO",
                "status": "Voting",
                "riskLevel": "critical",
                "sentiment": -1,
                "decision": "human-review",
                "confidence": 0.92,
                "yesVotes": 2800,
                "noVotes": 120,
                "processed": datetime.now().isoformat()
            },
            {
                "id": "demo_marinade_001",
                "title": "Parameter Update - Increase Validator Commission Cap",
                "dao": "Marinade DAO",
                "status": "Voting", 
                "riskLevel": "low",
                "sentiment": 0,
                "decision": "auto-approve",
                "confidence": 0.78,
                "yesVotes": 890,
                "noVotes": 240,
                "processed": datetime.now().isoformat()
            },
            {
                "id": "demo_pyth_001",
                "title": "Community Growth Fund - Educational Initiatives",
                "dao": "Pyth DAO", 
                "status": "Voting",
                "riskLevel": "high",
                "sentiment": 1,
                "decision": "human-review",
                "confidence": 0.81,
                "yesVotes": 1580,
                "noVotes": 420,
                "processed": datetime.now().isoformat()
            }
        ]
    
    def _get_demo_stats(self):
        """Demo stats fallback"""
        return {
            "totalProposals": 4,
            "automatedDecisions": 1,
            "humanReview": 3,
            "automationRate": 25,
            "highRiskCount": 3,
            "daosMonitored": 4,
            "uptime": "demo mode",
            "source": "demo"
        }

async def update_live_data():
    """Background task to fetch live Solana governance data"""
    
    print("🔄 Starting live data updater...")
    
    # Initialize Solana monitor
    monitor = SolanaGovernanceMonitor()
    engine = GovernanceEngine()
    
    while True:
        try:
            print(f"📡 Fetching live governance data... [{datetime.now().strftime('%H:%M:%S')}]")
            
            # Fetch proposals from all DAOs
            all_proposals = []
            dao_configs = monitor.dao_configs
            
            for dao_name, config in dao_configs.items():
                try:
                    proposals = await monitor.get_dao_proposals(config["governance_program"])
                    
                    # Analyze each proposal
                    for prop in proposals:
                        analysis = engine.analyze_proposal(prop)
                        
                        # Format for API
                        all_proposals.append({
                            "id": prop.get("pubkey", "unknown"),
                            "title": prop.get("title", "Untitled Proposal"),
                            "dao": dao_name,
                            "status": prop.get("state", "Unknown"),
                            "riskLevel": analysis.get("risk_level", "medium"),
                            "sentiment": analysis.get("sentiment_score", 0),
                            "decision": analysis.get("decision", {}).get("action", "human-review"),
                            "confidence": analysis.get("confidence_score", 0.5),
                            "yesVotes": prop.get("yes_votes", 0),
                            "noVotes": prop.get("no_votes", 0),
                            "processed": datetime.now().isoformat()
                        })
                    
                    print(f"  ✓ {dao_name}: {len(proposals)} proposals")
                    
                except Exception as e:
                    print(f"  ✗ {dao_name}: {str(e)}")
            
            # Update shared state
            AgoraDashboardHandler.live_proposals = all_proposals
            AgoraDashboardHandler.last_update = datetime.now()
            
            # Update stats
            total = len(all_proposals)
            automated = sum(1 for p in all_proposals if p["decision"] == "auto-approve")
            high_risk = sum(1 for p in all_proposals if p["riskLevel"] in ["high", "critical"])
            
            AgoraDashboardHandler.live_stats = {
                "totalProposals": total,
                "automatedDecisions": automated,
                "humanReview": total - automated,
                "automationRate": round((automated / total * 100) if total > 0 else 0),
                "highRiskCount": high_risk,
                "daosMonitored": len(dao_configs),
                "lastUpdate": datetime.now().isoformat(),
                "source": "live"
            }
            
            print(f"✅ Updated: {total} proposals, {automated} automated ({round(automated/total*100) if total > 0 else 0}%)")
            
        except Exception as e:
            print(f"❌ Error updating live data: {e}")
            # Keep using existing data or demo data
        
        # Update every 2 minutes
        await asyncio.sleep(120)

def start_dashboard(port=8080, open_browser=True, live_mode=False):
    """Start the Agora dashboard server"""
    
    dashboard_dir = os.path.dirname(__file__)
    os.chdir(dashboard_dir)
    
    print("🏛️  AGORA GOVERNANCE DASHBOARD")
    print("=" * 40)
    
    if live_mode:
        print("🌐 LIVE MODE: Connecting to Solana mainnet...")
        # Start background data updater
        import threading
        def run_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(update_live_data())
        
        updater_thread = threading.Thread(target=run_async_loop, daemon=True)
        updater_thread.start()
    else:
        print("📋 DEMO MODE: Using sample data")
        print("💡 Use --live flag for real Solana data")
    
    print(f"🚀 Starting server on port {port}...")
    
    try:
        with socketserver.TCPServer(("", port), AgoraDashboardHandler) as httpd:
            url = f"http://localhost:{port}"
            print(f"📊 Dashboard available at: {url}")
            print("🔄 Auto-refresh enabled (30s intervals)")
            if live_mode:
                print("⚡ Live governance monitoring active (updates every 2min)")
            print("\n🛑 Press Ctrl+C to stop")
            print("-" * 40)
            
            if open_browser:
                print("🌐 Opening browser...")
                try:
                    webbrowser.open(url)
                except:
                    print("❌ Could not open browser automatically")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down dashboard...")
    except PermissionError:
        print(f"❌ Permission denied on port {port}. Try a different port.")
        print("💡 Example: python dashboard/server.py --port 8081")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Try a different port.")
            print("💡 Example: python dashboard/server.py --port 8081")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agora Governance Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve dashboard (default: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--live", action="store_true", help="Enable live Solana data (requires RPC access)")
    
    args = parser.parse_args()
    
    start_dashboard(port=args.port, open_browser=not args.no_browser, live_mode=args.live)