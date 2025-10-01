#!/usr/bin/env python3
"""
Airdrop Trace Scanner - Find all MURF holders by tracing from airdrop wallet
"""

import requests
import sqlite3
import json
from datetime import datetime
import time

def hex_to_decimal(hex_str):
    """Convert hexadecimal string to decimal integer."""
    if hex_str.startswith('0x'):
        return int(hex_str, 16)
    return int(hex_str)

class AirdropTraceScanner:
    def __init__(self):
        self.airdrop_wallet = "keeta_aablrt5p4in4mehyxxunow3kp4c7rs2v4mh6v4z6qtfnt7sw5cxtw4r3b5oxtwi"
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.api_url = "https://rep2.main.network.api.keeta.com/api/node/ledger/account"
        self.db_path = "airdrop_trace.db"
        self.holders = {}  # {address: {'received': amount, 'sent': amount, 'tx_count': count, 'first_tx': date, 'last_tx': date}}
        self.airdrop_txs = []  # All airdrop transactions
        self.start_time = None
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for airdrop trace data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS airdrop_holders (
                address TEXT PRIMARY KEY,
                total_received INTEGER,
                total_sent INTEGER,
                current_balance INTEGER,
                tx_count INTEGER,
                first_tx_date TEXT,
                last_tx_date TEXT,
                is_airdrop_recipient BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS airdrop_transactions (
                tx_hash TEXT PRIMARY KEY,
                from_address TEXT,
                to_address TEXT,
                amount INTEGER,
                date TEXT,
                block_hash TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Airdrop trace database initialized: {self.db_path}")
    
    def get_account_history(self, address, limit=1000):
        """Get account history from Keeta API"""
        url = f"{self.api_url}/{address}/history"
        params = {'limit': limit}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching account history for {address}: {e}")
            return None
    
    def analyze_airdrop_wallet(self):
        """Analyze the airdrop wallet to find all MURF recipients"""
        print("=" * 80)
        print("ANALYZING AIRDROP WALLET")
        print("=" * 80)
        print(f"Airdrop Wallet: {self.airdrop_wallet}")
        print(f"Target Token: {self.murf_token}")
        print()
        
        self.start_time = time.time()
        
        # Get airdrop wallet history
        print("Fetching airdrop wallet history...")
        data = self.get_account_history(self.airdrop_wallet, limit=1000)
        
        if not data or not data.get('history'):
            print("ERROR: No history data found for airdrop wallet")
            return False
        
        print(f"Found {len(data['history'])} history entries")
        
        # Analyze each history entry
        airdrop_count = 0
        for entry in data['history']:
            if entry.get('voteStaple') and entry['voteStaple'].get('blocks'):
                for block in entry['voteStaple']['blocks']:
                    operations = block.get('operations', [])
                    block_date = block.get('date')
                    block_hash = block.get('$hash')
                    
                    for op in operations:
                        # Look for MURF token operations (Type 0 = RECEIVE, Type 7 = SEND)
                        if op.get('token') == self.murf_token:
                            amount = hex_to_decimal(op.get('amount', '0x0'))
                            
                            if op.get('type') == 7:  # SEND operation (airdrop wallet sending to recipients)
                                from_address = op.get('from')
                                if from_address and from_address != self.airdrop_wallet:
                                    # This is someone sending MURF to airdrop wallet
                                    if from_address not in self.holders:
                                        self.holders[from_address] = {
                                            'received': 0, 'sent': 0, 'tx_count': 0,
                                            'first_tx': block_date, 'last_tx': block_date
                                        }
                                    self.holders[from_address]['sent'] += amount
                                    self.holders[from_address]['tx_count'] += 1
                                    self.holders[from_address]['last_tx'] = block_date
                                    
                                    # Record airdrop transaction
                                    self.airdrop_txs.append({
                                        'tx_hash': f"{block_hash}_{op.get('$id', 'unknown')}",
                                        'from_address': from_address,
                                        'to_address': self.airdrop_wallet,
                                        'amount': amount,
                                        'date': block_date,
                                        'block_hash': block_hash
                                    })
                                    airdrop_count += 1
                            
                            elif op.get('type') == 7:  # SEND operation (airdrop wallet sending)
                                to_address = op.get('to')
                                if to_address and to_address != self.airdrop_wallet:
                                    # This is airdrop wallet sending MURF to recipients
                                    if to_address not in self.holders:
                                        self.holders[to_address] = {
                                            'received': 0, 'sent': 0, 'tx_count': 0,
                                            'first_tx': block_date, 'last_tx': block_date
                                        }
                                    self.holders[to_address]['received'] += amount
                                    self.holders[to_address]['tx_count'] += 1
                                    self.holders[to_address]['last_tx'] = block_date
                                    
                                    # Record airdrop transaction
                                    self.airdrop_txs.append({
                                        'tx_hash': f"{block_hash}_{op.get('$id', 'unknown')}",
                                        'from_address': self.airdrop_wallet,
                                        'to_address': to_address,
                                        'amount': amount,
                                        'date': block_date,
                                        'block_hash': block_hash
                                    })
                                    airdrop_count += 1
        
        print(f"Found {airdrop_count} MURF transactions from airdrop wallet")
        print(f"Found {len(self.holders)} unique addresses involved")
        
        return True
    
    def check_user_address(self, user_address):
        """Check if user address is in the holders list"""
        print("=" * 80)
        print("CHECKING USER ADDRESS")
        print("=" * 80)
        print(f"User Address: {user_address}")
        
        if user_address in self.holders:
            holder_data = self.holders[user_address]
            print("USER ADDRESS FOUND!")
            print(f"Total Received: {holder_data['received']:,} MURF")
            print(f"Total Sent: {holder_data['sent']:,} MURF")
            print(f"Current Balance: {holder_data['received'] - holder_data['sent']:,} MURF")
            print(f"Transaction Count: {holder_data['tx_count']}")
            print(f"First TX: {holder_data['first_tx']}")
            print(f"Last TX: {holder_data['last_tx']}")
            return True
        else:
            print("USER ADDRESS NOT FOUND")
            return False
    
    def save_to_database(self):
        """Save all data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM airdrop_holders')
        cursor.execute('DELETE FROM airdrop_transactions')
        
        # Save holders
        for address, data in self.holders.items():
            current_balance = data['received'] - data['sent']
            is_airdrop_recipient = data['received'] > 0
            
            cursor.execute('''
                INSERT OR REPLACE INTO airdrop_holders 
                (address, total_received, total_sent, current_balance, tx_count, 
                 first_tx_date, last_tx_date, is_airdrop_recipient)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (address, data['received'], data['sent'], current_balance, 
                  data['tx_count'], data['first_tx'], data['last_tx'], is_airdrop_recipient))
        
        # Save transactions
        for tx in self.airdrop_txs:
            cursor.execute('''
                INSERT OR REPLACE INTO airdrop_transactions 
                (tx_hash, from_address, to_address, amount, date, block_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tx['tx_hash'], tx['from_address'], tx['to_address'], 
                  tx['amount'], tx['date'], tx['block_hash']))
        
        conn.commit()
        conn.close()
        print(f"Saved {len(self.holders)} holders and {len(self.airdrop_txs)} transactions to database")
    
    def print_summary(self):
        """Print summary of findings"""
        print("=" * 80)
        print("AIRDROP TRACE SCAN SUMMARY")
        print("=" * 80)
        
        # Calculate statistics
        total_received = sum(data['received'] for data in self.holders.values())
        total_sent = sum(data['sent'] for data in self.holders.values())
        airdrop_recipients = sum(1 for data in self.holders.values() if data['received'] > 0)
        
        print(f"Total Addresses Found: {len(self.holders)}")
        print(f"Airdrop Recipients: {airdrop_recipients}")
        print(f"Total MURF Received: {total_received:,}")
        print(f"Total MURF Sent: {total_sent:,}")
        print(f"Net MURF in Circulation: {total_received - total_sent:,}")
        print()
        
        # Top holders
        sorted_holders = sorted(self.holders.items(), 
                              key=lambda x: x[1]['received'] - x[1]['sent'], 
                              reverse=True)
        
        print("TOP MURF HOLDERS (by current balance):")
        print("-" * 80)
        for i, (address, data) in enumerate(sorted_holders[:20], 1):
            current_balance = data['received'] - data['sent']
            if current_balance > 0:
                print(f"{i:2d}. {address[:50]}...")
                print(f"    Current Balance: {current_balance:,} MURF")
                print(f"    Received: {data['received']:,} MURF")
                print(f"    Sent: {data['sent']:,} MURF")
                print(f"    TX Count: {data['tx_count']}")
                print(f"    First TX: {data['first_tx']}")
                print(f"    Last TX: {data['last_tx']}")
                print()
        
        elapsed_time = time.time() - self.start_time
        print(f"Scan completed in {elapsed_time:.2f} seconds")
        print(f"Database saved to: {self.db_path}")

def main():
    scanner = AirdropTraceScanner()
    
    print("Starting Airdrop Trace Scanner...")
    print("Target: Find all MURF holders by tracing from airdrop wallet")
    print("=" * 80)
    
    # Analyze airdrop wallet
    if scanner.analyze_airdrop_wallet():
        # Check user address
        user_address = "keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay"
        scanner.check_user_address(user_address)
        
        # Save to database
        scanner.save_to_database()
        
        # Print summary
        scanner.print_summary()
    else:
        print("ERROR: Failed to analyze airdrop wallet")

if __name__ == "__main__":
    main()
