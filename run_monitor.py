#!/usr/bin/env python3
"""
Keeta Monitor Runner
Script utama untuk menjalankan semua komponen monitoring
"""

import time
import threading
from datetime import datetime
from keeta_monitor import KeetaMonitor
from price_analyzer import KeetaPriceAnalyzer
from notification_system import KeetaNotifier

class KeetaMonitorRunner:
    def __init__(self):
        self.monitor = KeetaMonitor()
        self.analyzer = KeetaPriceAnalyzer()
        self.notifier = KeetaNotifier()
        self.running = False
    
    def start_monitoring(self):
        """Mulai monitoring dalam thread terpisah"""
        self.running = True
        
        # Thread untuk monitoring transaksi
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Thread untuk analisis harga
        analysis_thread = threading.Thread(target=self._analysis_loop)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        # Thread untuk notifikasi
        notification_thread = threading.Thread(target=self._notification_loop)
        notification_thread.daemon = True
        notification_thread.start()
        
        print("🚀 Keeta Monitor Started!")
        print("Monitoring MURF-KTA OTC trades...")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def _monitor_loop(self):
        """Loop untuk monitoring transaksi"""
        while self.running:
            try:
                # Ambil data terbaru
                history = self.monitor.get_ledger_history(limit=50)
                if history:
                    # Parse dan simpan transaksi
                    new_trades = 0
                    for entry in history.get("history", []):
                        blocks = entry.get("voteStaple", {}).get("blocks", [])
                        
                        for block in blocks:
                            operations = block.get("operations", [])
                            
                            for operation in operations:
                                trade_data = self.monitor.parse_transaction(operation, block)
                                if trade_data:
                                    self.monitor.save_trade(trade_data)
                                    new_trades += 1
                    
                    if new_trades > 0:
                        print(f"📊 Found {new_trades} new trades at {datetime.now().strftime('%H:%M:%S')}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(60)
    
    def _analysis_loop(self):
        """Loop untuk analisis harga"""
        while self.running:
            try:
                # Generate dan tampilkan laporan harga
                self.analyzer.print_price_summary()
                print("-" * 50)
                
                time.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                print(f"❌ Analysis error: {e}")
                time.sleep(60)
    
    def _notification_loop(self):
        """Loop untuk notifikasi"""
        while self.running:
            try:
                # Cek alert
                self.notifier.check_alerts()
                
                time.sleep(60)  # Check alerts every minute
                
            except Exception as e:
                print(f"❌ Notification error: {e}")
                time.sleep(60)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        print("\n👋 Keeta Monitor stopped")

def main():
    """Main function"""
    runner = KeetaMonitorRunner()
    
    print("🔍 Keeta Network Token Monitor")
    print("=" * 50)
    print("Monitoring MURF-KTA OTC trades on Keeta blockchain")
    print("Token IDs:")
    print(f"  MURF: keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm")
    print(f"  KTA:  keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg")
    print("=" * 50)
    
    try:
        runner.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
