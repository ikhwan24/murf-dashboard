#!/usr/bin/env python3
"""
Price History Database Manager
"""

import sqlite3
import json
from datetime import datetime
import requests

class PriceHistoryDB:
    def __init__(self, db_path="price_history.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Setup price history database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create price_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                kta_price_usd REAL NOT NULL,
                murf_kta_price REAL NOT NULL,
                murf_usd_price REAL NOT NULL,
                exchange_rate_murf REAL NOT NULL,
                murf_fdv REAL NOT NULL,
                murf_marketcap REAL NOT NULL,
                type_7_count INTEGER DEFAULT 0,
                last_trade_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON price_history(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_price_data(self, price_data):
        """Save price data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO price_history 
            (timestamp, kta_price_usd, murf_kta_price, murf_usd_price, 
             exchange_rate_murf, murf_fdv, murf_marketcap, type_7_count, last_trade_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            price_data.get('timestamp', datetime.now().isoformat()),
            price_data.get('kta_price_usd', 0),
            price_data.get('murf_kta_price', 0),
            price_data.get('murf_usd_price', 0),
            price_data.get('exchange_rate_murf', 0),
            price_data.get('murf_fdv', 0),
            price_data.get('murf_marketcap', 0),
            price_data.get('type_7_count', 0),
            price_data.get('last_trade_hash', 'N/A')
        ))
        
        conn.commit()
        conn.close()
    
    def get_price_history(self, limit=100):
        """Get price history for chart"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, kta_price_usd, murf_kta_price, murf_usd_price,
                   exchange_rate_murf, murf_fdv, murf_marketcap, type_7_count
            FROM price_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        history = []
        for row in results:
            history.append({
                'timestamp': row[0],
                'kta_price_usd': row[1],
                'murf_kta_price': row[2],
                'murf_usd_price': row[3],
                'exchange_rate_murf': row[4],
                'murf_fdv': row[5],
                'murf_marketcap': row[6],
                'type_7_count': row[7]
            })
        
        return history
    
    def get_chart_data(self, limit=50):
        """Get formatted data for Chart.js"""
        history = self.get_price_history(limit)
        
        # Reverse to get chronological order
        history.reverse()
        
        labels = []
        kta_prices = []
        murf_prices = []
        murf_kta_prices = []  # Add MURF-KTA exchange rates
        market_caps = []
        
        for entry in history:
            # Format timestamp for display
            dt = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
            labels.append(dt.strftime('%H:%M'))
            
            kta_prices.append(round(entry['kta_price_usd'], 4))
            murf_prices.append(round(entry['murf_usd_price'], 8))
            # Add MURF-KTA exchange rate (MURF per KTA)
            if entry.get('exchange_rate_murf', 0) > 0:
                murf_kta_prices.append(round(entry['exchange_rate_murf'], 2))
            else:
                # Calculate from murf_kta_price if exchange_rate_murf not available
                if entry.get('murf_kta_price', 0) > 0:
                    murf_kta_prices.append(round(1 / entry['murf_kta_price'], 2))
                else:
                    murf_kta_prices.append(0)
            market_caps.append(round(entry['murf_marketcap'], 0))
        
        return {
            'labels': labels,
            'kta_prices': kta_prices,
            'murf_prices': murf_prices,
            'murf_kta_prices': murf_kta_prices,  # Add MURF-KTA exchange rates
            'market_caps': market_caps,
            'count': len(history)
        }
    
    def cleanup_old_data(self, days_to_keep=7):
        """Clean up old data to keep database size manageable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM price_history 
            WHERE created_at < datetime('now', '-{} days')
        '''.format(days_to_keep))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_latest_price_data(self):
        """Get the latest price data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, kta_price_usd, murf_kta_price, murf_usd_price,
                   exchange_rate_murf, murf_fdv, murf_marketcap, type_7_count, last_trade_hash
            FROM price_history 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'timestamp': result[0],
                'kta_price_usd': result[1],
                'murf_kta_price': result[2],
                'murf_usd_price': result[3],
                'exchange_rate_murf': result[4],
                'murf_fdv': result[5],
                'murf_marketcap': result[6],
                'type_7_count': result[7],
                'last_trade_hash': result[8]
            }
        return None

if __name__ == "__main__":
    # Test the database
    db = PriceHistoryDB()
    
    # Test data
    test_data = {
        'timestamp': datetime.now().isoformat(),
        'kta_price_usd': 0.67,
        'murf_kta_price': 0.000007,
        'murf_usd_price': 0.0000047,
        'exchange_rate_murf': 141492,
        'murf_fdv': 4700,
        'murf_marketcap': 4700,
        'type_7_count': 1,
        'last_trade_hash': 'test_hash'
    }
    
    db.save_price_data(test_data)
    print("✅ Test data saved")
    
    history = db.get_price_history(5)
    print(f"📊 Retrieved {len(history)} records")
    
    chart_data = db.get_chart_data(5)
    print(f"📈 Chart data: {chart_data['count']} points")
