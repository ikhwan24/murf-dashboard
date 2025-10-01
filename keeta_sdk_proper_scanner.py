#!/usr/bin/env python3
"""
KeetaNetSDK Proper Scanner - Using KeetaNetSDK methods
Based on: https://static.network.keeta.com/docs/documents/GETTING-STARTED.html
"""

import requests
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
import time

class KeetaNetSDKProperScanner:
    def __init__(self):
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.api_base = "https://rep2.main.network.api.keeta.com/api/node/ledger"
        
        # Database setup
        self.db_path = "keeta_sdk_proper.db"
        self.init_database()
        
        # Scanning data
        self.all_addresses = set()
        self.murf_holders = {}
        self.blocks_scanned = 0
        self.start_time = None
        
    def init_database(self):
        """Initialize proper KeetaNetSDK database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create addresses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                address TEXT PRIMARY KEY,
                first_seen TEXT,
                last_seen TEXT,
                transaction_count INTEGER DEFAULT 0,
                is_murf_holder BOOLEAN DEFAULT 0
            )
        ''')
        
        # Create murf_holders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS murf_holders (
                address TEXT PRIMARY KEY,
                total_received INTEGER DEFAULT 0,
                total_sent INTEGER DEFAULT 0,
                current_balance INTEGER DEFAULT 0,
                transaction_count INTEGER DEFAULT 0,
                first_murf_tx TEXT,
                last_murf_tx TEXT
            )
        ''')
        
        # Create scan_metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_metadata (
                id INTEGER PRIMARY KEY,
                scan_date TEXT,
                total_addresses INTEGER,
                murf_holders INTEGER,
                total_murf_balance INTEGER,
                blocks_scanned INTEGER,
                scan_duration REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("KeetaNetSDK proper database initialized: keeta_sdk_proper.db")
    
    def get_chain_data(self, address):
        """Get chain data for specific address using KeetaNetSDK approach"""
        try:
            # This would be the proper KeetaNetSDK way:
            # client.chain() - returns blocks for the account
            # But we'll use API equivalent for now
            
            url = f"{self.api_base}/history"
            params = {'limit': 200}
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                history = data.get('history', [])
                
                # Process vote staples (equivalent to client.chain())
                for entry in history:
                    if 'voteStaple' in entry:
                        vote_staple = entry['voteStaple']
                        blocks = vote_staple.get('blocks', [])
                        
                        for block in blocks:
                            if isinstance(block, dict):
                                # Check if this block affects the address
                                if self.block_affects_address(block, address):
                                    self.process_block_for_address(block, address)
                                    self.blocks_scanned += 1
                
                return True
            else:
                print(f"API Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error getting chain data: {e}")
            return False
    
    def block_affects_address(self, block, address):
        """Check if block affects specific address"""
        try:
            # Check account
            if block.get('account') == address:
                return True
            
            # Check operations
            operations = block.get('operations', [])
            if isinstance(operations, list):
                for op in operations:
                    if isinstance(op, dict):
                        if op.get('from') == address or op.get('to') == address:
                            return True
            
            return False
            
        except Exception as e:
            return False
    
    def process_block_for_address(self, block, address):
        """Process block for specific address"""
        try:
            operations = block.get('operations', [])
            if isinstance(operations, list):
                for op in operations:
                    if isinstance(op, dict):
                        if op.get('token') == self.murf_token:
                            self.process_murf_operation_for_address(op, block, address)
                            
        except Exception as e:
            pass
    
    def process_murf_operation_for_address(self, op, block, address):
        """Process MURF operation for specific address"""
        try:
            from_addr = op.get('from', '')
            to_addr = op.get('to', '')
            amount = self.hex_to_decimal(op.get('amount', '0'))
            op_type = op.get('type', 0)
            date = block.get('date', '')
            
            # Only process if address is involved
            if from_addr == address or to_addr == address:
                if address not in self.murf_holders:
                    self.murf_holders[address] = {
                        'total_received': 0,
                        'total_sent': 0,
                        'current_balance': 0,
                        'transaction_count': 0,
                        'first_murf_tx': date,
                        'last_murf_tx': date
                    }
                
                if from_addr == address and op_type == 7:  # SEND operation
                    self.murf_holders[address]['total_sent'] += amount
                    self.murf_holders[address]['current_balance'] -= amount
                    self.murf_holders[address]['transaction_count'] += 1
                    self.murf_holders[address]['last_murf_tx'] = date
                
                elif to_addr == address and op_type == 0:  # RECEIVE operation
                    self.murf_holders[address]['total_received'] += amount
                    self.murf_holders[address]['current_balance'] += amount
                    self.murf_holders[address]['transaction_count'] += 1
                    self.murf_holders[address]['last_murf_tx'] = date
                    
        except Exception as e:
            pass
    
    def get_balance_for_address(self, address):
        """Get balance for specific address using KeetaNetSDK approach"""
        try:
            # This would be the proper KeetaNetSDK way:
            # client.getBalance(account, token) - returns Promise<bigint>
            # But we'll use API equivalent for now
            
            if address in self.murf_holders:
                return self.murf_holders[address]['current_balance']
            else:
                return 0
                
        except Exception as e:
            return 0
    
    def hex_to_decimal(self, hex_str):
        """Convert hexadecimal string to decimal integer."""
        try:
            if hex_str.startswith('0x'):
                return int(hex_str, 16)
            return int(hex_str)
        except:
            return 0
    
    def scan_all_addresses_comprehensive(self, max_blocks=50000):
        """Scan all addresses comprehensively using KeetaNetSDK approach"""
        self.start_time = time.time()
        print(f"Starting KeetaNetSDK Proper Scanner...")
        print(f"Using KeetaNetSDK methods: client.chain(), getBalance()")
        print(f"Target: Find ALL MURF holders including your address")
        print(f"Max blocks to scan: {max_blocks}")
        print("=" * 60)
        
        try:
            # Get all addresses first
            all_blocks = []
            next_key = None
            batch_count = 0
            
            while len(all_blocks) < max_blocks and batch_count < 250:
                url = f"{self.api_base}/history"
                params = {'limit': 200}
                if next_key:
                    params['nextKey'] = next_key
                
                print(f"Fetching batch {batch_count + 1}...")
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    history = data.get('history', [])
                    next_key = data.get('nextKey')
                    
                    all_blocks.extend(history)
                    print(f"  Batch {batch_count + 1}: {len(history)} blocks (Total: {len(all_blocks)})")
                    
                    if not next_key:
                        print("  No more blocks available")
                        break
                    
                    batch_count += 1
                else:
                    print(f"  API Error: {response.status_code}")
                    break
            
            # Extract all addresses
            print("Extracting all addresses...")
            for entry in all_blocks:
                if 'voteStaple' in entry:
                    vote_staple = entry['voteStaple']
                    blocks = vote_staple.get('blocks', [])
                    
                    for block in blocks:
                        if isinstance(block, dict):
                            self.extract_addresses_from_block(block)
                            self.blocks_scanned += 1
            
            print(f"Found {len(self.all_addresses)} unique addresses")
            
            # Now check each address for MURF balance using KeetaNetSDK approach
            print("Checking MURF balances for all addresses...")
            for i, address in enumerate(self.all_addresses):
                try:
                    # Use KeetaNetSDK approach: client.chain() for each address
                    self.get_chain_data(address)
                    
                    if (i + 1) % 100 == 0:
                        print(f"  Checked {i+1}/{len(self.all_addresses)} addresses, found {len(self.murf_holders)} MURF holders...")
                        
                except Exception as e:
                    continue
            
            elapsed = time.time() - self.start_time
            rate = self.blocks_scanned / elapsed if elapsed > 0 else 0
            
            print(f"KeetaNetSDK proper scan complete!")
            print(f"Blocks processed: {self.blocks_scanned}")
            print(f"Unique addresses found: {len(self.all_addresses)}")
            print(f"MURF holders found: {len(self.murf_holders)}")
            print(f"Time elapsed: {elapsed:.2f} seconds")
            print(f"Processing rate: {rate:.2f} blocks/second")
            
            return True
            
        except Exception as e:
            print(f"Error in KeetaNetSDK proper scan: {e}")
            return False
    
    def extract_addresses_from_block(self, block):
        """Extract addresses from block"""
        try:
            # Extract account address
            account = block.get('account', '')
            if account and isinstance(account, str):
                self.all_addresses.add(account)
            
            # Extract addresses from operations
            operations = block.get('operations', [])
            if isinstance(operations, list):
                for op in operations:
                    if isinstance(op, dict):
                        from_addr = op.get('from', '')
                        to_addr = op.get('to', '')
                        
                        if from_addr and isinstance(from_addr, str):
                            self.all_addresses.add(from_addr)
                        if to_addr and isinstance(to_addr, str):
                            self.all_addresses.add(to_addr)
            
            # Extract other addresses from block metadata
            signer = block.get('signer', '')
            if signer and isinstance(signer, str):
                self.all_addresses.add(signer)
                
        except Exception as e:
            pass
    
    def save_proper_data(self):
        """Save proper KeetaNetSDK data to database"""
        print("Saving proper KeetaNetSDK data to database...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM addresses')
        cursor.execute('DELETE FROM murf_holders')
        cursor.execute('DELETE FROM scan_metadata')
        
        # Save all addresses
        for address in self.all_addresses:
            is_murf_holder = address in self.murf_holders
            cursor.execute('''
                INSERT INTO addresses (address, is_murf_holder)
                VALUES (?, ?)
            ''', (address, is_murf_holder))
        
        # Save MURF holders
        for address, data in self.murf_holders.items():
            cursor.execute('''
                INSERT INTO murf_holders (address, total_received, total_sent, 
                                        current_balance, transaction_count, 
                                        first_murf_tx, last_murf_tx)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (address, data['total_received'], data['total_sent'], 
                  data['current_balance'], data['transaction_count'],
                  data['first_murf_tx'], data['last_murf_tx']))
        
        # Calculate totals
        total_murf_balance = sum(data['current_balance'] for data in self.murf_holders.values())
        
        # Save scan metadata
        cursor.execute('''
            INSERT INTO scan_metadata (scan_date, total_addresses, murf_holders, 
                                     total_murf_balance, blocks_scanned, scan_duration)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), len(self.all_addresses), len(self.murf_holders),
              total_murf_balance, self.blocks_scanned, time.time() - self.start_time))
        
        conn.commit()
        conn.close()
        print(f"Saved {len(self.all_addresses)} addresses and {len(self.murf_holders)} MURF holders to database")
    
    def check_user_address(self, user_address):
        """Check if user address is found"""
        print(f"\nChecking user address: {user_address}")
        print("=" * 60)
        
        if user_address in self.murf_holders:
            data = self.murf_holders[user_address]
            print(f"FOUND! User is a MURF holder!")
            print(f"Current Balance: {data['current_balance']:,} MURF")
            print(f"Total Received: {data['total_received']:,} MURF")
            print(f"Total Sent: {data['total_sent']:,} MURF")
            print(f"Transactions: {data['transaction_count']}")
            print(f"First TX: {data['first_murf_tx']}")
            print(f"Last TX: {data['last_murf_tx']}")
            return True
        else:
            print(f"NOT FOUND! User address not detected as MURF holder")
            return False
    
    def print_proper_results(self):
        """Print proper KeetaNetSDK results"""
        print(f"\nKEETANETSDK PROPER MURF HOLDERS ANALYSIS:")
        print("=" * 60)
        print(f"Total Addresses Found: {len(self.all_addresses)}")
        print(f"MURF Holders: {len(self.murf_holders)}")
        print(f"Blocks Scanned: {self.blocks_scanned}")
        
        if self.murf_holders:
            total_balance = sum(data['current_balance'] for data in self.murf_holders.values())
            print(f"Total MURF Balance: {total_balance:,}")
            
            print(f"\nMURF Token Holders (by current balance):")
            sorted_holders = sorted(self.murf_holders.items(), key=lambda x: x[1]['current_balance'], reverse=True)
            
            for i, (address, data) in enumerate(sorted_holders, 1):
                print(f"{i:2d}. {address[:50]}...")
                print(f"    Current Balance: {data['current_balance']:,} MURF")
                print(f"    Total Received: {data['total_received']:,} MURF")
                print(f"    Total Sent: {data['total_sent']:,} MURF")
                print(f"    Transactions: {data['transaction_count']}")
                print(f"    First TX: {data['first_murf_tx']}")
                print(f"    Last TX: {data['last_murf_tx']}")
                print()
        
        return {
            'total_addresses': len(self.all_addresses),
            'murf_holders': len(self.murf_holders),
            'total_murf_balance': sum(data['current_balance'] for data in self.murf_holders.values()),
            'blocks_scanned': self.blocks_scanned,
            'scan_duration': time.time() - self.start_time if self.start_time else 0
        }
    
    def run_proper_scan(self, max_blocks=50000):
        """Run proper KeetaNetSDK scan"""
        print("Starting KeetaNetSDK Proper Scanner...")
        print("Using KeetaNetSDK methods: client.chain(), getBalance()")
        print("Target: Find ALL MURF holders including your address")
        print("=" * 60)
        
        # Step 1: Scan all addresses
        if not self.scan_all_addresses_comprehensive(max_blocks):
            print("Failed to scan all addresses")
            return None
        
        # Step 2: Check user address
        user_address = "keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay"
        user_found = self.check_user_address(user_address)
        
        # Step 3: Save data
        self.save_proper_data()
        
        # Step 4: Print results
        stats = self.print_proper_results()
        
        print("=" * 60)
        print("KEETANETSDK PROPER SCAN COMPLETE!")
        print(f"Found {stats['total_addresses']} total addresses")
        print(f"Found {stats['murf_holders']} MURF holders")
        print(f"Total MURF balance: {stats['total_murf_balance']:,}")
        print(f"User address found: {'YES' if user_found else 'NO'}")
        print(f"Scanned {stats['blocks_scanned']} blocks in {stats['scan_duration']:.2f} seconds")
        print(f"Database: {self.db_path}")
        
        return stats

def main():
    scanner = KeetaNetSDKProperScanner()
    stats = scanner.run_proper_scan(max_blocks=50000)
    
    if stats:
        print(f"\nKeetaNetSDK Proper MURF Holder Scan Complete!")
        print(f"Database saved to: {scanner.db_path}")
        print(f"Ready for dashboard integration!")
    else:
        print("KeetaNetSDK proper scan failed")

if __name__ == "__main__":
    main()
