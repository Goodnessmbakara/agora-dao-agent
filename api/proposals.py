#!/usr/bin/env python3
"""
Vercel API endpoint for governance proposals
"""

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Return governance proposals data"""
        
        # Mock governance proposals data
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
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Return data
        response = {
            "proposals": proposals,
            "timestamp": datetime.now().isoformat(),
            "system": "agora-governance-agent",
            "version": "1.0.0"
        }
        
        self.wfile.write(json.dumps(response).encode())