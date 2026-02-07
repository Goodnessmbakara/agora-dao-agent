# Agora Governance Dashboard

🏛️ **Interactive dashboard for monitoring autonomous DAO governance**

## Features

- **Real-time Proposal Monitoring** - Live display of governance proposals across major Solana DAOs
- **AI Analysis Visualization** - Risk levels, sentiment scores, and confidence ratings
- **Automated Decision Tracking** - Shows auto-approve/reject decisions vs human review
- **Governance Statistics** - Automation rates, risk distribution, DAO coverage
- **Activity Feed** - Real-time log of governance events and decisions

## Quick Start

```bash
# Start the dashboard server
python3 dashboard/server.py

# Or specify custom port
python3 dashboard/server.py --port 8081

# Run without auto-opening browser
python3 dashboard/server.py --no-browser
```

The dashboard will be available at `http://localhost:8080` (or your specified port).

## API Endpoints

- `GET /api/proposals` - Current governance proposals with analysis
- `GET /api/stats` - Governance statistics and metrics

## Dashboard Sections

### 📊 Statistics Overview
- Total proposals processed
- Automation rate and decisions made
- DAOs monitored (Mango, Jupiter, Marinade, Pyth)
- High-risk proposals requiring review

### 🏛️ Live Governance Analysis
- Real-time proposal cards with:
  - Risk level classification (LOW/MEDIUM/HIGH/CRITICAL)
  - Sentiment analysis scores
  - Automated decision recommendations
  - Voting statistics (YES/NO counts)
  - Confidence ratings

### ⚡ Activity Feed
- Recent governance events
- Decision notifications
- System status updates

## Design Features

- **Modern UI** with glassmorphism effects and smooth animations
- **Real-time updates** with 30-second auto-refresh
- **Responsive design** works on desktop and mobile
- **Interactive elements** with hover effects and click handlers
- **Color-coded risk levels** for quick visual assessment
- **Professional gradient styling** with proper contrast

## Technical Implementation

- **Pure HTML/CSS/JavaScript** - No framework dependencies
- **Embedded Python server** - Lightweight HTTP server with API
- **Mock data integration** - Demonstrates with realistic DAO proposals
- **RESTful API design** - Clean endpoints for data access
- **Auto-refresh capability** - Live monitoring simulation

## Production Integration

The dashboard is designed to integrate with the live Agora governance engine:

1. Replace mock data with real Solana governance client
2. Connect API endpoints to governance database
3. Add WebSocket support for real-time updates
4. Implement detailed proposal view modals
5. Add user authentication for DAO-specific access

## Customization

The dashboard can be easily customized for specific DAOs:

- Modify color schemes and branding
- Adjust risk thresholds and decision criteria  
- Add custom metrics and KPIs
- Integrate with DAO-specific governance tools
- Extend API with additional endpoints

---

**Built for the Colosseum Agent Hackathon** - Demonstrating real-time autonomous governance monitoring and decision-making for Solana DAOs.