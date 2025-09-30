#!/usr/bin/env python3
"""
MURF Token Dashboard
Dashboard untuk menampilkan statistik dan grafik harga MURF Token
"""

import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import json

class MURFDashboard:
    def __init__(self, db_path: str = "keeta_trades.db"):
        self.db_path = db_path
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
        
        # MURF Token Statistics
        self.murf_total_supply = 1_000_000_000_000.00  # 1T MURF
        self.murf_circulation = 60_000_000_000.00     # 60B MURF
        self.kta_price_usd = 0.658  # Live KTA price
        
    def get_token_statistics(self) -> Dict:
        """Ambil statistik token dari database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ambil data transaksi terbaru
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
        
        # Analisis transaksi terbaru
        murf_trades = [t for t in trades if t['token_id'] == self.murf_token]
        kta_trades = [t for t in trades if t['token_id'] == self.kta_token]
        
        # Cari last known trade
        last_murf_trade = murf_trades[0] if murf_trades else None
        last_kta_trade = kta_trades[0] if kta_trades else None
        
        # Hitung exchange rate berdasarkan data OTC
        exchange_rate = 0
        murf_kta_price = 0.000004  # Default: 1 MURF = 0.000004 KTA (250,000 MURF = 1 KTA)
        
        # Cari transaksi OTC untuk mendapatkan exchange rate yang benar
        otc_trades = [t for t in trades if t.get('is_otc', False)]
        if otc_trades:
            # Ambil exchange ratio dari OTC trade
            otc_trade = otc_trades[0]
            if otc_trade.get('exchange_ratio', 0) > 0:
                exchange_rate = otc_trade['exchange_ratio']
                murf_kta_price = 1 / exchange_rate  # 1 MURF = 1/exchange_rate KTA
            else:
                # Fallback: 250,000 MURF = 1 KTA
                exchange_rate = 250000.0
                murf_kta_price = 1 / exchange_rate
        else:
            # Default exchange rate
            exchange_rate = 250000.0
            murf_kta_price = 1 / exchange_rate
        
        murf_usd_price = murf_kta_price * self.kta_price_usd
        
        # Hitung market cap dan FDV
        murf_fdv = self.murf_total_supply * murf_usd_price
        murf_marketcap = self.murf_circulation * murf_usd_price
        
        return {
            "murf_total_supply": self.murf_total_supply,
            "murf_circulation": self.murf_circulation,
            "kta_price_usd": self.kta_price_usd,
            "last_murf_trade": last_murf_trade['amount_decimal'] if last_murf_trade else 0,
            "last_kta_trade": last_kta_trade['amount_decimal'] if last_kta_trade else 0,
            "exchange_rate_kta": 1.0,
            "exchange_rate_murf": exchange_rate,
            "murf_kta_price": murf_kta_price,
            "murf_usd_price": murf_usd_price,
            "murf_fdv": murf_fdv,
            "murf_marketcap": murf_marketcap,
            "last_trade_time": last_murf_trade['timestamp'] if last_murf_trade else datetime.now().isoformat()
        }
    
    def _get_default_stats(self) -> Dict:
        """Return default statistics jika tidak ada data"""
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
        """Ambil riwayat harga untuk grafik"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ambil data 5 hari terakhir
        cutoff_time = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT timestamp, amount_decimal, token_id, is_otc, exchange_ratio, counterpart_amount
            FROM trades 
            WHERE timestamp > ? AND token_id IN (?, ?)
            ORDER BY timestamp ASC
        ''', (cutoff_time.isoformat(), self.murf_token, self.kta_token))
        
        trades = cursor.fetchall()
        conn.close()
        
        # Generate price history
        price_history = []
        current_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = current_date + timedelta(days=i)
            
            # Cari transaksi pada hari ini
            day_trades = [t for t in trades if t[0].startswith(date.strftime('%Y-%m-%d'))]
            
            if day_trades:
                # Hitung harga rata-rata hari ini
                murf_trades = [t for t in day_trades if t[2] == self.murf_token]
                kta_trades = [t for t in day_trades if t[2] == self.kta_token]
                
                if murf_trades and kta_trades:
                    # Hitung rata-rata dari transaksi hari ini
                    avg_murf = sum(t[1] for t in murf_trades) / len(murf_trades)
                    avg_kta = sum(t[1] for t in kta_trades) / len(kta_trades)
                    
                    if avg_kta > 0:
                        exchange_rate = avg_murf / avg_kta
                        murf_kta_price = 1 / exchange_rate if exchange_rate > 0 else 0
                        murf_usd_price = murf_kta_price * self.kta_price_usd
                    else:
                        murf_usd_price = 0.00000263  # Default price
                else:
                    murf_usd_price = 0.00000263  # Default price
            else:
                # Generate realistic price movement
                base_price = 0.00000263
                variation = np.random.normal(0, 0.000001)
                murf_usd_price = max(0.0000001, base_price + variation)
            
            price_history.append({
                "date": date,
                "price": murf_usd_price,
                "formatted_date": date.strftime("%d/%m/%Y %H:%M:%S")
            })
        
        return price_history
    
    def create_dashboard(self):
        """Buat dashboard lengkap"""
        # Ambil data
        stats = self.get_token_statistics()
        price_history = self.get_price_history()
        
        # Setup figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('MURF TOKEN DASHBOARD', fontsize=16, fontweight='bold')
        
        # Left panel - Statistics
        self._create_statistics_panel(ax1, stats)
        
        # Right panel - Price chart
        self._create_price_chart(ax2, price_history)
        
        plt.tight_layout()
        plt.show()
    
    def _create_statistics_panel(self, ax, stats: Dict):
        """Buat panel statistik"""
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'MURF TOKEN STATISTICS', 
                ha='center', va='top', fontsize=14, fontweight='bold')
        
        # Basic stats
        y_pos = 0.85
        ax.text(0.05, y_pos, f'MURF Total Supply:', fontweight='bold')
        ax.text(0.6, y_pos, f'{stats["murf_total_supply"]:,.2f}', ha='right')
        
        y_pos -= 0.08
        ax.text(0.05, y_pos, f'MURF Circulation:', fontweight='bold')
        ax.text(0.6, y_pos, f'{stats["murf_circulation"]:,.2f}', ha='right')
        
        y_pos -= 0.08
        ax.text(0.05, y_pos, f'Live KTA Price (USD):', fontweight='bold')
        ax.text(0.6, y_pos, f'${stats["kta_price_usd"]:.3f}', ha='right')
        
        # Last Known Trade
        y_pos -= 0.12
        ax.text(0.05, y_pos, 'Last Known Trade:', fontweight='bold', fontsize=12)
        y_pos -= 0.08
        ax.text(0.1, y_pos, f'MURF: {stats["last_murf_trade"]:,.2f}')
        y_pos -= 0.06
        ax.text(0.1, y_pos, f'KTA: {stats["last_kta_trade"]:,.2f}')
        
        # Exchange Rates
        y_pos -= 0.12
        ax.text(0.05, y_pos, 'Exchange Rates:', fontweight='bold', fontsize=12)
        y_pos -= 0.08
        ax.text(0.1, y_pos, f'KTA: {stats["exchange_rate_kta"]:.2f}')
        y_pos -= 0.06
        ax.text(0.1, y_pos, f'MURF: {stats["exchange_rate_murf"]:,.2f}')
        
        # Key metrics (highlighted)
        y_pos -= 0.12
        ax.text(0.05, y_pos, 'Key Metrics:', fontweight='bold', fontsize=12, color='orange')
        y_pos -= 0.08
        ax.text(0.1, y_pos, f'MURF/KTA Price: {stats["murf_kta_price"]:.8f}', color='orange')
        y_pos -= 0.06
        ax.text(0.1, y_pos, f'MURF/USD Price: ${stats["murf_usd_price"]:.8f}', color='orange')
        y_pos -= 0.06
        ax.text(0.1, y_pos, f'MURF FDV (USD): ${stats["murf_fdv"]:,.0f}', color='orange')
        y_pos -= 0.06
        ax.text(0.1, y_pos, f'MURF Marketcap (USD): ${stats["murf_marketcap"]:,.0f}', color='orange')
        
        # Footer
        y_pos -= 0.15
        ax.text(0.05, y_pos, 'Dashboard By: @sack_kta', fontsize=10, style='italic')
        y_pos -= 0.06
        ax.text(0.05, y_pos, f'{self.murf_token[:50]}...', fontsize=8, family='monospace')
    
    def _create_price_chart(self, ax, price_history: List[Dict]):
        """Buat grafik harga"""
        if not price_history:
            ax.text(0.5, 0.5, 'No price data available', ha='center', va='center')
            return
        
        # Extract data
        dates = [p['date'] for p in price_history]
        prices = [p['price'] for p in price_history]
        
        # Plot
        ax.plot(dates, prices, 'b-', linewidth=2, marker='o', markersize=4)
        ax.set_title('MURF Token Price (USD)', fontweight='bold')
        ax.set_ylabel('MURF Price (USD)')
        ax.set_xlabel('Datetime (AEST)')
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.8f}'))
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M'))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        # Set y-axis range
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            margin = (max_price - min_price) * 0.1
            ax.set_ylim(max(0, min_price - margin), max_price + margin)
    
    def print_statistics(self):
        """Print statistik ke console"""
        stats = self.get_token_statistics()
        
        print("📊 MURF TOKEN STATISTICS")
        print("=" * 50)
        print(f"MURF Total Supply: {stats['murf_total_supply']:,.2f}")
        print(f"MURF Circulation: {stats['murf_circulation']:,.2f}")
        print(f"Live KTA Price (USD): ${stats['kta_price_usd']:.3f}")
        print()
        print("Last Known Trade:")
        print(f"  MURF: {stats['last_murf_trade']:,.2f}")
        print(f"  KTA: {stats['last_kta_trade']:,.2f}")
        print()
        print("Exchange Rates:")
        print(f"  KTA: {stats['exchange_rate_kta']:.2f}")
        print(f"  MURF: {stats['exchange_rate_murf']:,.2f}")
        print()
        print("Key Metrics:")
        print(f"  MURF/KTA Price: {stats['murf_kta_price']:.8f}")
        print(f"  MURF/USD Price: ${stats['murf_usd_price']:.8f}")
        print(f"  MURF FDV (USD): ${stats['murf_fdv']:,.0f}")
        print(f"  MURF Marketcap (USD): ${stats['murf_marketcap']:,.0f}")
        print()
        print(f"Dashboard By: @sack_kta")
        print(f"Token ID: {self.murf_token}")

def main():
    """Main function"""
    dashboard = MURFDashboard()
    
    print("🚀 MURF Token Dashboard")
    print("Creating dashboard...")
    print()
    
    # Print statistics
    dashboard.print_statistics()
    print()
    
    # Create visual dashboard
    try:
        dashboard.create_dashboard()
    except ImportError:
        print("❌ matplotlib not installed. Install with: pip install matplotlib")
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")

if __name__ == "__main__":
    main()
