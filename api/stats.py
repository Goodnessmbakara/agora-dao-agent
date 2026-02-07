#!/usr/bin/env python3
"""
Vercel API endpoint for governance statistics
"""

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Return governance statistics"""
        
        stats = {
            "totalProposals": 4,
            "automatedDecisions": 1,
            "humanReview": 3,
            "automationRate": 25,
            "highRiskCount": 3,
            "daosMonitored": 4,
            "uptime": "2h 45m",
            "lastUpdate": datetime.now().isoformat(),
            "system": {
                "name": "Agora Governance Agent",
                "version": "1.0.0",
                "status": "operational"
            },
            "daos": [
                {"name": "Mango DAO", "proposals": 1, "lastScan": "2m ago"},
                {"name": "Jupiter DAO", "proposals": 1, "lastScan": "5m ago"},
                {"name": "Marinade DAO", "proposals": 1, "lastScan": "8m ago"},
                {"name": "Pyth DAO", "proposals": 1, "lastScan": "12m ago"}
            ],
            "riskDistribution": {
                "low": 1,
                "medium": 0, 
                "high": 2,
                "critical": 1
            },
            "decisionBreakdown": {
                "autoApprove": 1,
                "autoReject": 0,
                "humanReview": 3
            }
        }
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json.dumps(stats).encode())