class VolumeAnalyzer {
    constructor() {
        this.chart = null;
        this.currentTicker = 'RELIANCE.NS';
        this.init();
    }
    
    init() {
        this.createVolumeContainer();
        this.loadVolumeData();
    }
    
    createVolumeContainer() {
        const volumeHTML = `
            <div class="volume-analyzer-container" id="volumeAnalyzer">
                <div class="volume-header">
                    <h3>📈 Volume Analysis</h3>
                    <select id="volumeTickerSelect" class="ticker-select">
                        <option value="RELIANCE.NS">Reliance</option>
                        <option value="TCS.NS">TCS</option>
                        <option value="HDFCBANK.NS">HDFC Bank</option>
                        <option value="INFY.NS">Infosys</option>
                        <option value="SBIN.NS">SBI</option>
                    </select>
                    <button id="refreshVolume" class="refresh-btn">🔄</button>
                </div>
                
                <div class="volume-metrics" id="volumeMetrics">
                    <div class="metric-card">
                        <div class="metric-label">Current Volume</div>
                        <div class="metric-value" id="currentVolume">--</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Avg Volume (20d)</div>
                        <div class="metric-value" id="avgVolume">--</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Volume Ratio</div>
                        <div class="metric-value" id="volumeRatio">--</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Signal</div>
                        <div class="metric-value" id="volumeSignal">--</div>
                    </div>
                </div>
                
                <div class="volume-chart-container">
                    <canvas id="volumeChart" width="400" height="200"></canvas>
                </div>
                
                <div class="volume-insights" id="volumeInsights">
                    <div class="insight-item">
                        <span class="insight-label">Trend:</span>
                        <span class="insight-value" id="volumeTrend">--</span>
                    </div>
                    <div class="insight-item">
                        <span class="insight-label">Strength:</span>
                        <span class="insight-value" id="volumeStrength">--</span>
                    </div>
                    <div class="insight-item">
                        <span class="insight-label">Price-Volume:</span>
                        <span class="insight-value" id="priceVolumeRelation">--</span>
                    </div>
                </div>
            </div>
        `;
        
        const dashboard = document.querySelector('.dashboard-container') || document.body;
        dashboard.insertAdjacentHTML('beforeend', volumeHTML);
        
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        document.getElementById('volumeTickerSelect').addEventListener('change', (e) => {
            this.currentTicker = e.target.value;
            this.loadVolumeData();
        });
        
        document.getElementById('refreshVolume').addEventListener('click', () => {
            this.loadVolumeData();
        });
    }
    
    async loadVolumeData() {
        try {
            const response = await fetch(`/volume-analysis/${this.currentTicker}`);
            const data = await response.json();
            
            if (data.volume_analysis) {
                this.updateVolumeMetrics(data.volume_analysis);
                this.updateVolumeInsights(data.volume_analysis);
                this.createVolumeChart(data.volume_analysis);
            }
            
        } catch (error) {
            console.error('Volume analysis error:', error);
        }
    }
    
    updateVolumeMetrics(analysis) {
        document.getElementById('currentVolume').textContent = 
            analysis.current_volume ? analysis.current_volume.toLocaleString() : '--';
        
        document.getElementById('avgVolume').textContent = 
            analysis.avg_volume_20d ? analysis.avg_volume_20d.toLocaleString() : '--';
        
        document.getElementById('volumeRatio').textContent = 
            analysis.volume_ratio ? `${analysis.volume_ratio}x` : '--';
        
        const signalElement = document.getElementById('volumeSignal');
        signalElement.textContent = analysis.signal || '--';
        signalElement.className = `metric-value ${this.getSignalClass(analysis.strength)}`;
    }
    
    updateVolumeInsights(analysis) {
        document.getElementById('volumeTrend').textContent = 
            `${analysis.trend || '--'} (${analysis.trend_strength || 0}%)`;
        
        document.getElementById('volumeStrength').textContent = analysis.strength || '--';
        
        document.getElementById('priceVolumeRelation').textContent = 
            `${analysis.pv_relationship || '--'} (${analysis.conviction || '--'} conviction)`;
    }
    
    getSignalClass(strength) {
        switch(strength) {
            case 'Extremely High':
            case 'High':
                return 'bullish';
            case 'Low':
                return 'bearish';
            default:
                return 'neutral';
        }
    }
    
    createVolumeChart(analysis) {
        const canvas = document.getElementById('volumeChart');
        const ctx = canvas.getContext('2d');
        
        // Simple bar chart for volume comparison
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const currentVol = analysis.current_volume || 0;
        const avgVol = analysis.avg_volume_20d || 1;
        const maxVol = Math.max(currentVol, avgVol) * 1.2;
        
        // Draw bars
        const barWidth = 60;
        const barSpacing = 100;
        const chartHeight = 150;
        const baseY = canvas.height - 30;
        
        // Average volume bar
        const avgHeight = (avgVol / maxVol) * chartHeight;
        ctx.fillStyle = '#6c757d';
        ctx.fillRect(50, baseY - avgHeight, barWidth, avgHeight);
        
        // Current volume bar
        const currentHeight = (currentVol / maxVol) * chartHeight;
        ctx.fillStyle = currentVol > avgVol ? '#28a745' : '#dc3545';
        ctx.fillRect(50 + barSpacing, baseY - currentHeight, barWidth, currentHeight);
        
        // Labels
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Avg (20d)', 50 + barWidth/2, baseY + 15);
        ctx.fillText('Current', 50 + barSpacing + barWidth/2, baseY + 15);
        
        // Volume ratio indicator
        ctx.fillStyle = analysis.volume_ratio > 1.5 ? '#28a745' : analysis.volume_ratio < 0.8 ? '#dc3545' : '#ffc107';
        ctx.fillRect(canvas.width - 80, 20, 60, 20);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${analysis.volume_ratio}x`, canvas.width - 50, 35);
    }
}

// Initialize Volume Analyzer when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.volumeAnalyzer = new VolumeAnalyzer();
});
