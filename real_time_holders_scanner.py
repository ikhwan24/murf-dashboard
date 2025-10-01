#!/usr/bin/env python3
"""
Real-Time MURF Holders Scanner
Check current balance of all known holders using Keeta API
"""

import requests
import sqlite3
import time
from datetime import datetime

class RealTimeHoldersScanner:
    def __init__(self):
        self.api_base = "https://rep2.main.network.api.keeta.com/api/node/ledger/account"
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.holders_db = "murf_holders.db"
        self.real_time_db = "murf_real_time_holders.db"
        
    def hex_to_decimal(self, hex_str):
        """Convert hex string to decimal"""
        try:
            return int(hex_str, 16)
        except:
            return 0
    
    def get_current_balance(self, address):
        """Get current MURF balance for an address"""
        try:
            url = f"{self.api_base}/{address}/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                balances = data.get('balances', [])
                
                # Find MURF token balance
                for balance in balances:
                    if balance.get('token') == self.murf_token:
                        hex_balance = balance.get('balance', '0x0')
                        return self.hex_to_decimal(hex_balance)
                
                return 0  # No MURF token found
            else:
                print(f"API Error for {address}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error checking {address}: {e}")
            return None
    
    def scan_all_holders(self):
        """Scan all known holders for current balance"""
        print("Real-Time MURF Holders Scanner")
        print("=" * 50)
        
        # Get all addresses from database
        conn = sqlite3.connect(self.holders_db)
        cursor = conn.cursor()
        cursor.execute('SELECT address FROM murf_holders ORDER BY current_balance DESC')
        addresses = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"Scanning {len(addresses)} holders for current MURF balance...")
        
        # Create real-time database
        self.init_real_time_db()
        
        real_holders = []
        total_current_balance = 0
        
        for i, address in enumerate(addresses, 1):
            print(f"[{i:4d}/{len(addresses)}] Checking {address[:50]}...")
            
            current_balance = self.get_current_balance(address)
            
            if current_balance is not None:
                if current_balance > 0:
                    real_holders.append({
                        'address': address,
                        'current_balance': current_balance,
                        'rank': len(real_holders) + 1
                    })
                    total_current_balance += current_balance
                    print(f"    Current Balance: {current_balance:,} MURF")
                else:
                    print(f"    No MURF balance (sold/traded)")
            else:
                print(f"    Error getting balance")
            
            # Rate limiting
            time.sleep(0.1)
        
        # Save to real-time database
        self.save_real_time_data(real_holders, total_current_balance)
        
        return real_holders, total_current_balance
    
    def init_real_time_db(self):
        """Initialize real-time holders database"""
        conn = sqlite3.connect(self.real_time_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS real_time_holders (
                address TEXT PRIMARY KEY,
                current_balance INTEGER,
                rank INTEGER,
                last_checked TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_real_time_data(self, holders, total_balance):
        """Save real-time data to database"""
        conn = sqlite3.connect(self.real_time_db)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM real_time_holders')
        
        # Insert new data
        for holder in holders:
            cursor.execute('''
                INSERT INTO real_time_holders (address, current_balance, rank, last_checked)
                VALUES (?, ?, ?, ?)
            ''', (
                holder['address'],
                holder['current_balance'],
                holder['rank'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        print(f"\nReal-time data saved:")
        print(f"Active holders: {len(holders)}")
        print(f"Total current balance: {total_balance:,} MURF")
    
    def compare_with_old_data(self):
        """Compare real-time data with old database"""
        print("\n" + "=" * 50)
        print("COMPARISON: Old vs Real-Time Data")
        print("=" * 50)
        
        # Get old data
        conn_old = sqlite3.connect(self.holders_db)
        cursor_old = conn_old.cursor()
        cursor_old.execute('SELECT address, current_balance FROM murf_holders ORDER BY current_balance DESC LIMIT 10')
        old_data = {row[0]: row[1] for row in cursor_old.fetchall()}
        conn_old.close()
        
        # Get real-time data
        conn_new = sqlite3.connect(self.real_time_db)
        cursor_new = conn_new.cursor()
        cursor_new.execute('SELECT address, current_balance FROM real_time_holders ORDER BY current_balance DESC LIMIT 10')
        new_data = {row[0]: row[1] for row in cursor_new.fetchall()}
        conn_new.close()
        
        print("Top 10 Holders Comparison:")
        print("-" * 80)
        print(f"{'Rank':<4} {'Address':<50} {'Old Balance':<15} {'New Balance':<15} {'Change':<10}")
        print("-" * 80)
        
        for i, address in enumerate(list(new_data.keys())[:10], 1):
            old_balance = old_data.get(address, 0)
            new_balance = new_data.get(address, 0)
            change = new_balance - old_balance
            
            print(f"{i:<4} {address[:50]:<50} {old_balance:<15,} {new_balance:<15,} {change:+,}")
        
        # Find holders who sold all tokens
        sold_all = []
        for address in old_data:
            if address not in new_data or new_data[address] == 0:
                sold_all.append((address, old_data[address]))
        
        if sold_all:
            print(f"\nHolders who sold all MURF ({len(sold_all)}):")
            for address, old_balance in sold_all[:5]:  # Show first 5
                print(f"  {address[:50]}... (had {old_balance:,} MURF)")

def main():
    scanner = RealTimeHoldersScanner()
    
    print("Starting real-time MURF holders scan...")
    print("This will check current balance of all known holders")
    print("Note: Some holders may have sold their tokens via OTC")
    print()
    
    # Scan all holders
    real_holders, total_balance = scanner.scan_all_holders()
    
    # Compare with old data
    scanner.compare_with_old_data()
    
    print(f"\nReal-time scan completed!")
    print(f"Active holders: {len(real_holders)}")
    print(f"Total current MURF in circulation: {total_balance:,}")

if __name__ == "__main__":
    main()
