#!/usr/bin/env python3
"""
Simple dashboard server for Agora governance monitoring
"""

import http.server
import socketserver
import json
import os
import sys
from datetime import datetime
import webbrowser

class AgoraDashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for Agora dashboard"""
    
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
        """Serve mock proposal data"""
        proposals = [
            {
                "id": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgHkJ",
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
                "id": "9yBrqpF1KLjH3wQX2Zm4Nr8JN6wBrCqA4vS5TgHkJmL2", 
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
                "id": "3mE8KnX9vL2Qw5Rp4TgHz6Jc1FyNdVbS7uAq2MpYrT8",
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
                "id": "6kR4vW2pN8Qm3xYz1JhFg9Cs5BtUa7Lp2MnXr4TyE1A",
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
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"proposals": proposals, "timestamp": datetime.now().isoformat()}
        self.wfile.write(json.dumps(response).encode())
    
    def serve_api_stats(self):
        """Serve governance statistics"""
        stats = {
            "totalProposals": 4,
            "automatedDecisions": 1,
            "humanReview": 3,
            "automationRate": 25,
            "highRiskCount": 3,
            "daosMonitored": 4,
            "uptime": "2h 15m"
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(stats).encode())

def start_dashboard(port=8080, open_browser=True):
    """Start the Agora dashboard server"""
    
    dashboard_dir = os.path.dirname(__file__)
    os.chdir(dashboard_dir)
    
    print("🏛️  AGORA GOVERNANCE DASHBOARD")
    print("=" * 40)
    print(f"🚀 Starting server on port {port}...")
    
    try:
        with socketserver.TCPServer(("", port), AgoraDashboardHandler) as httpd:
            url = f"http://localhost:{port}"
            print(f"📊 Dashboard available at: {url}")
            print("🔄 Auto-refresh enabled (30s intervals)")
            print("⚡ Live governance monitoring active")
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
    
    args = parser.parse_args()
    
    start_dashboard(port=args.port, open_browser=not args.no_browser)