#!/usr/bin/env python3
"""
Keeta Network Token Monitor Bot
Memantau transaksi OTC MURF-KTA di blockchain Keeta
"""

import requests
import json
import time
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KeetaMonitor:
    def __init__(self, db_path: str = "keeta_trades.db"):
        self.api_base = "https://rep2.main.network.api.keeta.com/api/node"
        self.db_path = db_path
        self.setup_database()
        
        # Token IDs yang dipantau
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
        
    def setup_database(self):
        """Setup database untuk menyimpan data transaksi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                block_hash TEXT,
                from_address TEXT,
                to_address TEXT,
                token_id TEXT,
                amount_hex TEXT,
                amount_decimal REAL,
                price_usd REAL,
                trade_type TEXT,
                operation_type INTEGER,
                is_otc BOOLEAN DEFAULT 0,
                otc_from_address TEXT,
                otc_exact BOOLEAN DEFAULT 0,
                otc_type TEXT,
                trade_pair TEXT,
                settlement_time TEXT,
                network TEXT,
                signer TEXT,
                exchange_ratio REAL,
                counterpart_amount REAL,
                counterpart_token TEXT,
                related_operations TEXT,
                raw_operation TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                token_id TEXT,
                price REAL,
                volume REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database setup completed")
    
    def hex_to_decimal(self, hex_value: str) -> float:
        """Konversi hex ke desimal dengan handling untuk nilai besar"""
        try:
            # Handle nilai yang sangat besar dengan konversi ke float
            decimal_value = int(hex_value, 16)
            
            # Jika nilai terlalu besar (> 1e15), konversi ke format yang lebih kecil
            if decimal_value > 1e15:
                # Asumsikan ini adalah token dengan 18 decimals
                return decimal_value / 1e18
            else:
                return float(decimal_value)
                
        except (ValueError, OverflowError):
            return 0.0
    
    def get_ledger_history(self, limit: int = 50) -> Optional[Dict]:
        """Ambil riwayat ledger dari API Keeta"""
        try:
            url = f"{self.api_base}/ledger/history"
            params = {"limit": limit}
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching ledger history: {e}")
            return None
    
    def parse_transaction(self, operation: Dict, block_data: Dict) -> Optional[Dict]:
        """Parse transaksi individual"""
        try:
            # Cek apakah ini transaksi MURF atau KTA
            token_id = operation.get("token", "")
            if token_id not in [self.murf_token, self.kta_token]:
                return None
            
            # Tentukan jenis transaksi berdasarkan type
            operation_type = operation.get("type", 0)
            trade_type_map = {
                0: "transfer",
                1: "mint",
                2: "burn", 
                3: "freeze",
                4: "unfreeze",
                5: "approve",
                6: "revoke",
                7: "otc_trade",  # Transaksi OTC
                8: "swap",
                9: "stake",
                10: "unstake"
            }
            
            trade_type = trade_type_map.get(operation_type, f"unknown_type_{operation_type}")
            
            # Extract data transaksi
            trade_data = {
                "timestamp": block_data.get("date", ""),
                "block_hash": block_data.get("$hash", ""),
                "from_address": block_data.get("account", ""),
                "to_address": operation.get("to", ""),
                "token_id": token_id,
                "amount_hex": operation.get("amount", ""),
                "amount_decimal": self.hex_to_decimal(operation.get("amount", "0x0")),
                "trade_type": trade_type,
                "operation_type": operation_type,
                "raw_operation": operation  # Simpan data mentah untuk analisis lebih lanjut
            }
            
            # Khusus untuk type 7 (OTC), tambahkan analisis tambahan
            if operation_type == 7:
                trade_data.update(self._parse_otc_trade(operation, block_data))
            
            return trade_data
        except Exception as e:
            logger.error(f"Error parsing transaction: {e}")
            return None
    
    def _parse_otc_trade(self, operation: Dict, block_data: Dict) -> Dict:
        """Parse transaksi OTC (type 7) dengan detail tambahan"""
        try:
            # Analisis khusus untuk transaksi OTC berdasarkan struktur data yang sebenarnya
            otc_data = {
                "is_otc": True,
                "otc_details": {
                    "from_address": operation.get("from", ""),
                    "exact": operation.get("exact", False),
                    "otc_type": "swap",  # Berdasarkan data, ini adalah SWAP
                    "trade_pair": f"{operation.get('token', '')[:20]}...",
                    "settlement_time": block_data.get("date", ""),
                    "block_hash": block_data.get("$hash", ""),
                    "network": block_data.get("network", ""),
                    "signer": block_data.get("signer", "")
                }
            }
            
            # Cari operasi terkait dalam block yang sama untuk mendapatkan counterpart
            related_operations = []
            if "operations" in block_data:
                for op in block_data["operations"]:
                    if op.get("type") == 0 and op.get("token") != operation.get("token"):
                        related_operations.append({
                            "to": op.get("to", ""),
                            "amount": op.get("amount", ""),
                            "amount_decimal": self.hex_to_decimal(op.get("amount", "0x0")),
                            "token": op.get("token", "")
                        })
            
            otc_data["otc_details"]["related_operations"] = related_operations
            
            # Hitung rasio pertukaran jika ada operasi terkait
            if related_operations:
                main_amount = self.hex_to_decimal(operation.get("amount", "0x0"))
                counterpart_amount = related_operations[0]["amount_decimal"]
                
                if main_amount > 0 and counterpart_amount > 0:
                    otc_data["otc_details"]["exchange_ratio"] = main_amount / counterpart_amount
                    otc_data["otc_details"]["counterpart_amount"] = counterpart_amount
                    otc_data["otc_details"]["counterpart_token"] = related_operations[0]["token"]
            
            return otc_data
            
        except Exception as e:
            logger.error(f"Error parsing OTC trade: {e}")
            return {"is_otc": True, "otc_details": {}}
    
    def save_trade(self, trade_data: Dict):
        """Simpan data transaksi ke database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract OTC data jika ada
            otc_details = trade_data.get("otc_details", {})
            is_otc = trade_data.get("is_otc", False)
            
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, block_hash, from_address, to_address, 
                    token_id, amount_hex, amount_decimal, trade_type,
                    operation_type, is_otc, otc_from_address, otc_exact,
                    otc_type, trade_pair, settlement_time, network, signer,
                    exchange_ratio, counterpart_amount, counterpart_token,
                    related_operations, raw_operation
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data["timestamp"],
                trade_data["block_hash"],
                trade_data["from_address"],
                trade_data["to_address"],
                trade_data["token_id"],
                trade_data["amount_hex"],
                trade_data["amount_decimal"],
                trade_data["trade_type"],
                trade_data.get("operation_type", 0),
                is_otc,
                otc_details.get("from_address", ""),
                otc_details.get("exact", False),
                otc_details.get("otc_type", ""),
                otc_details.get("trade_pair", ""),
                otc_details.get("settlement_time", ""),
                otc_details.get("network", ""),
                otc_details.get("signer", ""),
                otc_details.get("exchange_ratio", 0),
                otc_details.get("counterpart_amount", 0),
                otc_details.get("counterpart_token", ""),
                json.dumps(otc_details.get("related_operations", [])),
                json.dumps(trade_data.get("raw_operation", {}))
            ))
            
            conn.commit()
            conn.close()
            
            # Log dengan detail OTC jika ada
            if is_otc:
                exchange_ratio = otc_details.get('exchange_ratio', 0)
                counterpart_amount = otc_details.get('counterpart_amount', 0)
                counterpart_token = otc_details.get('counterpart_token', '')[:20] + '...' if otc_details.get('counterpart_token') else 'N/A'
                
                logger.info(f"🔄 OTC SWAP detected: {trade_data['amount_decimal']:,} {trade_data['token_id'][:20]}... "
                          f"⇄ {counterpart_amount:,} {counterpart_token} "
                          f"(Ratio: {exchange_ratio:.8f})")
            else:
                logger.info(f"💸 Regular trade: {trade_data['amount_decimal']:,} {trade_data['token_id'][:20]}... "
                          f"(Type: {trade_data['trade_type']})")
            
        except Exception as e:
            logger.error(f"Error saving trade: {e}")
    
    def calculate_price_ratio(self) -> Optional[float]:
        """Hitung rasio harga MURF/KTA dari transaksi terbaru"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ambil transaksi terbaru untuk kedua token
            cursor.execute('''
                SELECT token_id, amount_decimal, timestamp 
                FROM trades 
                WHERE token_id IN (?, ?) 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''', (self.murf_token, self.kta_token))
            
            trades = cursor.fetchall()
            conn.close()
            
            if len(trades) < 2:
                return None
            
            # Cari transaksi yang berdekatan waktunya
            murf_trades = [t for t in trades if t[0] == self.murf_token]
            kta_trades = [t for t in trades if t[0] == self.kta_token]
            
            if murf_trades and kta_trades:
                # Ambil transaksi terbaru
                latest_murf = murf_trades[0]
                latest_kta = kta_trades[0]
                
                # Hitung rasio (asumsi 30M MURF = 116 KTA)
                if latest_murf[1] > 0 and latest_kta[1] > 0:
                    ratio = latest_murf[1] / latest_kta[1]
                    return ratio
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating price ratio: {e}")
            return None
    
    def monitor_trades(self, interval: int = 60):
        """Monitor transaksi secara real-time"""
        logger.info("Starting Keeta token monitor...")
        logger.info(f"Monitoring tokens: MURF ({self.murf_token[:20]}...) and KTA ({self.kta_token[:20]}...)")
        
        while True:
            try:
                # Ambil data terbaru
                history = self.get_ledger_history(limit=100)
                if not history:
                    logger.warning("Failed to fetch ledger history")
                    time.sleep(interval)
                    continue
                
                # Parse dan simpan transaksi baru
                new_trades = 0
                for entry in history.get("history", []):
                    blocks = entry.get("voteStaple", {}).get("blocks", [])
                    
                    for block in blocks:
                        operations = block.get("operations", [])
                        
                        for operation in operations:
                            trade_data = self.parse_transaction(operation, block)
                            if trade_data:
                                self.save_trade(trade_data)
                                new_trades += 1
                
                if new_trades > 0:
                    logger.info(f"Found {new_trades} new trades")
                    
                    # Hitung dan tampilkan rasio harga
                    ratio = self.calculate_price_ratio()
                    if ratio:
                        logger.info(f"Current MURF/KTA ratio: {ratio:.8f}")
                        logger.info(f"Price: 1 KTA = {ratio:.2f} MURF")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(interval)

def main():
    """Main function"""
    monitor = KeetaMonitor()
    
    print("🚀 Keeta Network Token Monitor")
    print("=" * 50)
    print("Monitoring MURF-KTA OTC trades on Keeta blockchain")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        monitor.monitor_trades(interval=30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print("\n👋 Monitor stopped")

if __name__ == "__main__":
    main()
