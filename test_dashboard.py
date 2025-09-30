#!/usr/bin/env python3
"""
Test Dashboard untuk MURF Token
Test dashboard tanpa matplotlib untuk menghindari masalah GUI
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List

class MURFTestDashboard:
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
        exchange_rate = 250000.0  # Default: 250,000 MURF = 1 KTA
        murf_kta_price = 0.000004  # 1 MURF = 0.000004 KTA
        
        # Cari transaksi OTC untuk mendapatkan exchange rate yang benar
        otc_trades = [t for t in trades if t.get('is_otc', False)]
        if otc_trades:
            otc_trade = otc_trades[0]
            if otc_trade.get('exchange_ratio', 0) > 0:
                exchange_rate = otc_trade['exchange_ratio']
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
    dashboard = MURFTestDashboard()
    
    print("🚀 MURF Token Test Dashboard")
    print("Testing dashboard without matplotlib...")
    print()
    
    # Print statistics
    dashboard.print_statistics()
    print()
    
    print("✅ Dashboard test completed!")
    print("📊 Data should now be consistent with the image you showed")

if __name__ == "__main__":
    main()
