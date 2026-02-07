#!/usr/bin/env python3
"""
LIVE dashboard server for Agora governance monitoring
Connects to real Solana governance programs via agora_live.py
"""

import http.server
import socketserver
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.solana_client import SolanaGovernanceClient
from src.analyzer import ProposalAnalyzer
from src.governance_engine import GovernanceEngine

class AgoraLiveDashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for live Agora dashboard with real Solana data"""
    
    # Shared state for governance monitoring
    governance_client = None
    analyzer = None
    engine = None
    cached_proposals = []
    cached_stats = {}
    last_update = None
    
    def __init__(self, *args, **kwargs):
        # Initialize governance components on first request
        if AgoraLiveDashboardHandler.governance_client is None:
            print("🔧 Initializing governance monitoring...")
            try:
                AgoraLiveDashboardHandler.governance_client = SolanaGovernanceClient()
                AgoraLiveDashboardHandler.analyzer = ProposalAnalyzer()
                AgoraLiveDashboardHandler.engine = GovernanceEngine(
                    analyzer=AgoraLiveDashboardHandler.analyzer
                )
                print("✅ Governance monitoring initialized")
            except Exception as e:
                print(f"❌ Failed to initialize governance: {e}")
        
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
        elif self.path == '/api/refresh':
            self.refresh_governance_data()
            return
        
        super().do_GET()
    
    def refresh_governance_data(self):
        """Force refresh governance data from Solana"""
        try:
            print("🔄 Refreshing governance data...")
            
            # Get live proposals from all DAOs
            all_proposals = []
            daos = ['mango', 'jupiter', 'marinade', 'pyth']
            
            for dao in daos:
                try:
                    proposals = self.governance_client.get_active_proposals(dao)
                    
                    # Analyze each proposal
                    for prop in proposals:
                        analysis = self.analyzer.analyze_proposal(
                            title=prop.get('title', 'Untitled'),
                            description=prop.get('description', ''),
                            dao_context=dao
                        )
                        
                        # Merge analysis with proposal data
                        all_proposals.append({
                            "id": prop.get('pubkey', 'unknown'),
                            "title": prop.get('title', 'Untitled'),
                            "dao": dao.upper() + " DAO",
                            "status": prop.get('status', 'Unknown'),
                            "riskLevel": analysis.get('risk_level', 'unknown'),
                            "sentiment": analysis.get('sentiment_score', 0),
                            "decision": analysis.get('automation_recommendation', 'human-review'),
                            "confidence": analysis.get('confidence_score', 0),
                            "yesVotes": prop.get('yes_votes', 0),
                            "noVotes": prop.get('no_votes', 0),
                            "processed": datetime.now().isoformat()
                        })
                except Exception as e:
                    print(f"⚠️ Error fetching {dao} proposals: {e}")
            
            # Update cache
            AgoraLiveDashboardHandler.cached_proposals = all_proposals
            AgoraLiveDashboardHandler.last_update = datetime.now()
            
            # Calculate stats
            total = len(all_proposals)
            automated = sum(1 for p in all_proposals if p['decision'] == 'auto-approve')
            human_review = sum(1 for p in all_proposals if p['decision'] == 'human-review')
            high_risk = sum(1 for p in all_proposals if p['riskLevel'] in ['high', 'critical'])
            
            AgoraLiveDashboardHandler.cached_stats = {
                "totalProposals": total,
                "automatedDecisions": automated,
                "humanReview": human_review,
                "automationRate": round((automated / total * 100) if total > 0 else 0, 1),
                "highRiskCount": high_risk,
                "daosMonitored": len(daos),
                "uptime": "live",
                "lastUpdate": AgoraLiveDashboardHandler.last_update.isoformat(),
                "source": "live"
            }
            
            print(f"✅ Refreshed {total} proposals from {len(daos)} DAOs")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "success": True,
                "proposals": len(all_proposals),
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"❌ Refresh failed: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "success": False,
                "error": str(e)
            }
            self.wfile.write(json.dumps(response).encode())
    
    def serve_api_proposals(self):
        """Serve LIVE proposal data from Solana"""
        
        # Use cached data if available and recent (< 2 minutes old)
        if (AgoraLiveDashboardHandler.cached_proposals and 
            AgoraLiveDashboardHandler.last_update and
            (datetime.now() - AgoraLiveDashboardHandler.last_update).seconds < 120):
            proposals = AgoraLiveDashboardHandler.cached_proposals
        else:
            # Fall back to demo data if cache is stale
            print("⚠️ Using demo data - cache stale or empty. Call /api/refresh to update")
            proposals = self._get_demo_proposals()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "proposals": proposals,
            "timestamp": datetime.now().isoformat(),
            "source": "live" if AgoraLiveDashboardHandler.cached_proposals else "demo",
            "lastUpdate": AgoraLiveDashboardHandler.last_update.isoformat() if AgoraLiveDashboardHandler.last_update else None
        }
        self.wfile.write(json.dumps(response).encode())
    
    def serve_api_stats(self):
        """Serve LIVE governance statistics"""
        
        if AgoraLiveDashboardHandler.cached_stats:
            stats = AgoraLiveDashboardHandler.cached_stats
        else:
            print("⚠️ Using demo stats - no live data yet. Call /api/refresh")
            stats = {
                "totalProposals": 0,
                "automatedDecisions": 0,
                "humanReview": 0,
                "automationRate": 0,
                "highRiskCount": 0,
                "daosMonitored": 4,
                "uptime": "initializing",
                "source": "demo"
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(stats).encode())
    
    def _get_demo_proposals(self):
        """Fallback demo proposals"""
        return [
            {
                "id": "demo-1",
                "title": "Loading live data...",
                "dao": "System",
                "status": "Initializing",
                "riskLevel": "low",
                "sentiment": 0,
                "decision": "pending",
                "confidence": 0,
                "yesVotes": 0,
                "noVotes": 0,
                "processed": datetime.now().isoformat()
            }
        ]

def start_dashboard(port=8080):
    """Start the LIVE Agora dashboard server"""
    
    dashboard_dir = os.path.dirname(__file__)
    os.chdir(dashboard_dir)
    
    print("🏛️  AGORA GOVERNANCE DASHBOARD - LIVE MODE")
    print("=" * 50)
    print("🔴 LIVE DATA: Connecting to Solana governance...")
    print(f"🚀 Starting server on port {port}...")
    print()
    print("📊 API Endpoints:")
    print(f"   GET /api/proposals  - Live proposal data")
    print(f"   GET /api/stats      - Live statistics")
    print(f"   GET /api/refresh    - Force data refresh")
    print()
    
    try:
        with socketserver.TCPServer(("", port), AgoraLiveDashboardHandler) as httpd:
            url = f"http://localhost:{port}"
            print(f"✅ Dashboard available at: {url}")
            print("🔄 Auto-refresh enabled (30s intervals)")
            print("💡 Manually refresh: curl http://localhost:8080/api/refresh")
            print("\n🛑 Press Ctrl+C to stop")
            print("-" * 50)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down dashboard...")
    except PermissionError:
        print(f"❌ Permission denied on port {port}")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use")
        else:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agora Live Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve (default: 8080)")
    
    args = parser.parse_args()
    
    start_dashboard(port=args.port)
