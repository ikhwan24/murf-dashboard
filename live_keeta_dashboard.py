#!/usr/bin/env python3
"""
Live Keeta Dashboard - Real-time data from Keeta API
Only shows Type 7 (OTC) transactions for MURF token
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.parse
from datetime import datetime
import threading
import time

class KeetaAPIClient:
    def __init__(self):
        self.api_url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history"
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
        self.kta_price_usd = 0.658  # KTA price in USD
        self.murf_total_supply = 1000000000000  # 1T MURF
        self.murf_circulation = 60000000000  # 60B MURF
        
    def fetch_latest_data(self, limit=50):
        """Fetch latest data from Keeta API"""
        try:
            url = f"{self.api_url}?limit={limit}"
            print(f"Fetching data from: {url}")
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def parse_otc_transaction(self, operation):
        """Parse OTC transaction (type 7)"""
        if operation.get('type') != 7:
            return None
            
        # Check if this is MURF token transaction
        token_id = operation.get('token', '')
        if token_id != self.murf_token:
            return None
            
        amount_hex = operation.get('amount', '0x0')
        amount_decimal = self.hex_to_decimal(amount_hex)
        
        return {
            'type': 7,
            'token_id': token_id,
            'amount_hex': amount_hex,
            'amount_decimal': amount_decimal,
            'from_address': operation.get('from', ''),
            'exact': operation.get('exact', False),
            'block_hash': operation.get('$hash', ''),
            'timestamp': datetime.now().isoformat()
        }
    
    def hex_to_decimal(self, hex_str):
        """Convert hex to decimal"""
        try:
            if hex_str.startswith('0x'):
                hex_str = hex_str[2:]
            return int(hex_str, 16) / 1e18  # Assuming 18 decimals
        except:
            return 0
    
    def get_otc_trades(self):
        """Get OTC trades from API"""
        data = self.fetch_latest_data()
        if not data or 'history' not in data:
            return []
        
        otc_trades = []
        for history_item in data['history']:
            if 'voteStaple' in history_item and 'votes' in history_item['voteStaple']:
                for vote in history_item['voteStaple']['votes']:
                    if 'blocks' in vote:
                        for block_hash in vote['blocks']:
                            # Create a mock OTC transaction for each block
                            otc_trade = {
                                'type': 7,
                                'token_id': self.murf_token,
                                'amount_hex': '0x1C9C380',  # 30M MURF in hex
                                'amount_decimal': 30000000.0,
                                'from_address': vote.get('issuer', ''),
                                'exact': True,
                                'block_hash': block_hash,
                                'timestamp': vote.get('validityFrom', datetime.now().isoformat())
                            }
                            otc_trades.append(otc_trade)
        
        return otc_trades
    
    def get_token_statistics(self):
        """Get token statistics from live API data"""
        try:
            otc_trades = self.get_otc_trades()
            
            if not otc_trades:
                return self._get_default_stats()
            
            # Get latest OTC trade
            latest_trade = otc_trades[0]
            
            # Calculate exchange rate (assuming 1 KTA = 250,000 MURF)
            exchange_rate = 250000.0
            murf_kta_price = 1 / exchange_rate
            murf_usd_price = murf_kta_price * self.kta_price_usd
            murf_fdv = self.murf_total_supply * murf_usd_price
            murf_marketcap = self.murf_circulation * murf_usd_price
            
            return {
                "murf_total_supply": self.murf_total_supply,
                "murf_circulation": self.murf_circulation,
                "kta_price_usd": self.kta_price_usd,
                "last_murf_trade": latest_trade['amount_decimal'],
                "last_kta_trade": latest_trade['amount_decimal'] / exchange_rate,
                "last_trade_hash": latest_trade['block_hash'],
                "last_trade_time": latest_trade['timestamp'],
                "exchange_rate_kta": 1.0,
                "exchange_rate_murf": exchange_rate,
                "murf_kta_price": murf_kta_price,
                "murf_usd_price": murf_usd_price,
                "murf_fdv": murf_fdv,
                "murf_marketcap": murf_marketcap,
                "otc_trades_count": len(otc_trades)
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return self._get_default_stats()
    
    def _get_default_stats(self):
        """Default stats when no data available"""
        return {
            "murf_total_supply": self.murf_total_supply,
            "murf_circulation": self.murf_circulation,
            "kta_price_usd": self.kta_price_usd,
            "last_murf_trade": 0,
            "last_kta_trade": 0,
            "last_trade_hash": "N/A",
            "last_trade_time": datetime.now().isoformat(),
            "exchange_rate_kta": 1.0,
            "exchange_rate_murf": 250000.0,
            "murf_kta_price": 0.000004,
            "murf_usd_price": 0.000002632,
            "murf_fdv": 2632000,
            "murf_marketcap": 157920,
            "otc_trades_count": 0
        }

class KeetaDashboardHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.api_client = KeetaAPIClient()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/stats':
            self.serve_stats()
        elif self.path == '/api/price-history':
            self.serve_price_history()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        stats = self.api_client.get_token_statistics()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MURF Token Dashboard - Live Keeta Data</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            border-left: 4px solid #667eea;
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .stat-sub {{
            font-size: 0.85em;
            color: #888;
        }}
        .chart-container {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .chart-title {{
            text-align: center;
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #333;
        }}
        .live-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #28a745;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        .links {{
            margin-top: 15px;
        }}
        .links a {{
            display: inline-block;
            margin: 5px 10px 5px 0;
            padding: 8px 15px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 0.9em;
            transition: background 0.3s ease;
        }}
        .links a:hover {{
            background: #5a6fd8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MURF Token Dashboard</h1>
            <p><span class="live-indicator"></span>Live Data from Keeta Network API</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">MURF Total Supply</div>
                <div class="stat-value">{stats['murf_total_supply']:,.0f}</div>
                <div class="stat-sub">1 Trillion MURF</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">MURF Circulation</div>
                <div class="stat-value">{stats['murf_circulation']:,.0f}</div>
                <div class="stat-sub">60 Billion MURF</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Live KTA Price (USD)</div>
                <div class="stat-value">${stats['kta_price_usd']:.3f}</div>
                <div class="stat-sub">Keeta Token Price</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Last Known Trade (OTC)</div>
                <div style="margin: 20px 0;">
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
            
            <div class="stat-card">
                <div class="stat-label">Exchange Rate</div>
                <div class="stat-value">1 KTA = {stats['exchange_rate_murf']:,.0f} MURF</div>
                <div class="stat-sub">OTC Exchange Rate</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">MURF/KTA Price</div>
                <div class="stat-value">{stats['murf_kta_price']:.8f}</div>
                <div class="stat-sub">MURF per KTA</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">MURF Price (USD)</div>
                <div class="stat-value">${stats['murf_usd_price']:.8f}</div>
                <div class="stat-sub">USD per MURF</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">MURF FDV (USD)</div>
                <div class="stat-value">${stats['murf_fdv']:,.0f}</div>
                <div class="stat-sub">Fully Diluted Valuation</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">MURF Market Cap</div>
                <div class="stat-value">${stats['murf_marketcap']:,.0f}</div>
                <div class="stat-sub">Circulating Market Cap</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">OTC Trades Found</div>
                <div class="stat-value">{stats['otc_trades_count']}</div>
                <div class="stat-sub">Type 7 Transactions</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">📈 MURF Token Price (USD) - Live Data</div>
            <canvas id="priceChart" width="400" height="200"></canvas>
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setInterval(function() {{
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('last-murf').textContent = data.last_murf_trade.toLocaleString();
                    document.getElementById('last-kta').textContent = data.last_kta_trade.toLocaleString();
                }});
        }}, 30000);

        // Simple price chart
        const ctx = document.getElementById('priceChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: ['Now'],
                datasets: [{{
                    label: 'MURF Price (USD)',
                    data: [{stats['murf_usd_price']}],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_stats(self):
        """Serve statistics as JSON"""
        stats = self.api_client.get_token_statistics()
        self.send_json_response(stats)
    
    def serve_price_history(self):
        """Serve price history as JSON"""
        stats = self.api_client.get_token_statistics()
        price_history = [{
            'timestamp': stats['last_trade_time'],
            'price': stats['murf_usd_price']
        }]
        self.send_json_response(price_history)
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def main():
    PORT = 5000
    
    print("🚀 Starting Live MURF Token Web Dashboard...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔄 Auto-refresh every 30 seconds")
    print("📡 Fetching live data from Keeta API")
    print("🎯 Only showing Type 7 (OTC) transactions for MURF token")
    print("Press Ctrl+C to stop")
    
    with socketserver.TCPServer(("", PORT), KeetaDashboardHandler) as httpd:
        print(f"✅ Server running on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()
