#!/usr/bin/env python3

import sqlite3
import requests
import json
from datetime import datetime
import time

class OTCDatabaseManager:
    def __init__(self):
        self.api_url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history"
        self.db_path = "otc_transactions.db"
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
        self.init_database()
    
    def init_database(self):
        """Initialize OTC transactions database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otc_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_hash TEXT UNIQUE NOT NULL,
                block_hash TEXT,
                kta_amount REAL NOT NULL,
                murf_amount REAL NOT NULL,
                exchange_rate REAL NOT NULL,
                from_address TEXT,
                to_address TEXT,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tx_hash ON otc_transactions(tx_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON otc_transactions(timestamp)')
        
        conn.commit()
        conn.close()
        print("[OK] OTC Transactions database initialized")
    
    def clean_database(self):
        """Clear all OTC transactions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM otc_transactions')
            conn.commit()
            print("[OK] Database cleared - all OTC transactions removed")
            return True
        except Exception as e:
            print(f"[ERROR] Error clearing database: {e}")
            return False
        finally:
            conn.close()
    
    def fetch_api_data(self, limit=200):
        """Fetch data from API"""
        try:
            params = {"limit": limit}
            
            print(f"[DEBUG] Fetching data from API with limit={limit}...")
            response = requests.get(self.api_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] API data fetched: {len(data.get('history', []))} entries")
                return data
            else:
                print(f"[ERROR] API Error: {response.status_code} - {response.text[:100]}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Exception fetching API data: {e}")
            return None
    
    def analyze_otc_transactions(self, data):
        """Analyze OTC transactions from API data"""
        if not data or 'history' not in data:
            print("[WARNING] No history data found")
            return []
        
        otc_transactions = []
        print(f"[DEBUG] Analyzing {len(data['history'])} history entries...")
        
        for entry in data['history']:
            if 'operations' in entry:
                operations = entry['operations']
                
                # Look for Type 7 KTA operations
                type_7_kta = None
                type_0_murf = None
                
                for op in operations:
                    if op.get('type') == 7 and op.get('token') == self.kta_token:
                        type_7_kta = op
                    elif op.get('type') == 0 and op.get('token') == self.murf_token:
                        type_0_murf = op
                
                # If we found both Type 7 KTA and Type 0 MURF in the same block
                if type_7_kta and type_0_murf:
                    try:
                        # Parse KTA amount
                        kta_amount_hex = type_7_kta.get('amount', '0x0')
                        kta_amount = int(kta_amount_hex, 16) / 1e18
                        
                        # Parse MURF amount
                        murf_amount_hex = type_0_murf.get('amount', '0x0')
                        murf_amount = int(murf_amount_hex, 16)
                        
                        if kta_amount > 0 and murf_amount > 0:
                            exchange_rate = murf_amount / kta_amount
                            
                            otc_transaction = {
                                'tx_hash': entry.get('$hash', 'N/A'),
                                'block_hash': entry.get('$hash', 'N/A'),
                                'kta_amount': kta_amount,
                                'murf_amount': murf_amount,
                                'exchange_rate': exchange_rate,
                                'from_address': type_7_kta.get('from', 'N/A'),
                                'to_address': type_0_murf.get('to', 'N/A'),
                                'timestamp': entry.get('date', datetime.now().isoformat())
                            }
                            
                            otc_transactions.append(otc_transaction)
                            print(f"[OK] Found OTC: {kta_amount:.2f} KTA <-> {murf_amount:,.0f} MURF (Rate: {exchange_rate:,.0f})")
                    
                    except Exception as e:
                        print(f"[ERROR] Error parsing OTC transaction: {e}")
        
        print(f"[DATA] Total OTC transactions found: {len(otc_transactions)}")
        return otc_transactions
    
    def save_otc_transactions(self, transactions):
        """Save OTC transactions to database"""
        if not transactions:
            print("[WARNING] No transactions to save")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for tx in transactions:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO otc_transactions 
                    (tx_hash, block_hash, kta_amount, murf_amount, exchange_rate, 
                     from_address, to_address, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tx['tx_hash'],
                    tx['block_hash'],
                    tx['kta_amount'],
                    tx['murf_amount'],
                    tx['exchange_rate'],
                    tx['from_address'],
                    tx['to_address'],
                    tx['timestamp']
                ))
                saved_count += 1
                print(f"[SAVE] Saved OTC transaction: {tx['tx_hash'][:20]}...")
                
            except Exception as e:
                print(f"[ERROR] Error saving transaction {tx['tx_hash'][:20]}...: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"[OK] Saved {saved_count} OTC transactions to database")
        return saved_count
    
    def get_database_stats(self):
        """Get statistics from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM otc_transactions')
            count = cursor.fetchone()[0]
            
            if count > 0:
                cursor.execute('SELECT * FROM otc_transactions ORDER BY timestamp DESC LIMIT 5')
                rows = cursor.fetchall()
                print(f"\n[DATA] Database Statistics:")
                print(f"   Total OTC transactions: {count}")
                print(f"   Latest transactions:")
                for i, row in enumerate(rows):
                    print(f"     {i+1}. {row[2]:.2f} KTA <-> {row[3]:,.0f} MURF (Rate: {row[4]:,.0f})")
                    print(f"        Time: {row[8]}")
                    print(f"        Hash: {row[1][:20]}...")
            else:
                print("[WARNING] Database is empty")
                
        except Exception as e:
            print(f"[ERROR] Error getting database stats: {e}")
        finally:
            conn.close()
    
    def clean_and_update(self):
        """Main function to clean database and update with latest API data"""
        print("[OK] Starting OTC Database Clean and Update...")
        
        # Step 1: Clean database
        print("\n[STEP 1] Cleaning database...")
        if not self.clean_database():
            print("[ERROR] Failed to clean database")
            return False
        
        # Step 2: Fetch latest data from API
        print("\n[STEP 2] Fetching latest data from API...")
        data = self.fetch_api_data(limit=200)
        if not data:
            print("[ERROR] Failed to fetch API data")
            return False
        
        # Step 3: Analyze OTC transactions
        print("\n[STEP 3] Analyzing OTC transactions...")
        otc_transactions = self.analyze_otc_transactions(data)
        if not otc_transactions:
            print("[WARNING] No OTC transactions found in API data")
            return True  # Success but no data
        
        # Step 4: Save to database
        print("\n[STEP 4] Saving to database...")
        saved_count = self.save_otc_transactions(otc_transactions)
        
        # Step 5: Show statistics
        print("\n[STEP 5] Database statistics...")
        self.get_database_stats()
        
        print(f"\n[OK] Clean and update completed! Saved {saved_count} OTC transactions")
        return True

if __name__ == "__main__":
    manager = OTCDatabaseManager()
    manager.clean_and_update()
