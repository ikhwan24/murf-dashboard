#!/usr/bin/env python3

import sqlite3
import os

def check_databases():
    """Check which databases exist and their contents"""
    databases = ['price_history.db', 'otc_transactions.db']
    
    for db in databases:
        if os.path.exists(db):
            print(f"Database {db} exists")
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"  Tables: {[t[0] for t in tables]}")
            
            # Check price_history table if exists
            if 'price_history' in [t[0] for t in tables]:
                cursor.execute('SELECT COUNT(*) FROM price_history')
                count = cursor.fetchone()[0]
                print(f"  price_history records: {count}")
                
                if count > 0:
                    cursor.execute('SELECT * FROM price_history ORDER BY created_at DESC LIMIT 3')
                    rows = cursor.fetchall()
                    print("  Latest 3 records:")
                    for i, row in enumerate(rows):
                        print(f"    {i+1}. MURF Price: ${row[3]:.8f}, Exchange Rate: {row[5]:,.0f}, Time: {row[1]}")
            
            # Check otc_transactions table if exists
            if 'otc_transactions' in [t[0] for t in tables]:
                cursor.execute('SELECT COUNT(*) FROM otc_transactions')
                count = cursor.fetchone()[0]
                print(f"  otc_transactions records: {count}")
                
                if count > 0:
                    cursor.execute('SELECT * FROM otc_transactions ORDER BY timestamp DESC LIMIT 3')
                    rows = cursor.fetchall()
                    print("  Latest 3 OTC transactions:")
                    for i, row in enumerate(rows):
                        print(f"    {i+1}. {row[2]:.2f} KTA <-> {row[3]:,.0f} MURF (Rate: {row[4]:,.0f})")
            
            conn.close()
            print()
        else:
            print(f"Database {db} does not exist")

if __name__ == "__main__":
    check_databases()
