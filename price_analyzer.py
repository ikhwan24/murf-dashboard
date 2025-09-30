#!/usr/bin/env python3
"""
Keeta Price Analyzer
Analisis harga dan volume trading MURF-KTA
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import pandas as pd

class KeetaPriceAnalyzer:
    def __init__(self, db_path: str = "keeta_trades.db"):
        self.db_path = db_path
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
    
    def get_recent_trades(self, hours: int = 24) -> List[Dict]:
        """Ambil transaksi terbaru dalam N jam terakhir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT * FROM trades 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC
        ''', (cutoff_time.isoformat(),))
        
        columns = [description[0] for description in cursor.description]
        trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return trades
    
    def get_otc_trades(self, hours: int = 24) -> List[Dict]:
        """Ambil transaksi OTC terbaru"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT * FROM trades 
            WHERE timestamp > ? AND is_otc = 1
            ORDER BY timestamp DESC
        ''', (cutoff_time.isoformat(),))
        
        columns = [description[0] for description in cursor.description]
        otc_trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return otc_trades
    
    def calculate_murf_kta_ratio(self, trades: List[Dict]) -> float:
        """Hitung rasio MURF/KTA dari transaksi"""
        murf_trades = [t for t in trades if t['token_id'] == self.murf_token]
        kta_trades = [t for t in trades if t['token_id'] == self.kta_token]
        
        if not murf_trades or not kta_trades:
            return 0.0
        
        # Ambil transaksi terbesar untuk menghitung rasio
        max_murf = max(murf_trades, key=lambda x: x['amount_decimal'])
        max_kta = max(kta_trades, key=lambda x: x['amount_decimal'])
        
        # Hitung rasio berdasarkan contoh: 30M MURF = 116 KTA
        if max_murf['amount_decimal'] > 0 and max_kta['amount_decimal'] > 0:
            ratio = max_murf['amount_decimal'] / max_kta['amount_decimal']
            return ratio
        
        return 0.0
    
    def get_trading_volume(self, trades: List[Dict]) -> Dict:
        """Hitung volume trading per token"""
        murf_volume = sum(t['amount_decimal'] for t in trades if t['token_id'] == self.murf_token)
        kta_volume = sum(t['amount_decimal'] for t in trades if t['token_id'] == self.kta_token)
        
        return {
            'murf_volume': murf_volume,
            'kta_volume': kta_volume,
            'total_trades': len(trades)
        }
    
    def detect_large_trades(self, trades: List[Dict], threshold: int = 1000000) -> List[Dict]:
        """Deteksi transaksi besar (whale trades)"""
        large_trades = []
        
        for trade in trades:
            if trade['amount_decimal'] >= threshold:
                large_trades.append({
                    'timestamp': trade['timestamp'],
                    'token': 'MURF' if trade['token_id'] == self.murf_token else 'KTA',
                    'amount': trade['amount_decimal'],
                    'from': trade['from_address'],
                    'to': trade['to_address']
                })
        
        return large_trades
    
    def generate_price_report(self) -> Dict:
        """Generate laporan harga lengkap"""
        trades = self.get_recent_trades(24)  # 24 jam terakhir
        otc_trades = self.get_otc_trades(24)  # Transaksi OTC 24 jam terakhir
        
        if not trades:
            return {"error": "No recent trades found"}
        
        ratio = self.calculate_murf_kta_ratio(trades)
        volume = self.get_trading_volume(trades)
        large_trades = self.detect_large_trades(trades)
        
        # Analisis khusus OTC
        otc_analysis = self.analyze_otc_trades(otc_trades)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "price_ratio": {
                "murf_per_kta": ratio,
                "kta_per_murf": 1/ratio if ratio > 0 else 0,
                "formatted": f"1 KTA = {ratio:.2f} MURF" if ratio > 0 else "No data"
            },
            "volume_24h": {
                "murf_volume": volume['murf_volume'],
                "kta_volume": volume['kta_volume'],
                "total_trades": volume['total_trades']
            },
            "otc_analysis": otc_analysis,
            "large_trades": large_trades,
            "market_analysis": {
                "active_trading": volume['total_trades'] > 10,
                "high_volume": volume['murf_volume'] > 1000000000,  # 1B MURF
                "whale_activity": len(large_trades) > 0,
                "otc_activity": len(otc_trades) > 0
            }
        }
        
        return report
    
    def analyze_otc_trades(self, otc_trades: List[Dict]) -> Dict:
        """Analisis transaksi OTC"""
        if not otc_trades:
            return {"total_otc_trades": 0, "otc_volume": 0, "avg_price": 0}
        
        total_volume = sum(t['amount_decimal'] for t in otc_trades)
        total_price = sum(t['price_decimal'] for t in otc_trades if t['price_decimal'] > 0)
        avg_price = total_price / len([t for t in otc_trades if t['price_decimal'] > 0]) if any(t['price_decimal'] > 0 for t in otc_trades) else 0
        
        # Kategorisasi berdasarkan otc_type
        buy_trades = [t for t in otc_trades if t.get('otc_type') == 'buy']
        sell_trades = [t for t in otc_trades if t.get('otc_type') == 'sell']
        swap_trades = [t for t in otc_trades if t.get('otc_type') == 'swap']
        
        return {
            "total_otc_trades": len(otc_trades),
            "otc_volume": total_volume,
            "avg_price": avg_price,
            "buy_trades": len(buy_trades),
            "sell_trades": len(sell_trades),
            "swap_trades": len(swap_trades),
            "recent_otc": otc_trades[:5]  # 5 transaksi OTC terbaru
        }
    
    def print_price_summary(self):
        """Tampilkan ringkasan harga"""
        report = self.generate_price_report()
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        print("📊 Keeta Token Price Report")
        print("=" * 50)
        print(f"⏰ Time: {report['timestamp']}")
        print()
        
        print("💰 Price Information:")
        print(f"   {report['price_ratio']['formatted']}")
        print(f"   Ratio: {report['price_ratio']['murf_per_kta']:.8f}")
        print()
        
        print("📈 Volume (24h):")
        print(f"   MURF Volume: {report['volume_24h']['murf_volume']:,}")
        print(f"   KTA Volume: {report['volume_24h']['kta_volume']:,}")
        print(f"   Total Trades: {report['volume_24h']['total_trades']}")
        print()
        
        if report['large_trades']:
            print("🐋 Large Trades Detected:")
            for trade in report['large_trades'][:5]:  # Show top 5
                print(f"   {trade['amount']:,} {trade['token']} at {trade['timestamp']}")
        print()
        
        print("🔄 OTC Analysis:")
        otc = report['otc_analysis']
        print(f"   Total OTC Trades: {otc['total_otc_trades']}")
        print(f"   OTC Volume: {otc['otc_volume']:,}")
        print(f"   Average Price: {otc['avg_price']:.8f}")
        print(f"   Buy/Sell/Swap: {otc['buy_trades']}/{otc['sell_trades']}/{otc['swap_trades']}")
        print()
        
        if otc['recent_otc']:
            print("📋 Recent OTC Trades:")
            for trade in otc['recent_otc'][:3]:  # Show top 3
                counterpart_amount = trade.get('counterpart_amount', 0)
                counterpart_token = trade.get('counterpart_token', '')[:20] + '...' if trade.get('counterpart_token') else 'N/A'
                exchange_ratio = trade.get('exchange_ratio', 0)
                
                print(f"   • {trade['amount_decimal']:,} {trade['token_id'][:20]}... "
                      f"⇄ {counterpart_amount:,} {counterpart_token} "
                      f"(Ratio: {exchange_ratio:.8f}) at {trade['timestamp']}")
        print()
        
        print("🔍 Market Analysis:")
        analysis = report['market_analysis']
        print(f"   Active Trading: {'✅' if analysis['active_trading'] else '❌'}")
        print(f"   High Volume: {'✅' if analysis['high_volume'] else '❌'}")
        print(f"   Whale Activity: {'✅' if analysis['whale_activity'] else '❌'}")
        print(f"   OTC Activity: {'✅' if analysis['otc_activity'] else '❌'}")

def main():
    """Main function untuk menjalankan analyzer"""
    analyzer = KeetaPriceAnalyzer()
    
    print("🔍 Keeta Price Analyzer")
    print("Analyzing MURF-KTA trading activity...")
    print()
    
    analyzer.print_price_summary()

if __name__ == "__main__":
    main()
