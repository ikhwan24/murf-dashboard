#!/usr/bin/env python3
"""
Efficient Real-Time MURF Holders Scanner
Uses direct API calls with batch processing for speed
"""

import requests
import sqlite3
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class EfficientAPIHoldersScanner:
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
            response = requests.get(url, timeout=5)
            
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
                return None
                
        except Exception as e:
            return None
    
    def check_address_batch(self, address_batch):
        """Check a batch of addresses"""
        results = []
        for address in address_batch:
            balance = self.get_current_balance(address)
            results.append({
                'address': address,
                'balance': balance if balance is not None else 0,
                'error': balance is None
            })
        return results
    
    def scan_all_holders_efficient(self, batch_size=10, max_workers=5):
        """Scan all holders efficiently with batch processing"""
        print("Efficient Real-Time MURF Holders Scanner")
        print("=" * 60)
        
        # Get all addresses from database
        conn = sqlite3.connect(self.holders_db)
        cursor = conn.cursor()
        cursor.execute('SELECT address FROM murf_holders ORDER BY current_balance DESC')
        addresses = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"Scanning {len(addresses)} holders with batch processing...")
        print(f"Batch size: {batch_size}, Max workers: {max_workers}")
        print()
        
        # Create real-time database
        self.init_real_time_db()
        
        # Split addresses into batches
        address_batches = [addresses[i:i + batch_size] for i in range(0, len(addresses), batch_size)]
        
        real_holders = []
        total_current_balance = 0
        errors = 0
        processed = 0
        
        # Process batches with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all batches
            future_to_batch = {
                executor.submit(self.check_address_batch, batch): batch 
                for batch in address_batches
            }
            
            # Process completed batches
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    results = future.result()
                    
                    for result in results:
                        processed += 1
                        address = result['address']
                        balance = result['balance']
                        error = result['error']
                        
                        print(f"[{processed:4d}/{len(addresses)}] {address[:50]}...")
                        
                        if not error:
                            if balance > 0:
                                real_holders.append({
                                    'address': address,
                                    'current_balance': balance,
                                    'rank': len(real_holders) + 1
                                })
                                total_current_balance += balance
                                print(f"    Current Balance: {balance:,} MURF")
                            else:
                                print(f"    No MURF balance (sold/traded)")
                        else:
                            errors += 1
                            print(f"    Error getting balance")
                        
                        # Small delay
                        time.sleep(0.01)
                        
                except Exception as e:
                    print(f"Batch error: {e}")
                    errors += len(batch)
        
        # Save to real-time database
        self.save_real_time_data(real_holders, total_current_balance)
        
        print(f"\nScan completed!")
        print(f"Processed: {processed}")
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

def main():
    scanner = EfficientAPIHoldersScanner()
    
    print("Starting efficient real-time MURF holders scan...")
    print("This will check current balance of all known holders")
    print("Note: Some holders may have sold their tokens via OTC")
    print()
    
    # Scan all holders
    real_holders, total_balance = scanner.scan_all_holders_efficient()
    
    # Compare with old data
    scanner.compare_with_old_data()
    
    print(f"\nReal-time scan completed!")
    print(f"Active holders: {len(real_holders)}")
    print(f"Total current MURF in circulation: {total_balance:,}")

if __name__ == "__main__":
    main()
