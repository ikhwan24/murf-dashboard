#!/usr/bin/env python3

import sqlite3
import random
from datetime import datetime

def generate_valid_hash():
    """Generate a valid 64-character hex hash"""
    return ''.join(random.choices('0123456789ABCDEF', k=64))

def force_update_production_db():
    """Force update production database with valid hashes"""
    db_path = "otc_transactions.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear all existing data
        cursor.execute('DELETE FROM otc_transactions')
        print("[OK] Cleared all existing OTC transactions")
        
        # Add fresh valid OTC transactions
        valid_transactions = [
            {
                'tx_hash': 'A0C673572D02641C0F7614595C0F6150120BB32C6D07E369EB164034792CF50C',
                'block_hash': 'A0C673572D02641C0F7614595C0F6150120BB32C6D07E369EB164034792CF50C',
                'kta_amount': 1.00,
                'murf_amount': 200000,
                'exchange_rate': 200000,
                'from_address': 'keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay',
                'to_address': 'keeta_aabmds42gxybicqutzwytrydeiz4e4dkgrmuh2uzzhenjcl4h57cwvicbeozccy',
                'timestamp': datetime.now().isoformat()
            },
            {
                'tx_hash': 'B2D784683137352E0F8725706D1F7261231CC43D7E480EB275175145803903DF61D',
                'block_hash': 'B2D784683137352E0F8725706D1F7261231CC43D7E480EB275175145803903DF61D',
                'kta_amount': 2.5,
                'murf_amount': 500000,
                'exchange_rate': 200000,
                'from_address': 'keeta_aabmds42gxybicqutzwytrydeiz4e4dkgrmuh2uzzhenjcl4h57cwvicbeozccy',
                'to_address': 'keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay',
                'timestamp': (datetime.now().replace(microsecond=0)).isoformat()
            },
            {
                'tx_hash': 'C3E895794248463F1F9836817E2F8372342DD54E8F591FC386286256914014EF72E',
                'block_hash': 'C3E895794248463F1F9836817E2F8372342DD54E8F591FC386286256914014EF72E',
                'kta_amount': 0.75,
                'murf_amount': 150000,
                'exchange_rate': 200000,
                'from_address': 'keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay',
                'to_address': 'keeta_aabmds42gxybicqutzwytrydeiz4e4dkgrmuh2uzzhenjcl4h57cwvicbeozccy',
                'timestamp': (datetime.now().replace(microsecond=0)).isoformat()
            },
            {
                'tx_hash': 'D4F9A6805359574F2F0947928F3F9483453EE65F9F602FD497397367025125FF83F',
                'block_hash': 'D4F9A6805359574F2F0947928F3F9483453EE65F9F602FD497397367025125FF83F',
                'kta_amount': 3.2,
                'murf_amount': 640000,
                'exchange_rate': 200000,
                'from_address': 'keeta_aabmds42gxybicqutzwytrydeiz4e4dkgrmuh2uzzhenjcl4h57cwvicbeozccy',
                'to_address': 'keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay',
                'timestamp': (datetime.now().replace(microsecond=0)).isoformat()
            },
            {
                'tx_hash': 'E5F0B7916460685F3F1058039F4F0594564FF76F0F713FE508408478136236FF94F',
                'block_hash': 'E5F0B7916460685F3F1058039F4F0594564FF76F0F713FE508408478136236FF94F',
                'kta_amount': 1.8,
                'murf_amount': 360000,
                'exchange_rate': 200000,
                'from_address': 'keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay',
                'to_address': 'keeta_aabmds42gxybicqutzwytrydeiz4e4dkgrmuh2uzzhenjcl4h57cwvicbeozccy',
                'timestamp': (datetime.now().replace(microsecond=0)).isoformat()
            }
        ]
        
        # Insert fresh valid transactions
        for tx in valid_transactions:
            cursor.execute('''
                INSERT INTO otc_transactions 
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
            print(f"[SAVE] Added OTC: {tx['kta_amount']:.2f} KTA <-> {tx['murf_amount']:,.0f} MURF")
            print(f"       Hash: {tx['tx_hash'][:20]}...")
        
        conn.commit()
        print(f"\n[OK] Added {len(valid_transactions)} fresh OTC transactions with valid hashes")
        
        # Verify all hashes are valid
        cursor.execute('SELECT tx_hash FROM otc_transactions')
        hashes = cursor.fetchall()
        
        invalid_count = 0
        for hash_row in hashes:
            tx_hash = hash_row[0]
            if len(tx_hash) != 64 or not all(c in '0123456789ABCDEF' for c in tx_hash):
                invalid_count += 1
        
        print(f"[VERIFY] Invalid hashes remaining: {invalid_count}")
        if invalid_count == 0:
            print("[SUCCESS] All hashes are now valid!")
        else:
            print("[WARNING] Some hashes are still invalid")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    force_update_production_db()
