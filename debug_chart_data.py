#!/usr/bin/env python3
"""
Debug Chart Data
"""

import sqlite3
from price_history_db import PriceHistoryDB

def debug_chart_data():
    print("Debugging Chart Data...")
    
    # Check database directly
    try:
        conn = sqlite3.connect('price_history.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='price_history'")
        table_exists = cursor.fetchone()
        print(f"Table exists: {table_exists is not None}")
        
        if table_exists:
            # Count records
            cursor.execute('SELECT COUNT(*) FROM price_history')
            count = cursor.fetchone()[0]
            print(f"Total records: {count}")
            
            if count > 0:
                # Get latest 5 records
                cursor.execute('SELECT timestamp, murf_usd_price, kta_price_usd FROM price_history ORDER BY timestamp DESC LIMIT 5')
                records = cursor.fetchall()
                print("Latest 5 records:")
                for i, (timestamp, murf_price, kta_price) in enumerate(records):
                    print(f"  {i+1}. {timestamp}: MURF=${murf_price:.8f}, KTA=${kta_price:.6f}")
            else:
                print("No data in database!")
        else:
            print("Table doesn't exist!")
            
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")
    
    # Check chart data from PriceHistoryDB
    try:
        db = PriceHistoryDB()
        chart_data = db.get_chart_data(50)
        
        print(f"\nChart Data from PriceHistoryDB:")
        print(f"  MURF Prices: {len(chart_data.get('murf_prices', []))} points")
        print(f"  KTA Prices: {len(chart_data.get('kta_prices', []))} points")
        print(f"  Timestamps: {len(chart_data.get('timestamps', []))} points")
        
        if chart_data.get('murf_prices'):
            print(f"  Latest MURF Price: ${chart_data['murf_prices'][-1]:.8f}")
            print(f"  First MURF Price: ${chart_data['murf_prices'][0]:.8f}")
            
    except Exception as e:
        print(f"PriceHistoryDB error: {e}")

if __name__ == "__main__":
    debug_chart_data()
