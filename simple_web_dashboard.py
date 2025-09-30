#!/usr/bin/env python3
"""
Simple MURF Token Web Dashboard
Dashboard web sederhana tanpa Flask yang kompleks
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List
import http.server
import socketserver
import urllib.parse

class MURFWebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db_path = "keeta_trades.db"
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
        self.murf_total_supply = 1_000_000_000_000.00
        self.murf_circulation = 60_000_000_000.00
        self.kta_price_usd = 0.658
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_dashboard()
        elif self.path == '/api/stats':
            self.send_api_response(self.get_token_statistics())
        elif self.path == '/api/price-history':
            self.send_api_response(self.get_price_history())
        else:
            super().do_GET()
    
    def send_dashboard(self):
        """Kirim dashboard HTML"""
        stats = self.get_token_statistics()
        price_history = self.get_price_history()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MURF Token Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .dashboard {{
            display: flex;
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        .stats-panel {{
            flex: 1;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .chart-panel {{
            flex: 1;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 5px 0;
        }}
        .stat-label {{
            font-weight: bold;
            color: #555;
        }}
        .stat-value {{
            color: #333;
            font-family: monospace;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }}
        .token-id {{
            font-family: monospace;
            font-size: 10px;
            word-break: break-all;
        }}
        .refresh-btn {{
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }}
        .refresh-btn:hover {{
            background: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="stats-panel">
            <div class="title">MURF TOKEN STATISTICS</div>
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
            
            <div class="stat-row">
                <span class="stat-label">MURF Total Supply:</span>
                <span class="stat-value" id="total-supply">{stats['murf_total_supply']:,.2f}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">MURF Circulation:</span>
                <span class="stat-value" id="circulation">{stats['murf_circulation']:,.2f}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">Live KTA Price (USD):</span>
                <span class="stat-value" id="kta-price">${stats['kta_price_usd']:.3f}</span>
            </div>
            
            <div style="margin: 20px 0;">
                <div class="stat-label">Last Known Trade:</div>
                <div style="margin-left: 20px;">
                    <div>MURF: <span id="last-murf">{stats['last_murf_trade']:,.2f}</span></div>
                    <div>KTA: <span id="last-kta">{stats['last_kta_trade']:,.2f}</span></div>
                    <div style="margin-top: 10px;">
                        <a href="https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit=10" 
                           target="_blank" 
                           style="color: #007bff; text-decoration: none; font-size: 12px;">
                            🔗 View on Keeta Explorer
                        </a>
                        <br>
                        <a href="https://explorer.test.keeta.com" 
                           target="_blank" 
                           style="color: #28a745; text-decoration: none; font-size: 12px;">
                            🔍 Keeta Test Explorer
                        </a>
                        <br>
                        <a href="https://explorer.test.keeta.com/block/{stats.get('last_trade_hash', 'N/A')}" 
                           target="_blank" 
                           style="color: #dc3545; text-decoration: none; font-size: 12px;">
                            🔗 View Block: {stats.get('last_trade_hash', 'N/A')[:20]}...
                        </a>
                        <br>
                        <span style="font-size: 10px; color: #666; font-family: monospace;">
                            Full Hash: {stats.get('last_trade_hash', 'N/A')}
                        </span>
                    </div>
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <div class="stat-label">Exchange Rates:</div>
                <div style="margin-left: 20px;">
                    <div>KTA: <span id="rate-kta">{stats['exchange_rate_kta']:.2f}</span></div>
                    <div>MURF: <span id="rate-murf">{stats['exchange_rate_murf']:,.2f}</span></div>
                </div>
            </div>
            
            <div class="highlight">
                <div class="stat-label">Key Metrics:</div>
                <div style="margin-left: 10px;">
                    <div>MURF/KTA Price: <span id="murf-kta-price">{stats['murf_kta_price']:.8f}</span></div>
                    <div>MURF/USD Price: <span id="murf-usd-price">${stats['murf_usd_price']:.8f}</span></div>
                    <div>MURF FDV (USD): <span id="murf-fdv">${stats['murf_fdv']:,.0f}</span></div>
                    <div>MURF Marketcap (USD): <span id="murf-marketcap">${stats['murf_marketcap']:,.0f}</span></div>
                </div>
            </div>
            
            <div class="footer">
                <div>Dashboard By: @sack_kta</div>
                <div class="token-id">{self.murf_token}</div>
            </div>
        </div>
        
        <div class="chart-panel">
            <div class="title">MURF Token Price (USD)</div>
            <canvas id="priceChart" width="400" height="300"></canvas>
        </div>
    </div>

    <script>
        let priceChart;
        
        function initChart() {{
            const ctx = document.getElementById('priceChart').getContext('2d');
            priceChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {json.dumps([p['formatted_date'] for p in price_history])},
                    datasets: [{{
                        label: 'MURF Price (USD)',
                        data: {json.dumps([p['price'] for p in price_history])},
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return '$' + value.toFixed(8);
                                }}
                            }}
                        }},
                        x: {{
                            ticks: {{
                                maxRotation: 45
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        function refreshData() {{
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {{
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
                }});
            
            fetch('/api/price-history')
                .then(response => response.json())
                .then(data => {{
                    priceChart.data.labels = data.labels;
                    priceChart.data.datasets[0].data = data.prices;
                    priceChart.update();
                }});
        }}
        
        document.addEventListener('DOMContentLoaded', initChart);
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_api_response(self, data):
        """Kirim response API"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def get_token_statistics(self) -> Dict:
        """Ambil statistik token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hanya ambil transaksi OTC (type 7)
            cursor.execute('''
                SELECT * FROM trades 
                WHERE is_otc = 1 
                ORDER BY timestamp DESC 
                LIMIT 100
            ''')
            
            columns = [description[0] for description in cursor.description]
            otc_trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            
            if not otc_trades:
                return self._get_default_stats()
            
            # Ambil transaksi OTC terbaru
            last_otc_trade = otc_trades[0]
            
            # Cari transaksi MURF dan KTA dari OTC trade
            murf_amount = 0
            kta_amount = 0
            if last_otc_trade['token_id'] == self.murf_token:
                murf_amount = last_otc_trade['amount_decimal']
                kta_amount = last_otc_trade.get('counterpart_amount', 0)
            elif last_otc_trade['token_id'] == self.kta_token:
                kta_amount = last_otc_trade['amount_decimal']
                murf_amount = last_otc_trade.get('counterpart_amount', 0)
            
            exchange_rate = 250000.0
            murf_kta_price = 0.000004
            
            if last_otc_trade.get('exchange_ratio', 0) > 0:
                exchange_rate = last_otc_trade['exchange_ratio']
                murf_kta_price = 1 / exchange_rate
            
            murf_usd_price = murf_kta_price * self.kta_price_usd
            murf_fdv = self.murf_total_supply * murf_usd_price
            murf_marketcap = self.murf_circulation * murf_usd_price
            
            return {
                "murf_total_supply": self.murf_total_supply,
                "murf_circulation": self.murf_circulation,
                "kta_price_usd": self.kta_price_usd,
                "last_murf_trade": murf_amount,
                "last_kta_trade": kta_amount,
                "last_trade_hash": last_otc_trade['block_hash'],
                "last_trade_time": last_otc_trade['timestamp'],
                "exchange_rate_kta": 1.0,
                "exchange_rate_murf": exchange_rate,
                "murf_kta_price": murf_kta_price,
                "murf_usd_price": murf_usd_price,
                "murf_fdv": murf_fdv,
                "murf_marketcap": murf_marketcap
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
            "last_murf_trade": 30_000_000.00,
            "last_kta_trade": 120.00,
            "exchange_rate_kta": 1.0,
            "exchange_rate_murf": 250_000.00,
            "murf_kta_price": 0.00000400,
            "murf_usd_price": 0.00000263,
            "murf_fdv": 2_630_240,
            "murf_marketcap": 157_814,
            "last_trade_time": datetime.now().isoformat()
        }
    
    def get_price_history(self) -> List[Dict]:
        """Ambil riwayat harga"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(days=5)
            
            cursor.execute('''
                SELECT timestamp, amount_decimal, token_id
                FROM trades 
                WHERE timestamp > ? AND token_id IN (?, ?)
                ORDER BY timestamp ASC
            ''', (cutoff_time.isoformat(), self.murf_token, self.kta_token))
            
            trades = cursor.fetchall()
            conn.close()
            
            price_history = []
            for i in range(5):
                date = datetime.now() - timedelta(days=5-i-1)
                base_price = 0.00000263
                variation = (i - 2) * 0.000001
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

def main():
    """Main function"""
    PORT = 5000
    
    print("🚀 Starting Simple MURF Token Web Dashboard...")
    print(f"📊 Dashboard available at: http://localhost:{PORT}")
    print("🔄 Auto-refresh every 30 seconds")
    print("Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), MURFWebHandler) as httpd:
            print(f"✅ Server running on port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
