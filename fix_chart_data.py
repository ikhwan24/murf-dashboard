#!/usr/bin/env python3
"""
Fix Chart Data - Add sample data for testing
"""

import sqlite3
from datetime import datetime, timedelta
import random

def fix_chart_data():
    print("Fixing Chart Data...")
    
    try:
        conn = sqlite3.connect('price_history.db')
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM price_history')
        print("Cleared existing data")
        
        # Add sample data for the last 2 hours (every 5 minutes)
        base_time = datetime.now() - timedelta(hours=2)
        base_murf_price = 0.00000500  # Starting price
        base_kta_price = 0.670000     # Starting KTA price
        
        for i in range(25):  # 25 data points (2 hours / 5 minutes)
            # Calculate time
            current_time = base_time + timedelta(minutes=i*5)
            
            # Simulate price movement (small random changes)
            price_change = random.uniform(-0.0000001, 0.0000001)
            base_murf_price += price_change
            base_kta_price += random.uniform(-0.01, 0.01)
            
            # Ensure positive prices
            base_murf_price = max(base_murf_price, 0.000001)
            base_kta_price = max(base_kta_price, 0.5)
            
            # Calculate derived values
            exchange_rate = 1 / base_murf_price if base_murf_price > 0 else 200000
            murf_fdv = base_murf_price * 1000000000000  # 1T supply
            murf_marketcap = base_murf_price * 60000000000  # 60B circulation
            
            # Insert data
            cursor.execute('''
                INSERT INTO price_history 
                (timestamp, kta_price_usd, murf_kta_price, murf_usd_price, 
                 exchange_rate_murf, murf_fdv, murf_marketcap, type_7_count, last_trade_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                current_time.isoformat(),
                base_kta_price,
                base_murf_price,
                base_murf_price,
                exchange_rate,
                murf_fdv,
                murf_marketcap,
                1,  # type_7_count
                f"sample_hash_{i:03d}"
            ))
        
        conn.commit()
        print(f"Added 25 sample data points")
        
        # Verify data
        cursor.execute('SELECT COUNT(*) FROM price_history')
        count = cursor.fetchone()[0]
        print(f"Total records: {count}")
        
        # Show latest 3 records
        cursor.execute('SELECT timestamp, murf_usd_price, kta_price_usd FROM price_history ORDER BY timestamp DESC LIMIT 3')
        records = cursor.fetchall()
        print("Latest 3 records:")
        for i, (timestamp, murf_price, kta_price) in enumerate(records):
            print(f"  {i+1}. {timestamp}: MURF=${murf_price:.8f}, KTA=${kta_price:.6f}")
        
        conn.close()
        print("Chart data fixed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_chart_data()
