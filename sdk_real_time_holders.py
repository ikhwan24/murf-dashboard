#!/usr/bin/env python3
"""
Real-Time MURF Holders Scanner using KeetaNetSDK
Much faster than API calls - uses SDK for direct balance checking
"""

import sqlite3
import time
from datetime import datetime
from keetanet_client import Client

class SDKRealTimeHoldersScanner:
    def __init__(self):
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.holders_db = "murf_holders.db"
        self.real_time_db = "murf_real_time_holders.db"
        
        # Initialize KeetaNetSDK Client
        print("Initializing KeetaNetSDK Client...")
        self.client = Client.fromNetwork('main')
        
    def get_current_balance_sdk(self, address):
        """Get current MURF balance using KeetaNetSDK"""
        try:
            # Use getBalance method from SDK
            balance = self.client.getBalance(address, self.murf_token)
            return int(balance) if balance else 0
        except Exception as e:
            print(f"SDK Error for {address}: {e}")
            return None
    
    def get_account_info_sdk(self, address):
        """Get full account info using KeetaNetSDK"""
        try:
            account_info = self.client.getAccountInfo(address)
            balances = account_info.get('balances', [])
            
            # Find MURF token balance
            for balance in balances:
                if balance.get('token') == self.murf_token:
                    hex_balance = balance.get('balance', '0x0')
                    return int(hex_balance, 16) if hex_balance.startswith('0x') else int(hex_balance)
            
            return 0  # No MURF token found
        except Exception as e:
            print(f"SDK Error for {address}: {e}")
            return None
    
    def scan_all_holders_sdk(self):
        """Scan all known holders using KeetaNetSDK"""
        print("Real-Time MURF Holders Scanner (KeetaNetSDK)")
        print("=" * 60)
        
        # Get all addresses from database
        conn = sqlite3.connect(self.holders_db)
        cursor = conn.cursor()
        cursor.execute('SELECT address FROM murf_holders ORDER BY current_balance DESC')
        addresses = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"Scanning {len(addresses)} holders using KeetaNetSDK...")
        print("This is much faster than API calls!")
        print()
        
        # Create real-time database
        self.init_real_time_db()
        
        real_holders = []
        total_current_balance = 0
        errors = 0
        
        for i, address in enumerate(addresses, 1):
            print(f"[{i:4d}/{len(addresses)}] Checking {address[:50]}...")
            
            # Try getBalance first (faster)
            current_balance = self.get_current_balance_sdk(address)
            
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
                errors += 1
                print(f"    Error getting balance")
            
            # Small delay to avoid overwhelming the network
            time.sleep(0.05)
        
        # Save to real-time database
        self.save_real_time_data(real_holders, total_current_balance)
        
        print(f"\nScan completed!")
        print(f"Active holders: {len(real_holders)}")
        print(f"Errors: {errors}")
        print(f"Total current MURF: {total_current_balance:,}")
        
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
        
        print(f"\nReal-time data saved to database")
    
    def compare_with_old_data(self):
        """Compare real-time data with old database"""
        print("\n" + "=" * 60)
        print("COMPARISON: Old vs Real-Time Data")
        print("=" * 60)
        
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
        print("-" * 90)
        print(f"{'Rank':<4} {'Address':<50} {'Old Balance':<15} {'New Balance':<15} {'Change':<10}")
        print("-" * 90)
        
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
    
    def cleanup(self):
        """Clean up SDK client"""
        try:
            self.client.destroy()
        except:
            pass

def main():
    scanner = SDKRealTimeHoldersScanner()
    
    try:
        print("Starting real-time MURF holders scan using KeetaNetSDK...")
        print("This will check current balance of all known holders")
        print("Note: Some holders may have sold their tokens via OTC")
        print()
        
        # Scan all holders
        real_holders, total_balance = scanner.scan_all_holders_sdk()
        
        # Compare with old data
        scanner.compare_with_old_data()
        
        print(f"\nReal-time scan completed!")
        print(f"Active holders: {len(real_holders)}")
        print(f"Total current MURF in circulation: {total_balance:,}")
        
    finally:
        # Clean up
        scanner.cleanup()

if __name__ == "__main__":
    main()
