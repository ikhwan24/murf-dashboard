import sqlite3
import json
from datetime import datetime

class OTCTransactionsDB:
    def __init__(self, db_path="otc_transactions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the OTC transactions database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create OTC transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otc_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_hash TEXT UNIQUE NOT NULL,
                block_hash TEXT,
                kta_amount REAL,
                murf_amount REAL,
                exchange_rate REAL,
                from_address TEXT,
                to_address TEXT,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tx_hash ON otc_transactions(tx_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON otc_transactions(timestamp)')
        
        conn.commit()
        conn.close()
        print("OTC Transactions database initialized")
    
    def save_otc_transaction(self, tx_data):
        """Save OTC transaction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO otc_transactions 
                (tx_hash, block_hash, kta_amount, murf_amount, exchange_rate, from_address, to_address, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tx_data.get('tx_hash', ''),
                tx_data.get('block_hash', ''),
                tx_data.get('kta_amount', 0),
                tx_data.get('murf_amount', 0),
                tx_data.get('exchange_rate', 0),
                tx_data.get('from_address', ''),
                tx_data.get('to_address', ''),
                tx_data.get('timestamp', '')
            ))
            conn.commit()
            print(f"💾 Saved OTC transaction: {tx_data.get('tx_hash', '')[:20]}...")
        except Exception as e:
            print(f"❌ Error saving OTC transaction: {e}")
        finally:
            conn.close()
    
    def get_latest_otc_transactions(self, limit=10):
        """Get latest OTC transactions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM otc_transactions 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            transactions = []
            for row in rows:
                transaction = dict(zip(columns, row))
                transactions.append(transaction)
            
            print(f"Retrieved {len(transactions)} OTC transactions from database")
            return transactions
        except Exception as e:
            print(f"Error retrieving OTC transactions: {e}")
            return []
        finally:
            conn.close()
    
    def get_otc_transaction_count(self):
        """Get total count of OTC transactions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM otc_transactions')
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Error getting OTC transaction count: {e}")
            return 0
        finally:
            conn.close()
    
    def get_latest_exchange_rate(self):
        """Get latest exchange rate from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT exchange_rate FROM otc_transactions 
                WHERE exchange_rate > 0 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"❌ Error getting latest exchange rate: {e}")
            return None
        finally:
            conn.close()
