#!/usr/bin/env python3
"""
Vercel API index endpoint
"""

from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """API index endpoint"""
        
        api_info = {
            "name": "Agora Governance Agent API",
            "version": "1.0.0", 
            "description": "Autonomous DAO governance automation for Solana",
            "endpoints": {
                "/api/proposals": "Get current governance proposals with AI analysis",
                "/api/stats": "Get governance statistics and system metrics"
            },
            "system": {
                "status": "operational",
                "daosMonitored": 4,
                "automationRate": "25%",
                "builtFor": "Colosseum Agent Hackathon"
            },
            "links": {
                "dashboard": "/",
                "github": "https://github.com/Goodnessmbakara/agora-dao-agent",
                "hackathon": "https://colosseum.com/agent-hackathon/projects/agora-autonomous-dao-governance-agent"
            }
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(api_info, indent=2).encode())