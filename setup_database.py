#!/usr/bin/env python3
"""
Setup Database untuk MURF Dashboard
Membuat database dan data sample untuk testing
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random

def setup_database():
    """Setup database dengan data sample"""
    print("🔧 Setting up MURF Token Database...")
    
    # Connect to database
    conn = sqlite3.connect("keeta_trades.db")
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            block_hash TEXT,
            from_address TEXT,
            to_address TEXT,
            token_id TEXT,
            amount_hex TEXT,
            amount_decimal REAL,
            price_usd REAL,
            trade_type TEXT,
            operation_type INTEGER,
            is_otc BOOLEAN DEFAULT 0,
            otc_from_address TEXT,
            otc_exact BOOLEAN DEFAULT 0,
            otc_type TEXT,
            trade_pair TEXT,
            settlement_time TEXT,
            network TEXT,
            signer TEXT,
            exchange_ratio REAL,
            counterpart_amount REAL,
            counterpart_token TEXT,
            related_operations TEXT,
            raw_operation TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            token_id TEXT,
            price REAL,
            volume REAL
        )
    ''')
    
    # Clear existing data
    cursor.execute('DELETE FROM trades')
    cursor.execute('DELETE FROM price_history')
    
    # Insert sample data
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
    
    # Generate sample trades
    base_time = datetime.now() - timedelta(days=5)
    
    for i in range(20):
        trade_time = base_time + timedelta(hours=i*6)
        
        # MURF trade
        murf_amount = random.randint(1000000, 50000000)
        cursor.execute('''
            INSERT INTO trades (
                timestamp, block_hash, from_address, to_address, token_id,
                amount_hex, amount_decimal, trade_type, operation_type, is_otc,
                otc_from_address, otc_exact, otc_type, trade_pair, settlement_time,
                network, signer, exchange_ratio, counterpart_amount, counterpart_token,
                related_operations, raw_operation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_time.isoformat(),
            f"block_{i:06x}",
            f"keeta_from_{i:03d}",
            f"keeta_to_{i:03d}",
            murf_token,
            hex(murf_amount),
            murf_amount,
            "transfer" if i % 3 != 0 else "otc_trade",
            0 if i % 3 != 0 else 7,
            i % 3 == 0,
            f"keeta_otc_{i:03d}" if i % 3 == 0 else "",
            i % 3 == 0,
            "swap" if i % 3 == 0 else "",
            f"{murf_token[:20]}..." if i % 3 == 0 else "",
            trade_time.isoformat() if i % 3 == 0 else "",
            "0x5382",
            f"keeta_signer_{i:03d}",
            250000.0 if i % 3 == 0 else 0,
            murf_amount / 250000 if i % 3 == 0 else 0,
            kta_token if i % 3 == 0 else "",
            json.dumps([]),
            json.dumps({})
        ))
        
        # KTA trade (counterpart)
        if i % 3 == 0:  # OTC trades
            kta_amount = murf_amount / 250000
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, block_hash, from_address, to_address, token_id,
                    amount_hex, amount_decimal, trade_type, operation_type, is_otc,
                    otc_from_address, otc_exact, otc_type, trade_pair, settlement_time,
                    network, signer, exchange_ratio, counterpart_amount, counterpart_token,
                    related_operations, raw_operation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_time.isoformat(),
                f"block_{i:06x}",
                f"keeta_from_{i:03d}",
                f"keeta_to_{i:03d}",
                kta_token,
                hex(int(kta_amount)),
                kta_amount,
                "transfer",
                0,
                False,
                "",
                False,
                "",
                "",
                "",
                "0x5382",
                f"keeta_signer_{i:03d}",
                0,
                0,
                "",
                json.dumps([]),
                json.dumps({})
            ))
    
    # Generate price history
    base_price = 0.00000263
    for i in range(5):
        date = base_time + timedelta(days=i)
        price = base_price * (1 + random.uniform(-0.3, 0.3))
        price = max(0.0000001, price)
        
        cursor.execute('''
            INSERT INTO price_history (timestamp, token_id, price, volume)
            VALUES (?, ?, ?, ?)
        ''', (
            date.isoformat(),
            murf_token,
            price,
            random.randint(1000000, 10000000)
        ))
    
    conn.commit()
    conn.close()
    
    print("✅ Database setup completed!")
    print("📊 Sample data generated:")
    print("   - 20 MURF trades")
    print("   - 7 OTC trades (type 7)")
    print("   - 5 days price history")
    print("   - Exchange rate: 1 KTA = 250,000 MURF")

def main():
    """Main function"""
    try:
        setup_database()
        print("\n🚀 Database ready! You can now run:")
        print("   python dashboard.py")
        print("   python web_dashboard.py")
        print("   python run_dashboard.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
