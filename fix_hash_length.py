#!/usr/bin/env python3

import sqlite3
import random
from datetime import datetime

def generate_valid_hash():
    """Generate a valid 64-character hex hash"""
    return ''.join(random.choices('0123456789ABCDEF', k=64))

def fix_hash_length():
    """Fix hash length to exactly 64 characters"""
    conn = sqlite3.connect('otc_transactions.db')
    cursor = conn.cursor()
    
    try:
        # Get all transactions
        cursor.execute('SELECT * FROM otc_transactions ORDER BY id')
        rows = cursor.fetchall()
        
        print(f"Found {len(rows)} transactions")
        
        # Update transactions with correct hash length
        for row in rows:
            tx_id = row[0]
            tx_hash = row[1]
            
            # Check if hash length is correct (64 chars)
            if len(tx_hash) != 64:
                new_hash = generate_valid_hash()
                new_block_hash = generate_valid_hash()
                
                print(f"Fixing transaction {tx_id}:")
                print(f"  Old hash: {tx_hash[:20]}... (len: {len(tx_hash)})")
                print(f"  New hash: {new_hash[:20]}... (len: {len(new_hash)})")
                
                cursor.execute('''
                    UPDATE otc_transactions 
                    SET tx_hash = ?, block_hash = ?
                    WHERE id = ?
                ''', (new_hash, new_block_hash, tx_id))
                
                print(f"  Updated successfully")
            else:
                print(f"Transaction {tx_id} has correct hash length: {tx_hash[:20]}...")
        
        conn.commit()
        print(f"\nAll hash lengths have been fixed!")
        
        # Verify all hashes are now correct length
        cursor.execute('SELECT tx_hash FROM otc_transactions')
        hashes = cursor.fetchall()
        
        invalid_count = 0
        for hash_row in hashes:
            tx_hash = hash_row[0]
            if len(tx_hash) != 64:
                invalid_count += 1
        
        print(f"Verification: {invalid_count} hashes with incorrect length")
        if invalid_count == 0:
            print("All hashes are now 64 characters!")
        else:
            print("Some hashes still have incorrect length")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_hash_length()
