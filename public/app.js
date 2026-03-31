/**
 * Agora DAO - Frontend Logic
 * Premium, High-Fidelity Dashboard Interactions
 */

const CONFIG = {
    ENDPOINTS: {
        PROPOSALS: '/api/proposals',
        STATS: '/api/stats'
    },
    REFRESH_INTERVAL: 45000 // 45 seconds
};

class AgoraDashboard {
    constructor() {
        this.stats = {
            totalProposals: 0,
            automatedDecisions: 0,
            automationRate: 0,
            daosMonitored: 4
        };
        this.proposals = [];
        this.init();
    }

    async init() {
        console.log('🏛️ Agora Dashboard Initializing...');
        await this.refreshData();
        this.setupPoll();
        this.setupEventListeners();
    }

    async refreshData() {
        this.showLoading();
        try {
            await Promise.all([
                this.fetchStats(),
                this.fetchProposals()
            ]);
            this.render();
        } catch (error) {
            console.error('Failed to refresh dashboard:', error);
            this.showError('Connection to Solana node interrupted. Retrying...');
        } finally {
            this.hideLoading();
        }
    }

    async fetchStats() {
        try {
            const response = await fetch(CONFIG.ENDPOINTS.STATS);
            if (!response.ok) throw new Error('Stats fetch failed');
            const data = await response.json();
            this.stats = { ...this.stats, ...data };
        } catch (e) {
            console.warn('Using fallback stats');
            // stats usually stay the same if transient failure
        }
    }

    async fetchProposals() {
        try {
            const response = await fetch(CONFIG.ENDPOINTS.PROPOSALS);
            if (!response.ok) throw new Error('Proposals fetch failed');
            const data = await response.json();
            this.proposals = data.proposals || [];
        } catch (e) {
            console.error('Error fetching proposals:', e);
        }
    }

    setupPoll() {
        setInterval(() => this.refreshData(), CONFIG.REFRESH_INTERVAL);
    }

    setupEventListeners() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }
    }

    showLoading() {
        const container = document.getElementById('proposals-container');
        if (container && this.proposals.length === 0) {
            container.innerHTML = `
                <div class="loader-container">
                    <span class="loader"></span>
                    <p style="margin-top: 1rem; color: var(--text-secondary);">Scanning Solana Realms...</p>
                </div>
            `;
        }
    }

    hideLoading() {
        // Handled by render()
    }

    showError(msg) {
        // Small toast or status indicator
        console.error(msg);
    }

    render() {
        this.updateStatsUI();
        this.updateProposalsUI();
    }

    updateStatsUI() {
        const els = {
            total: document.getElementById('stat-total-proposals'),
            automated: document.getElementById('stat-automated-decisions'),
            rate: document.getElementById('stat-automation-rate'),
            daos: document.getElementById('stat-daos-monitored')
        };

        if (els.total) els.total.textContent = this.stats.totalProposals;
        if (els.automated) els.automated.textContent = this.stats.automatedDecisions;
        if (els.rate) els.rate.textContent = `${this.stats.automationRate}%`;
        if (els.daos) els.daos.textContent = this.stats.daosMonitored;
    }

    updateProposalsUI() {
        const container = document.getElementById('proposals-container');
        if (!container) return;

        if (this.proposals.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 4rem; color: var(--text-muted);">
                    <p>No active proposals matching automation criteria</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.proposals.map(proposal => this.createProposalHTML(proposal)).join('');
    }

    createProposalHTML(p) {
        const riskClass = `badge-risk-${p.riskLevel.toLowerCase().substring(0, 3)}`;
        const decisionClass = `decision-${p.decision.replace('auto-', '')}`;
        
        return `
            <div class="proposal-item" onclick="window.open('/proposal/${p.id}', '_blank')">
                <div class="proposal-info">
                    <div class="proposal-dao">${p.dao}</div>
                    <h3>${p.title}</h3>
                </div>
                <div style="text-align: center;">
                    <span class="badge ${riskClass}">${p.riskLevel} RISK</span>
                </div>
                <div style="text-align: center;">
                    <div class="decision-indicator ${decisionClass}">
                        ${p.decision.toUpperCase().replace('AUTO-', '')}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.875rem; color: #fff; font-weight: 700;">${Math.round(p.confidence * 100)}%</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">CONFIDENCE</div>
                </div>
            </div>
        `;
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.agora = new AgoraDashboard();
});
