#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timedelta
import random

class OTCDataPopulator:
    def __init__(self):
        self.price_db_path = "price_history.db"
        self.otc_db_path = "otc_transactions.db"
        self.init_otc_database()
    
    def init_otc_database(self):
        """Initialize OTC transactions database"""
        conn = sqlite3.connect(self.otc_db_path)
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
        print("OTC database initialized successfully")
    
    def get_price_history_data(self):
        """Get data from price history database"""
        conn = sqlite3.connect(self.price_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT timestamp, kta_price_usd, murf_usd_price, exchange_rate_murf, 
                       last_trade_hash, type_7_count
                FROM price_history 
                WHERE exchange_rate_murf > 0 
                ORDER BY timestamp DESC 
                LIMIT 50
            ''')
            
            rows = cursor.fetchall()
            print(f"Found {len(rows)} price history records")
            return rows
            
        except Exception as e:
            print(f"Error getting price history: {e}")
            return []
        finally:
            conn.close()
    
    def generate_otc_transactions(self, price_data):
        """Generate OTC transactions from price history data"""
        otc_transactions = []
        
        # Sample addresses for realistic data
        addresses = [
            "keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay",
            "keeta_aabmds42gxybicqutzwytrydeiz4e4dkgrmuh2uzzhenjcl4h57cwvicbeozccy",
            "keeta_aab4anyllhowvsnjhpbynd6fvrdm4rby3xs4aoq5m4ttlhjhnrabtyxiqnmx25y",
            "keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay"
        ]
        
        for i, row in enumerate(price_data):
            timestamp, kta_price, murf_price, exchange_rate, trade_hash, type_7_count = row
            
            # Generate multiple OTC transactions for each price point
            for j in range(min(type_7_count, 3)):  # Max 3 transactions per price point
                # Generate realistic KTA amounts (1-50 KTA)
                kta_amount = round(random.uniform(1, 50), 2)
                
                # Calculate MURF amount based on exchange rate
                murf_amount = int(kta_amount * exchange_rate)
                
                # Generate unique transaction hash
                tx_hash = f"{trade_hash[:20]}{i:04d}{j:02d}"
                
                # Generate timestamp with some variation
                base_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                variation = timedelta(minutes=random.randint(-30, 30))
                tx_timestamp = (base_time + variation).isoformat()
                
                otc_transaction = {
                    'tx_hash': tx_hash,
                    'block_hash': trade_hash,
                    'kta_amount': kta_amount,
                    'murf_amount': murf_amount,
                    'exchange_rate': exchange_rate,
                    'from_address': random.choice(addresses),
                    'to_address': random.choice([addr for addr in addresses if addr != addresses[0]]),
                    'timestamp': tx_timestamp
                }
                
                otc_transactions.append(otc_transaction)
        
        print(f"Generated {len(otc_transactions)} OTC transactions")
        return otc_transactions
    
    def save_otc_transactions(self, transactions):
        """Save OTC transactions to database"""
        if not transactions:
            print("No transactions to save")
            return 0
        
        conn = sqlite3.connect(self.otc_db_path)
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
                
            except Exception as e:
                print(f"Error saving transaction {tx['tx_hash'][:20]}...: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"Saved {saved_count} OTC transactions to database")
        return saved_count
    
    def get_database_stats(self):
        """Get statistics from database"""
        conn = sqlite3.connect(self.otc_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM otc_transactions')
            count = cursor.fetchone()[0]
            
            if count > 0:
                cursor.execute('SELECT * FROM otc_transactions ORDER BY timestamp DESC LIMIT 5')
                rows = cursor.fetchall()
                print(f"\nDatabase Statistics:")
                print(f"   Total OTC transactions: {count}")
                print(f"   Latest transactions:")
                for i, row in enumerate(rows):
                    print(f"     {i+1}. {row[2]:.2f} KTA <-> {row[3]:,.0f} MURF (Rate: {row[4]:,.0f})")
                    print(f"        Time: {row[8]}")
                    print(f"        Hash: {row[1][:20]}...")
            else:
                print("Database is empty")
                
        except Exception as e:
            print(f"Error getting database stats: {e}")
        finally:
            conn.close()
    
    def populate_database(self):
        """Main function to populate OTC database"""
        print("Starting OTC Database Population...")
        
        # Get price history data
        price_data = self.get_price_history_data()
        if not price_data:
            print("No price history data found")
            return False
        
        # Generate OTC transactions
        otc_transactions = self.generate_otc_transactions(price_data)
        if not otc_transactions:
            print("No OTC transactions generated")
            return False
        
        # Save to database
        saved_count = self.save_otc_transactions(otc_transactions)
        
        # Show database stats
        self.get_database_stats()
        
        print(f"\nPopulation completed! Saved {saved_count} OTC transactions")
        return True

if __name__ == "__main__":
    populator = OTCDataPopulator()
    populator.populate_database()
