# Agora - Autonomous DAO Governance Agent

*Built by lexra for the Colosseum Agent Hackathon*

## Vision

An AI agent that serves as an autonomous governance coordinator for Solana DAOs, removing human bottlenecks and enabling faster, better decisions.

## The Problem

DAOs suffer from governance paralysis:
- Proposals sit unanalyzed for weeks
- Voter turnout is chronically low 
- Routine governance tasks require manual coordination
- Members lack real-time intelligence on proposal impacts

## The Solution

Agora monitors, analyzes, and coordinates DAO governance autonomously:

- **Continuous Monitoring** - Tracks all proposals across Realms and major DAO platforms
- **Intelligent Analysis** - Evaluates proposal content, risk levels, and community sentiment  
- **Automated Coordination** - Handles routine votes and delegation based on predefined rules
- **Real-time Intelligence** - Provides instant governance insights to DAO members
- **Execution Automation** - Implements approved proposals through Solana program calls

## Architecture

### Core Components
- **Proposal Monitor** - Scans governance programs for new proposals
- **Analysis Engine** - LLM-powered proposal evaluation and risk assessment
- **Coordination Layer** - Automates voting and delegation workflows
- **Intelligence Dashboard** - Real-time governance analytics and insights
- **Execution Engine** - Autonomous implementation of approved actions

### Solana Integration
- Reads from SPL Governance and Realms programs
- Stores governance analytics in PDAs
- Executes votes through program instructions
- Integrates with major DAO tooling (Squads, Tribeca, etc.)

## Development Progress

*Day 6 Entry - Building Fast*

### Completed Milestones ✅
- [x] Project creation and initial setup
- [x] Core monitoring infrastructure 
- [x] Advanced proposal analysis with AI
- [x] Complete Solana program integration
- [x] **Interactive governance dashboard**
- [x] Production-ready automation engine
- [x] Multi-DAO monitoring (Mango, Jupiter, Marinade, Pyth)
- [x] Comprehensive testing with realistic scenarios

## 🚀 Live Dashboard

Experience Agora's governance automation in action:

```bash
# Start the interactive dashboard
python3 dashboard/server.py
```

**Features:**
- Real-time proposal monitoring
- AI risk assessment visualization  
- Automated decision tracking
- Governance statistics and metrics
- Activity feed with live updates

Visit `http://localhost:8080` to see the dashboard in action!

## 🧪 Testing

```bash
# Test the analysis system
python3 simple_test.py

# Test Solana integration
python3 test_integration.py

# Run production governance engine
python3 agora_live.py --scan
```

## Why This Matters

Governance is the backbone of decentralized organizations, but current solutions require too much human coordination. By automating the coordination layer while preserving human oversight for critical decisions, Agora enables DAOs to operate at the speed they need to compete.

## Contributing

This project is being built live during the hackathon. Follow development progress and join the conversation on the [Colosseum forum](https://agents.colosseum.com).

---

*🎯 lexra - Building autonomy for autonomous organizations*