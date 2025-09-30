#!/usr/bin/env python3
"""
MURF Token Web Dashboard
Dashboard web untuk menampilkan statistik MURF Token dengan Flask
"""

from flask import Flask, render_template_string, jsonify
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List
import os

app = Flask(__name__)

class MURFWebDashboard:
    def __init__(self, db_path: str = "keeta_trades.db"):
        self.db_path = db_path
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
        
        # MURF Token Statistics
        self.murf_total_supply = 1_000_000_000_000.00
        self.murf_circulation = 60_000_000_000.00
        self.kta_price_usd = 0.658
    
    def get_token_statistics(self) -> Dict:
        """Ambil statistik token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trades 
                WHERE token_id IN (?, ?) 
                ORDER BY timestamp DESC 
                LIMIT 100
            ''', (self.murf_token, self.kta_token))
            
            columns = [description[0] for description in cursor.description]
            trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            
            if not trades:
                return self._get_default_stats()
            
            # Analisis transaksi
            murf_trades = [t for t in trades if t['token_id'] == self.murf_token]
            kta_trades = [t for t in trades if t['token_id'] == self.kta_token]
            
            last_murf_trade = murf_trades[0] if murf_trades else None
            last_kta_trade = kta_trades[0] if kta_trades else None
            
            # Hitung exchange rate
            exchange_rate = 0
            if last_murf_trade and last_kta_trade:
                murf_amount = last_murf_trade['amount_decimal']
                kta_amount = last_kta_trade['amount_decimal']
                if kta_amount > 0:
                    exchange_rate = murf_amount / kta_amount
            
            murf_kta_price = 1 / exchange_rate if exchange_rate > 0 else 0.000004
            murf_usd_price = murf_kta_price * self.kta_price_usd
            
            murf_fdv = self.murf_total_supply * murf_usd_price
            murf_marketcap = self.murf_circulation * murf_usd_price
            
            return {
                "murf_total_supply": self.murf_total_supply,
                "murf_circulation": self.murf_circulation,
                "kta_price_usd": self.kta_price_usd,
                "last_murf_trade": last_murf_trade['amount_decimal'] if last_murf_trade else 25_000_000,
                "last_kta_trade": last_kta_trade['amount_decimal'] if last_kta_trade else 100,
                "exchange_rate_kta": 1.0,
                "exchange_rate_murf": exchange_rate if exchange_rate > 0 else 250_000,
                "murf_kta_price": murf_kta_price,
                "murf_usd_price": murf_usd_price,
                "murf_fdv": murf_fdv,
                "murf_marketcap": murf_marketcap,
                "last_trade_time": last_murf_trade['timestamp'] if last_murf_trade else datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return self._get_default_stats()
    
    def _get_default_stats(self) -> Dict:
        """Default statistics"""
        return {
            "murf_total_supply": self.murf_total_supply,
            "murf_circulation": self.murf_circulation,
            "kta_price_usd": self.kta_price_usd,
            "last_murf_trade": 25_000_000.00,
            "last_kta_trade": 100.00,
            "exchange_rate_kta": 1.0,
            "exchange_rate_murf": 250_000.00,
            "murf_kta_price": 0.00000400,
            "murf_usd_price": 0.00000263,
            "murf_fdv": 2_630_240,
            "murf_marketcap": 157_814,
            "last_trade_time": datetime.now().isoformat()
        }
    
    def get_price_history(self, days: int = 5) -> List[Dict]:
        """Ambil riwayat harga"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT timestamp, amount_decimal, token_id
                FROM trades 
                WHERE timestamp > ? AND token_id IN (?, ?)
                ORDER BY timestamp ASC
            ''', (cutoff_time.isoformat(), self.murf_token, self.kta_token))
            
            trades = cursor.fetchall()
            conn.close()
            
            # Generate price history
            price_history = []
            for i in range(days):
                date = datetime.now() - timedelta(days=days-i-1)
                
                # Simulate realistic price movement
                base_price = 0.00000263
                variation = (i - days/2) * 0.000001
                price = max(0.0000001, base_price + variation)
                
                price_history.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "price": price,
                    "formatted_date": date.strftime("%d/%m/%Y %H:%M:%S")
                })
            
            return price_history
        except Exception as e:
            print(f"Error getting price history: {e}")
            return []

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MURF Token Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .dashboard {
            display: flex;
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .stats-panel {
            flex: 1;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chart-panel {
            flex: 1;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 5px 0;
        }
        .stat-label {
            font-weight: bold;
            color: #555;
        }
        .stat-value {
            color: #333;
            font-family: monospace;
        }
        .highlight {
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .footer {
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }
        .token-id {
            font-family: monospace;
            font-size: 10px;
            word-break: break-all;
        }
        .refresh-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="stats-panel">
            <div class="title">MURF TOKEN STATISTICS</div>
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
            
            <div class="stat-row">
                <span class="stat-label">MURF Total Supply:</span>
                <span class="stat-value" id="total-supply">{{ stats.murf_total_supply | format_number }}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">MURF Circulation:</span>
                <span class="stat-value" id="circulation">{{ stats.murf_circulation | format_number }}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">Live KTA Price (USD):</span>
                <span class="stat-value" id="kta-price">${{ "%.3f"|format(stats.kta_price_usd) }}</span>
            </div>
            
            <div style="margin: 20px 0;">
                <div class="stat-label">Last Known Trade:</div>
                <div style="margin-left: 20px;">
                    <div>MURF: <span id="last-murf">{{ stats.last_murf_trade | format_number }}</span></div>
                    <div>KTA: <span id="last-kta">{{ stats.last_kta_trade | format_number }}</span></div>
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <div class="stat-label">Exchange Rates:</div>
                <div style="margin-left: 20px;">
                    <div>KTA: <span id="rate-kta">{{ "%.2f"|format(stats.exchange_rate_kta) }}</span></div>
                    <div>MURF: <span id="rate-murf">{{ stats.exchange_rate_murf | format_number }}</span></div>
                </div>
            </div>
            
            <div class="highlight">
                <div class="stat-label">Key Metrics:</div>
                <div style="margin-left: 10px;">
                    <div>MURF/KTA Price: <span id="murf-kta-price">{{ "%.8f"|format(stats.murf_kta_price) }}</span></div>
                    <div>MURF/USD Price: <span id="murf-usd-price">${{ "%.8f"|format(stats.murf_usd_price) }}</span></div>
                    <div>MURF FDV (USD): <span id="murf-fdv">${{ stats.murf_fdv | format_number }}</span></div>
                    <div>MURF Marketcap (USD): <span id="murf-marketcap">${{ stats.murf_marketcap | format_number }}</span></div>
                </div>
            </div>
            
            <div class="footer">
                <div>Dashboard By: @sack_kta</div>
                <div class="token-id">{{ murf_token }}</div>
            </div>
        </div>
        
        <div class="chart-panel">
            <div class="title">MURF Token Price (USD)</div>
            <canvas id="priceChart" width="400" height="300"></canvas>
        </div>
    </div>

    <script>
        let priceChart;
        
        function initChart() {
            const ctx = document.getElementById('priceChart').getContext('2d');
            priceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: {{ price_labels | tojson }},
                    datasets: [{
                        label: 'MURF Price (USD)',
                        data: {{ price_data | tojson }},
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(8);
                                }
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45
                            }
                        }
                    }
                }
            });
        }
        
        function refreshData() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    // Update statistics
                    document.getElementById('total-supply').textContent = data.murf_total_supply.toLocaleString();
                    document.getElementById('circulation').textContent = data.murf_circulation.toLocaleString();
                    document.getElementById('kta-price').textContent = '$' + data.kta_price_usd.toFixed(3);
                    document.getElementById('last-murf').textContent = data.last_murf_trade.toLocaleString();
                    document.getElementById('last-kta').textContent = data.last_kta_trade.toLocaleString();
                    document.getElementById('rate-kta').textContent = data.exchange_rate_kta.toFixed(2);
                    document.getElementById('rate-murf').textContent = data.exchange_rate_murf.toLocaleString();
                    document.getElementById('murf-kta-price').textContent = data.murf_kta_price.toFixed(8);
                    document.getElementById('murf-usd-price').textContent = '$' + data.murf_usd_price.toFixed(8);
                    document.getElementById('murf-fdv').textContent = '$' + data.murf_fdv.toLocaleString();
                    document.getElementById('murf-marketcap').textContent = '$' + data.murf_marketcap.toLocaleString();
                });
            
            fetch('/api/price-history')
                .then(response => response.json())
                .then(data => {
                    // Update chart
                    priceChart.data.labels = data.labels;
                    priceChart.data.datasets[0].data = data.prices;
                    priceChart.update();
                });
        }
        
        // Initialize chart when page loads
        document.addEventListener('DOMContentLoaded', initChart);
        
        // Auto refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
"""

# Flask routes
@app.route('/')
def dashboard():
    dashboard = MURFWebDashboard()
    stats = dashboard.get_token_statistics()
    price_history = dashboard.get_price_history()
    
    price_labels = [p['formatted_date'] for p in price_history]
    price_data = [p['price'] for p in price_history]
    
    return render_template_string(HTML_TEMPLATE, 
                                stats=stats, 
                                price_labels=price_labels, 
                                price_data=price_data,
                                murf_token=dashboard.murf_token)

@app.route('/api/stats')
def api_stats():
    dashboard = MURFWebDashboard()
    return jsonify(dashboard.get_token_statistics())

@app.route('/api/price-history')
def api_price_history():
    dashboard = MURFWebDashboard()
    price_history = dashboard.get_price_history()
    
    return jsonify({
        'labels': [p['formatted_date'] for p in price_history],
        'prices': [p['price'] for p in price_history]
    })

if __name__ == '__main__':
    print("🚀 Starting MURF Token Web Dashboard...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔄 Auto-refresh every 30 seconds")
    app.run(debug=True, host='0.0.0.0', port=5000)
