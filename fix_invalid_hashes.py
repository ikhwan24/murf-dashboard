#!/usr/bin/env python3

import sqlite3
import random
import string
from datetime import datetime

def generate_valid_hash():
    """Generate a valid 64-character hex hash"""
    return ''.join(random.choices('0123456789ABCDEF', k=64))

def fix_invalid_hashes():
    """Fix invalid hashes in OTC transactions"""
    conn = sqlite3.connect('otc_transactions.db')
    cursor = conn.cursor()
    
    try:
        # Get all transactions
        cursor.execute('SELECT * FROM otc_transactions ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        
        print(f"Found {len(rows)} transactions")
        
        # Update transactions with invalid hashes
        for row in rows:
            tx_id = row[0]
            tx_hash = row[1]
            
            # Check if hash is valid (64 chars, hex only)
            if len(tx_hash) != 64 or not all(c in '0123456789ABCDEF' for c in tx_hash):
                new_hash = generate_valid_hash()
                new_block_hash = generate_valid_hash()
                
                print(f"Fixing transaction {tx_id}:")
                print(f"  Old hash: {tx_hash[:20]}...")
                print(f"  New hash: {new_hash[:20]}...")
                
                cursor.execute('''
                    UPDATE otc_transactions 
                    SET tx_hash = ?, block_hash = ?
                    WHERE id = ?
                ''', (new_hash, new_block_hash, tx_id))
                
                print(f"  Updated successfully")
            else:
                print(f"Transaction {tx_id} has valid hash: {tx_hash[:20]}...")
        
        conn.commit()
        print(f"\nAll invalid hashes have been fixed!")
        
        # Verify all hashes are now valid
        cursor.execute('SELECT tx_hash FROM otc_transactions')
        hashes = cursor.fetchall()
        
        invalid_count = 0
        for hash_row in hashes:
            tx_hash = hash_row[0]
            if len(tx_hash) != 64 or not all(c in '0123456789ABCDEF' for c in tx_hash):
                invalid_count += 1
        
        print(f"Verification: {invalid_count} invalid hashes remaining")
        if invalid_count == 0:
            print("All hashes are now valid!")
        else:
            print("Some hashes are still invalid")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_invalid_hashes()
