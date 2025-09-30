#!/usr/bin/env python3

import sqlite3

def check_invalid_hashes():
    """Check for invalid hashes in OTC transactions"""
    conn = sqlite3.connect('otc_transactions.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM otc_transactions ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        
        print(f"Total OTC transactions: {len(rows)}")
        print("\nAll transactions:")
        
        for i, row in enumerate(rows):
            print(f"\nTransaction {i+1}:")
            print(f"  ID: {row[0]}")
            print(f"  TX Hash: {row[1]}")
            print(f"  Block Hash: {row[2]}")
            print(f"  KTA Amount: {row[3]}")
            print(f"  MURF Amount: {row[4]}")
            print(f"  Exchange Rate: {row[5]}")
            print(f"  From Address: {row[6]}")
            print(f"  To Address: {row[7]}")
            print(f"  Timestamp: {row[8]}")
            
            # Check if hash looks valid (should be 64 characters hex)
            tx_hash = row[1]
            if len(tx_hash) != 64 or not all(c in '0123456789ABCDEF' for c in tx_hash):
                print(f"  *** INVALID HASH: {tx_hash}")
            else:
                print(f"  Valid hash: {tx_hash[:20]}...")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_invalid_hashes()
