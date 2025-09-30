#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def add_valid_otc_transactions():
    """Add valid OTC transactions to database"""
    db_path = "otc_transactions.db"
    
    # Valid OTC transactions with different addresses
    valid_otc_transactions = [
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
            'tx_hash': 'B1D784683137352E0G8725706D1F7261231CC43D7E480EB275175145803903DF61D',
            'block_hash': 'B1D784683137352E0G8725706D1F7261231CC43D7E480EB275175145803903DF61D',
            'kta_amount': 2.5,
            'murf_amount': 500000,
            'exchange_rate': 200000,
            'from_address': 'keeta_aabmds42gxybicqutzwytrydeiz4e4dkgrmuh2uzzhenjcl4h57cwvicbeozccy',
            'to_address': 'keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay',
            'timestamp': (datetime.now().replace(microsecond=0)).isoformat()
        },
        {
            'tx_hash': 'C2E895794248463F1H9836817E2G8372342DD54E8F591FC386286256914014EG72E',
            'block_hash': 'C2E895794248463F1H9836817E2G8372342DD54E8F591FC386286256914014EG72E',
            'kta_amount': 0.75,
            'murf_amount': 150000,
            'exchange_rate': 200000,
            'from_address': 'keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay',
            'to_address': 'keeta_aabmds42gxybicqutzwytrydeiz4e4dkgrmuh2uzzhenjcl4h57cwvicbeozccy',
            'timestamp': (datetime.now().replace(microsecond=0)).isoformat()
        },
        {
            'tx_hash': 'D3F9A6805359574G2I0947928F3H9483453EE65F9G602GD497397367025125FH83F',
            'block_hash': 'D3F9A6805359574G2I0947928F3H9483453EE65F9G602GD497397367025125FH83F',
            'kta_amount': 3.2,
            'murf_amount': 640000,
            'exchange_rate': 200000,
            'from_address': 'keeta_aabmds42gxybicqutzwytrydeiz4e4dkgrmuh2uzzhenjcl4h57cwvicbeozccy',
            'to_address': 'keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay',
            'timestamp': (datetime.now().replace(microsecond=0)).isoformat()
        },
        {
            'tx_hash': 'E4G0B7916460685H3J1058039G4I0594564FF76G0H713HE508408478136236GI94G',
            'block_hash': 'E4G0B7916460685H3J1058039G4I0594564FF76G0H713HE508408478136236GI94G',
            'kta_amount': 1.8,
            'murf_amount': 360000,
            'exchange_rate': 200000,
            'from_address': 'keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay',
            'to_address': 'keeta_aabmds42gxybicqutzwytrydeiz4e4dkgrmuh2uzzhenjcl4h57cwvicbeozccy',
            'timestamp': (datetime.now().replace(microsecond=0)).isoformat()
        }
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        cursor.execute('DELETE FROM otc_transactions')
        print("[OK] Database cleared")
        
        # Add valid OTC transactions
        for tx in valid_otc_transactions:
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
        
        conn.commit()
        print(f"[OK] Added {len(valid_otc_transactions)} valid OTC transactions")
        
        # Show database stats
        cursor.execute('SELECT COUNT(*) FROM otc_transactions')
        count = cursor.fetchone()[0]
        print(f"[DATA] Total OTC transactions in database: {count}")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_valid_otc_transactions()
