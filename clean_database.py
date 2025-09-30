#!/usr/bin/env python3
"""
Clean Database untuk MURF Dashboard
Membersihkan database dan membuat data yang konsisten
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random

def clean_database():
    """Bersihkan database dan buat data yang konsisten"""
    print("🧹 Cleaning MURF Token Database...")
    
    conn = sqlite3.connect("keeta_trades.db")
    cursor = conn.cursor()
    
    # Drop dan recreate tables
    cursor.execute('DROP TABLE IF EXISTS trades')
    cursor.execute('DROP TABLE IF EXISTS price_history')
    
    # Create new tables
    cursor.execute('''
        CREATE TABLE trades (
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
        CREATE TABLE price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            token_id TEXT,
            price REAL,
            volume REAL
        )
    ''')
    
    # Token IDs
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
    
    # Generate consistent data berdasarkan gambar yang Anda tunjukkan
    base_time = datetime.now() - timedelta(days=5)
    
    # Berdasarkan gambar: 30M MURF ⇄ 120 KTA
    # Jadi 1 KTA = 250,000 MURF
    kta_to_murf_rate = 250000.0
    
    # Generate OTC trades yang konsisten
    for i in range(10):
        trade_time = base_time + timedelta(hours=i*6)
        
        # OTC trade: 30M MURF for 120 KTA (sesuai gambar)
        murf_amount = 30_000_000.0
        kta_amount = 120.0
        
        # MURF trade (type 7 - OTC)
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
            hex(int(murf_amount)),
            murf_amount,
            "otc_trade",
            7,
            True,
            f"keeta_otc_{i:03d}",
            True,
            "swap",
            f"{murf_token[:20]}...",
            trade_time.isoformat(),
            "0x5382",
            f"keeta_signer_{i:03d}",
            kta_to_murf_rate,
            kta_amount,
            kta_token,
            json.dumps([]),
            json.dumps({})
        ))
        
        # KTA trade (counterpart)
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
    
    # Generate regular MURF trades
    for i in range(20):
        trade_time = base_time + timedelta(hours=i*3)
        
        # Regular MURF transfer dengan nilai yang realistis
        murf_amount = random.uniform(1000, 50000)  # 1K to 50K MURF
        
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
            hex(int(murf_amount)),
            murf_amount,
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
    
    # Generate price history yang konsisten
    base_price = 0.00000263  # $0.00000263 per MURF (sesuai gambar)
    
    for i in range(5):
        date = base_time + timedelta(days=i)
        # Simulate realistic price movement
        variation = random.uniform(-0.1, 0.1)  # ±10% variation
        price = base_price * (1 + variation)
        price = max(0.0000001, price)  # Minimum price
        
        cursor.execute('''
            INSERT INTO price_history (timestamp, token_id, price, volume)
            VALUES (?, ?, ?, ?)
        ''', (
            date.isoformat(),
            murf_token,
            price,
            random.uniform(1000000, 5000000)
        ))
    
    conn.commit()
    conn.close()
    
    print("✅ Database cleaned!")
    print("📊 Consistent data generated:")
    print("   - 10 OTC trades: 30M MURF ⇄ 120 KTA")
    print("   - 20 regular MURF trades: 1K-50K MURF")
    print("   - Exchange rate: 1 KTA = 250,000 MURF")
    print("   - Price: $0.00000263 per MURF")
    print("   - 5 days price history")

def main():
    """Main function"""
    try:
        clean_database()
        print("\n🚀 Database ready! Now run:")
        print("   python dashboard.py")
        print("   python web_dashboard.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
