#!/usr/bin/env python3

import sqlite3

def check_hash_validity():
    """Check which hashes are still invalid"""
    conn = sqlite3.connect('otc_transactions.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT tx_hash FROM otc_transactions')
        hashes = cursor.fetchall()
        
        print('Checking all hashes:')
        for i, hash_row in enumerate(hashes):
            tx_hash = hash_row[0]
            is_valid = len(tx_hash) == 64 and all(c in '0123456789ABCDEF' for c in tx_hash)
            print(f'{i+1}. {tx_hash[:20]}... - {"VALID" if is_valid else "INVALID"}')
            if not is_valid:
                invalid_chars = set(tx_hash) - set('0123456789ABCDEF')
                print(f'   Problem: len={len(tx_hash)}, invalid chars: {invalid_chars}')
        
    except Exception as e:
        print(f'Error: {e}')
    finally:
        conn.close()

if __name__ == "__main__":
    check_hash_validity()
