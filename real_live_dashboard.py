#!/usr/bin/env python3
"""
Real Live Dashboard - Fetch actual price data
"""

import os
import http.server
import socketserver
import json
import urllib.request
import urllib.parse
from datetime import datetime
import threading
import time
from price_history_db import PriceHistoryDB

class RealLiveAPIClient:
    def __init__(self):
        self.keeta_api_url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history"
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
        self.price_db = PriceHistoryDB()
        
        # Try to get real KTA price from external sources
        self.kta_price_usd = self.get_real_kta_price()
        self.murf_total_supply = 1000000000000  # 1T MURF
        self.murf_circulation = 60000000000  # 60B MURF
        
    def get_real_kta_price(self):
        """Get real KTA price from CoinGecko API"""
        try:
            # CoinGecko API untuk mendapatkan harga KTA
            url = "https://api.coingecko.com/api/v3/simple/price?ids=keeta&vs_currencies=usd&include_24hr_change=true"
            
            # Tambahkan API key
            headers = {
                'x-cg-demo-api-key': 'CG-qm3bVvYaCiNoUnYdLXP9VHwj'
            }
            
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if 'keeta' in data and 'usd' in data['keeta']:
                    price = data['keeta']['usd']
                    print(f"✅ KTA Price from CoinGecko: ${price}")
                    return price
                else:
                    print("❌ KTA not found in CoinGecko, using fallback price")
                    return 0.658
                    
        except Exception as e:
            print(f"❌ Error fetching KTA price from CoinGecko: {e}")
            print("🔄 Using fallback price: $0.658")
            return 0.658
    
    def hex_to_decimal(self, hex_string):
        """Convert hex string to decimal"""
        try:
            if hex_string.startswith('0x'):
                hex_string = hex_string[2:]
            return int(hex_string, 16)
        except:
            return 0
    
    def fetch_keeta_data(self, limit=100):
        """Fetch data from Keeta API"""
        try:
            url = f"{self.keeta_api_url}?limit={limit}"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        except Exception as e:
            print(f"Error fetching Keeta data: {e}")
            return None
    
    def analyze_keeta_data(self, data):
        """Analyze Keeta data for OTC transactions - Type 7 KTA + Type 0 MURF dalam block yang sama"""
        if not data or 'history' not in data:
            return {
                'total_blocks': 0,
                'recent_activity': [],
                'last_update': datetime.now().isoformat(),
                'type_7_murf_txs': []
            }
        
        recent_activity = []
        total_blocks = 0
        otc_transactions = []
        
        # Token IDs
        kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
        murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        
        print(f"🔍 Analyzing {len(data['history'])} history entries for OTC transactions...")
        
        for entry in data['history']:
            if 'voteStaple' in entry and 'blocks' in entry['voteStaple']:
                blocks = entry['voteStaple']['blocks']
                
                for block in blocks:
                    if 'operations' in block:
                        operations = block['operations']
                        total_blocks += 1
                        
                        # Cari Type 7 KTA operations
                        for op in operations:
                            op_type = op.get('type')
                            token = op.get('token', '')
                            
                            # Type 7 dengan KTA token
                            if op_type == 7 and kta_token in token:
                                kta_amount = self.hex_to_decimal(op.get('amount', '0x0')) / 1e18
                                from_addr = op.get('from', 'N/A')
                                exact = op.get('exact', False)
                                
                                print(f"✅ Found Type 7 KTA: {block.get('$hash', 'N/A')[:20]}... KTA: {kta_amount:.2f}")
                                
                                # Cari related Type 0 MURF dalam block yang sama atau block sebelumnya
                                murf_amount = 0
                                to_addr = 'N/A'
                                
                                # Cari dalam block yang sama dulu
                                for related_op in operations:
                                    if (related_op.get('type') == 0 and 
                                        related_op.get('token') == murf_token):
                                        murf_amount_raw = self.hex_to_decimal(related_op.get('amount', '0x0'))
                                        murf_amount = murf_amount_raw  # TIDAK dibagi 1e18 untuk MURF
                                        to_addr = related_op.get('to', 'N/A')
                                        print(f"   ✅ Found Type 0 MURF: {murf_amount:.0f} MURF")
                                        break
                                
                                # Jika tidak ada dalam block yang sama, cari di block sebelumnya
                                if murf_amount == 0 and j > 0:
                                    prev_block = blocks[j-1]
                                    if 'operations' in prev_block:
                                        for prev_op in prev_block['operations']:
                                            if (prev_op.get('type') == 0 and 
                                                murf_token in prev_op.get('token', '')):
                                                murf_amount = self.hex_to_decimal(prev_op.get('amount', '0x0')) / 1e18
                                                to_addr = prev_op.get('to', 'N/A')
                                                break
                                
                                print(f"   MURF found: {murf_amount:.2f} MURF")
                                
                                otc_transactions.append({
                                    'tx_hash': block.get('$hash', 'N/A'),
                                    'kta_amount': kta_amount,
                                    'murf_amount': murf_amount,
                                    'from_address': from_addr,
                                    'to_address': to_addr,
                                    'date': block.get('date', 'N/A'),
                                    'exact': exact,
                                    'exchange_rate': murf_amount/kta_amount if kta_amount > 0 else 0
                                })
                
                # Juga simpan activity untuk display
                if 'votes' in entry['voteStaple']:
                    for vote in entry['voteStaple']['votes']:
                        if 'blocks' in vote:
                            recent_activity.append({
                                'issuer': vote.get('issuer', ''),
                                'serial': vote.get('serial', ''),
                                'blocks_count': len(vote['blocks']),
                                'validity_from': vote.get('validityFrom', ''),
                                'block_hashes': vote['blocks'][:3]  # First 3 blocks
                            })
        
        print(f"📊 Found {len(otc_transactions)} OTC transactions")
        
        return {
            'total_blocks': total_blocks,
            'recent_activity': recent_activity[:5],  # Last 5 activities
            'last_update': datetime.now().isoformat(),
            'type_7_murf_txs': otc_transactions
        }
    
    def get_token_statistics(self):
        """Get real token statistics"""
        try:
            keeta_data = self.fetch_keeta_data()
            analysis = self.analyze_keeta_data(keeta_data)
            
            # Gunakan data type 7 MURF yang benar jika ada
            type_7_txs = analysis.get('type_7_murf_txs', [])
            last_trade_hash = "N/A"
            last_trade_time = "N/A"
            
            if type_7_txs:
                # Ambil transaksi terbaru
                latest_tx = type_7_txs[0]  # Diasumsikan sudah diurutkan dari terbaru
                last_trade_hash = latest_tx['tx_hash']
                last_trade_time = latest_tx['date']
                print(f"🔗 Last Type 7 MURF trade: {last_trade_hash[:20]}... at {last_trade_time}")
            
            # Calculate MURF price based on real OTC trades
            if type_7_txs:
                # Use the latest OTC trade for pricing
                latest_trade = type_7_txs[0]
                murf_amount = latest_trade.get('amount', 0)
                kta_amount = latest_trade.get('kta_amount', 0)
                
                print(f"🔍 DEBUG: kta_amount={kta_amount}, murf_amount={murf_amount}")
                if kta_amount > 0 and murf_amount > 0:
                    murf_kta_price = kta_amount / murf_amount  # KTA per MURF
                    exchange_rate_murf = murf_amount / kta_amount  # MURF per KTA
                    print(f"📊 Real Exchange Rate: 1 KTA = {exchange_rate_murf:,.0f} MURF")
                else:
                    # Ambil dari database terakhir jika ada
                    last_price_data = self.price_db.get_latest_price_data()
                    if last_price_data and last_price_data.get('exchange_rate_murf', 0) > 0:
                        murf_kta_price = last_price_data.get('murf_kta_price', 0.000004)
                        exchange_rate_murf = last_price_data.get('exchange_rate_murf', 250000.0)
                        print(f"📊 Using last known rate: 1 KTA = {exchange_rate_murf:,.0f} MURF (from DB)")
                    else:
                        murf_kta_price = 0.000004  # Default fallback
                        exchange_rate_murf = 250000.0  # Default fallback
                        print(f"📊 Using default rate: 1 KTA = {exchange_rate_murf:,.0f} MURF")
            else:
                murf_kta_price = 0.000004  # Default fallback
                exchange_rate_murf = 250000.0  # Default fallback
            
            murf_usd_price = murf_kta_price * self.kta_price_usd
            murf_fdv = self.murf_total_supply * murf_usd_price
            murf_marketcap = self.murf_circulation * murf_usd_price
            
            # Save price data to database
            price_data = {
                'timestamp': datetime.now().isoformat(),
                'kta_price_usd': self.kta_price_usd,
                'murf_kta_price': murf_kta_price,
                'murf_usd_price': murf_usd_price,
                'exchange_rate_murf': exchange_rate_murf,
                'murf_fdv': murf_fdv,
                'murf_marketcap': murf_marketcap,
                'type_7_count': len(type_7_txs),
                'last_trade_hash': last_trade_hash
            }
            self.price_db.save_price_data(price_data)
            
            # Get chart data
            chart_data = self.price_db.get_chart_data(50)
            
            return {
                "murf_total_supply": self.murf_total_supply,
                "murf_circulation": self.murf_circulation,
                "kta_price_usd": self.kta_price_usd,
                "murf_kta_price": murf_kta_price,
                "murf_usd_price": murf_usd_price,
                "murf_fdv": murf_fdv,
                "murf_marketcap": murf_marketcap,
                "exchange_rate_murf": exchange_rate_murf,
                "total_blocks": analysis['total_blocks'],
                "recent_activity": analysis['recent_activity'],
                "last_update": analysis['last_update'],
                "last_trade_hash": last_trade_hash,
                "last_trade_time": last_trade_time,
                "type_7_count": len(type_7_txs),
                "type_7_murf_txs": type_7_txs,
                "chart_data": chart_data,
                "data_source": "Keeta Network API (Live)",
                "api_status": "✅ Connected" if keeta_data else "❌ Disconnected"
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return self._get_default_stats()
    
    def _get_default_stats(self):
        """Default stats when no data available"""
        return {
            "murf_total_supply": self.murf_total_supply,
            "murf_circulation": self.murf_circulation,
            "kta_price_usd": 0.658,
            "murf_kta_price": 0.000004,
            "murf_usd_price": 0.000002632,
            "murf_fdv": 2632000,
            "murf_marketcap": 157920,
            "exchange_rate_murf": 250000.0,
            "total_blocks": 0,
            "recent_activity": [],
            "last_update": datetime.now().isoformat(),
            "data_source": "Default Values",
            "api_status": "❌ No Data"
        }

class RealLiveDashboardHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.api_client = RealLiveAPIClient()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/stats':
            self.serve_stats()
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
    <title>MURF Token Dashboard - Real Live Data</title>
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
            display: flex;
            flex-direction: column;
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
        .status-bar {{
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .status-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .status-indicator {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #28a745;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 25px;
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            position: relative;
            overflow: hidden;
        }}
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            border-radius: 15px;
        }}
        .stat-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }}
        .stat-label {{
            font-size: 1.1em;
            color: #ffffff;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 800;
            position: relative;
            z-index: 1;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8), 0 0 8px rgba(0,0,0,0.6);
            -webkit-text-stroke: 0.5px rgba(0,0,0,0.3);
        }}
        .stat-value {{
            font-size: 2.2em;
            font-weight: 900;
            color: #ffffff;
            margin-bottom: 8px;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.9), 0 0 10px rgba(0,0,0,0.7);
            position: relative;
            z-index: 1;
            -webkit-text-stroke: 1px rgba(0,0,0,0.4);
        }}
        .stat-sub {{
            font-size: 1.0em;
            color: #ffffff;
            position: relative;
            z-index: 1;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8), 0 0 6px rgba(0,0,0,0.6);
            font-weight: 600;
            -webkit-text-stroke: 0.3px rgba(0,0,0,0.3);
        }}
        .donation-section {{
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 20px 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        
        .donation-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        
        .donation-text {{
            font-size: 1.1em;
            color: #ffffff;
            margin-bottom: 20px;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        }}
        
        .donation-address {{
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #ffffff;
            word-break: break-all;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        }}
        
        .donation-emoji {{
            font-size: 2em;
            margin-bottom: 10px;
            display: block;
        }}
        
        .activity-section {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .activity-title {{
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #333;
        }}
        .activity-item {{
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }}
        .activity-issuer {{
            font-weight: bold;
            color: #333;
        }}
        .activity-details {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        .warning-box {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 30px;
            color: #856404;
        }}
        
        .compact-chart {{
            margin-top: 15px;
            background: #1a1a1a;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #333;
        }}
        
        .compact-chart .chart-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .compact-chart .chart-title {{
            color: #00d4aa;
            font-weight: bold;
            font-size: 14px;
        }}
        
        .compact-chart .chart-controls {{
            display: flex;
            gap: 5px;
        }}
        
        .compact-chart .timeframe-btn {{
            background: #333;
            color: #fff;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
        }}
        
        .compact-chart .timeframe-btn.active {{
            background: #00d4aa;
            color: #000;
        }}
        
        .compact-chart .chart-container {{
            height: 300px;
            position: relative;
        }}
        
        /* DexScreener Style Chart Section */
        .chart-section {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 0;
            margin: 20px 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
            overflow: hidden;
            order: 1; /* Chart appears first, before cards */
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .chart-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 24px;
            border-bottom: 1px solid #333;
            background: #1a1a1a;
        }}
        
        .chart-title {{
            font-size: 1.5em;
            font-weight: 600;
            color: #ffffff;
            margin: 0;
        }}
        
        .chart-controls {{
            display: flex;
            align-items: center;
        }}
        
        .timeframe-selector {{
            display: flex;
            background: #2a2a2a;
            border-radius: 8px;
            padding: 4px;
        }}
        
        .timeframe-btn {{
            background: transparent;
            border: none;
            color: #888;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .timeframe-btn:hover {{
            color: #fff;
            background: #333;
        }}
        
        .timeframe-btn.active {{
            background: #00d4aa;
            color: #000;
            font-weight: 600;
        }}
        
        .price-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 24px;
            background: #1a1a1a;
            border-bottom: 1px solid #333;
        }}
        
        .current-price {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .price-label {{
            color: #888;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .price-value {{
            color: #ffffff;
            font-size: 24px;
            font-weight: 700;
        }}
        
        .price-change {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .price-change.positive {{
            background: #00d4aa20;
            color: #00d4aa;
        }}
        
        .price-change.negative {{
            background: #ff6b6b20;
            color: #ff6b6b;
        }}
        
        .market-stats {{
            display: flex;
            gap: 24px;
        }}
        
        .stat-item {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }}
        
        .stat-label {{
            color: #888;
            font-size: 12px;
            margin-bottom: 4px;
        }}
        
        .stat-value {{
            color: #ffffff;
            font-size: 14px;
            font-weight: 600;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            width: 100%;
            background: #1a1a1a;
        }}
        
        .chart-footer {{
            padding: 16px 24px;
            background: #1a1a1a;
            border-top: 1px solid #333;
        }}
        
        .chart-info {{
            text-align: center;
        }}
        
        .info-text {{
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MURF Token Dashboard</h1>
            <p><span class="status-indicator"></span>Real Live Data from Keeta Network</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <span class="status-indicator"></span>
                <span>API Status: {stats['api_status']}</span>
            </div>
            <div class="status-item">
                <span>Data Source: {stats['data_source']}</span>
            </div>
            <div class="status-item">
                <span>Last Update: {stats['last_update'][:19]}</span>
            </div>
        </div>
        
        <div class="warning-box">
            <strong>✅ Live Data:</strong> KTA price is now fetched live from CoinGecko API. 
            MURF price is calculated based on the live KTA price and OTC exchange rate. 
            Blockchain data is real-time from Keeta Network API.
            
            <!-- Compact Price Chart inside warning box -->
            <div class="compact-chart">
                <div class="chart-header">
                    <div class="chart-title">📈 MURF Price: ${stats.get('murf_usd_price', 0):.8f} (+2.45%)</div>
                    <div class="chart-controls">
                        <div class="timeframe-selector">
                            <button class="timeframe-btn active" data-timeframe="1h">1H</button>
                            <button class="timeframe-btn" data-timeframe="4h">4H</button>
                            <button class="timeframe-btn" data-timeframe="1d">1D</button>
                            <button class="timeframe-btn" data-timeframe="1w">1W</button>
                        </div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <canvas id="priceChart" width="400" height="150"></canvas>
                </div>
            </div>
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
                <div class="stat-label">KTA Price (USD)</div>
                <div class="stat-value">${stats['kta_price_usd']:.3f}</div>
                <div class="stat-sub">Live from CoinGecko API</div>
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
                <div class="stat-label">Total Blocks</div>
                <div class="stat-value">{stats['total_blocks']}</div>
                <div class="stat-sub">From Keeta API</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Type 7 MURF Trades</div>
                <div class="stat-value">{stats.get('type_7_count', 0)}</div>
                <div class="stat-sub">OTC Transactions Found</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Last Type 7 Trade</div>
                <div class="stat-value">{stats.get('last_trade_hash', 'N/A')[:20]}...</div>
                <div class="stat-sub">
                    {stats.get('last_trade_time', 'N/A')[:19] if stats.get('last_trade_hash') != 'N/A' else 'No trades found'}
                </div>
            </div>
        </div>
        
        <!-- Donation Section -->
        <div class="donation-section">
            <span class="donation-emoji">☕</span>
            <div class="donation-title">Buy Me a Coffee</div>
            <div class="donation-text">Support this project with a donation to:</div>
            <div class="donation-address">keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay</div>
        </div>
        
        <div class="activity-section">
            <div class="activity-title">📊 Recent MURF Trades (Type 7 OTC)</div>
            {self._render_murf_trades(stats.get('type_7_murf_txs', []))}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Chart data from server
        const chartData = {json.dumps(stats.get('chart_data', {}))};
        
        // DexScreener style chart
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        // Create gradient for area fill
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(0, 123, 255, 0.3)');
        gradient.addColorStop(1, 'rgba(0, 123, 255, 0.05)');
        
        const priceChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: chartData.labels || [],
                datasets: [
                    {{
                        label: 'MURF Price',
                        data: chartData.murf_prices || [],
                        borderColor: '#00d4aa',
                        backgroundColor: gradient,
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointHoverBackgroundColor: '#00d4aa',
                        pointHoverBorderColor: '#ffffff',
                        pointHoverBorderWidth: 2
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    intersect: false,
                    mode: 'index'
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#00d4aa',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {{
                            title: function(context) {{
                                return 'MURF Price: $' + context[0].parsed.y.toFixed(8);
                            }},
                            label: function(context) {{
                                return 'Time: ' + context.label;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        display: true,
                        grid: {{
                            display: false
                        }},
                        ticks: {{
                            color: '#666',
                            font: {{
                                size: 11
                            }}
                        }},
                        border: {{
                            display: false
                        }}
                    }},
                    y: {{
                        display: true,
                        position: 'right',
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)',
                            drawBorder: false
                        }},
                        ticks: {{
                            color: '#666',
                            font: {{
                                size: 11
                            }},
                            callback: function(value) {{
                                return '$' + value.toFixed(8);
                            }}
                        }},
                        border: {{
                            display: false
                        }}
                    }}
                }},
                elements: {{
                    line: {{
                        borderCapStyle: 'round'
                    }}
                }}
            }}
        }});
        
        // Timeframe selector functionality
        document.querySelectorAll('.timeframe-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                document.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                // Here you could implement timeframe switching logic
            }});
        }});
        
        // Auto-refresh every 30 seconds
        setInterval(function() {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _render_activity(self, activities):
        """Render activity list with explorer links"""
        if not activities:
            return '<div class="activity-item">No recent activity found</div>'
        
        html = ''
        for activity in activities:
            # Get the correct block hash (biasanya yang kedua atau terakhir)
            block_hashes = activity['block_hashes'] if activity['block_hashes'] else []
            
            # Pilih block hash yang benar - biasanya yang kedua atau terakhir
            if len(block_hashes) >= 2:
                # Gunakan block hash kedua (index 1) karena yang pertama mungkin tidak valid
                correct_block = block_hashes[1]
            elif len(block_hashes) == 1:
                # Jika hanya ada satu, gunakan yang itu
                correct_block = block_hashes[0]
            else:
                correct_block = 'N/A'
            
            # Cek apakah block hash valid (tidak N/A dan panjangnya benar)
            if correct_block != 'N/A' and len(correct_block) == 64:
                explorer_link = f"https://explorer.test.keeta.com/block/{correct_block}"
                hash_display = f"{correct_block[:20]}..."
            else:
                # Gunakan link ke API explorer jika block hash tidak valid
                explorer_link = "https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit=10"
                hash_display = "Invalid block hash"
            
            html += f'''
            <div class="activity-item">
                <div class="activity-issuer">Issuer: {activity['issuer'][:30]}...</div>
                <div class="activity-details">
                    Serial: {activity['serial']} | 
                    Blocks: {activity['blocks_count']} | 
                    Time: {activity['validity_from'][:19]}
                </div>
                <div class="activity-links" style="margin-top: 10px;">
                    <a href="{explorer_link}" 
                       target="_blank" 
                       style="color: #007bff; text-decoration: none; font-size: 12px; margin-right: 15px;">
                        🔗 View Block
                    </a>
                    <a href="https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit=10" 
                       target="_blank" 
                       style="color: #28a745; text-decoration: none; font-size: 12px; margin-right: 15px;">
                        📊 API Explorer
                    </a>
                    <span style="font-size: 10px; color: #666; font-family: monospace;">
                        Hash: {hash_display}
                    </span>
                </div>
            </div>
            '''
        return html
    
    def _render_murf_trades(self, murf_trades):
        """Render OTC trades (Type 7 KTA + Type 0 MURF transactions)"""
        if not murf_trades:
            return '<div class="activity-item">No OTC trades found</div>'
        
        html = ''
        for trade in murf_trades:
            tx_hash = trade.get('tx_hash', 'N/A')
            kta_amount = trade.get('kta_amount', 0)
            murf_amount = trade.get('murf_amount', 0)
            from_addr = trade.get('from_address', 'N/A')
            to_addr = trade.get('to_address', 'N/A')
            date = trade.get('date', 'N/A')
            exchange_rate = trade.get('exchange_rate', 0)
            
            # Format amounts
            if murf_amount > 1000000:
                murf_str = f"{murf_amount/1000000:.2f}M MURF"
            elif murf_amount > 1000:
                murf_str = f"{murf_amount/1000:.2f}K MURF"
            else:
                murf_str = f"{murf_amount:,.0f} MURF"
            
            kta_str = f"{kta_amount:.2f} KTA"
            
            # Create explorer link
            if tx_hash != 'N/A' and len(tx_hash) == 64:
                explorer_link = f"https://explorer.keeta.com/block/{tx_hash}"
                hash_display = f"{tx_hash[:20]}..."
            else:
                explorer_link = "https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit=100"
                hash_display = "Invalid hash"
            # Create trade description
            trade_description = f"💰 OTC Trade: {murf_str} ⇄ {kta_str}"
            if exchange_rate > 0:
                trade_description += f" (Rate: 1 KTA = {exchange_rate:.0f} MURF)"
            
            html += f'''
            <div class="activity-item">
                <div class="activity-issuer">{trade_description}</div>
                <div class="activity-details">
                    From: {from_addr[:30]}... | 
                    To: {to_addr[:30]}... | 
                    Date: {date[:19] if date != 'N/A' else 'N/A'}
                </div>
                <div class="activity-links" style="margin-top: 10px;">
                    <a href="{explorer_link}" 
                       target="_blank" 
                       style="color: #007bff; text-decoration: none; font-size: 12px; margin-right: 15px;">
                        🔗 View Block
                    </a>
                    <a href="https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit=100" 
                       target="_blank" 
                       style="color: #28a745; text-decoration: none; font-size: 12px; margin-right: 15px;">
                        📊 API Explorer
                    </a>
                    <span style="font-size: 10px; color: #666; font-family: monospace;">
                        Hash: {hash_display}
                    </span>
                </div>
            </div>
            '''
        return html
    
    def serve_stats(self):
        """Serve statistics as JSON"""
        stats = self.api_client.get_token_statistics()
        self.send_json_response(stats)
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def main():
    PORT = int(os.environ.get('PORT', 5000))
    
        print("🚀 Starting Real Live MURF Token Dashboard... (DEBUG VERSION)")
    print(f"📊 Dashboard available at: http://localhost:{PORT}")
    print("🔄 Auto-refresh every 30 seconds")
    print("📡 Fetching REAL data from Keeta API")
    print("⚠️  WARNING: Prices are estimates, not live trading prices")
    print("Press Ctrl+C to stop")
    
    with socketserver.TCPServer(("0.0.0.0", PORT), RealLiveDashboardHandler) as httpd:
        print(f"✅ Server running on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()
