#!/usr/bin/env python3
"""
Smart Holders Manager
- Tracks OTC participants (buyers/sellers) 
- Updates holders list hourly
- Integrates with dashboard
"""

import sqlite3
import requests
import time
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from murf_holders_db import MURFHoldersDB
from otc_transactions_db import OTCTransactionsDB

class SmartHoldersManager:
    def __init__(self):
        self.murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        self.api_base = "https://rep2.main.network.api.keeta.com/api/node/ledger/account"
        self.holders_db = MURFHoldersDB()
        self.otc_db = OTCTransactionsDB()
        self.last_refresh = None
        self.refresh_interval = 3600  # 1 hour in seconds
        
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
            response = requests.get(url, timeout=3)  # Reduced timeout
            
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
    
    def get_balance_batch(self, addresses_batch):
        """Get balances for a batch of addresses using threading"""
        results = []
        
        def fetch_single_balance(address):
            balance = self.get_current_balance(address)
            return {
                'address': address,
                'current_balance': balance if balance is not None else 0
            }
        
        # Use ThreadPoolExecutor for concurrent API calls
        with ThreadPoolExecutor(max_workers=10) as executor:  # 10 concurrent requests
            future_to_address = {
                executor.submit(fetch_single_balance, addr): addr 
                for addr in addresses_batch
            }
            
            for future in as_completed(future_to_address):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    address = future_to_address[future]
                    results.append({
                        'address': address,
                        'current_balance': 0
                    })
        
        return results
    
    def extract_otc_participants(self):
        """Extract all OTC participants (buyers/sellers) from recent transactions"""
        print("Extracting OTC participants...")
        
        # Get recent OTC transactions
        conn = sqlite3.connect('otc_transactions.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT from_address, to_address, timestamp, tx_hash 
            FROM otc_transactions 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''')
        
        otc_transactions = cursor.fetchall()
        conn.close()
        
        # Extract unique participants
        participants = set()
        for tx in otc_transactions:
            from_address, to_address, timestamp, tx_hash = tx
            participants.add(from_address)
            participants.add(to_address)
        
        print(f"Found {len(participants)} OTC participants")
        return list(participants)
    
    def update_holders_from_otc(self):
        """Update holders list with OTC participants"""
        print("Updating holders from OTC participants...")
        
        # Get OTC participants
        otc_participants = self.extract_otc_participants()
        
        # Get existing holders
        conn = sqlite3.connect('murf_holders.db')
        cursor = conn.cursor()
        cursor.execute('SELECT address FROM murf_holders')
        existing_holders = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        # Find new participants not in existing holders
        new_participants = []
        for participant in otc_participants:
            if participant not in existing_holders:
                new_participants.append(participant)
        
        print(f"Found {len(new_participants)} new OTC participants")
        
        # Check balance for new participants
        active_new_holders = []
        for participant in new_participants:
            balance = self.get_current_balance(participant)
            if balance and balance > 0:
                active_new_holders.append({
                    'address': participant,
                    'current_balance': balance,
                    'total_received': balance,  # Assume all received from OTC
                    'total_sent': 0,
                    'tx_count': 1,
                    'first_tx_date': datetime.now().isoformat(),
                    'last_tx_date': datetime.now().isoformat()
                })
                print(f"New holder: {participant[:50]}... - {balance:,} MURF")
            
            time.sleep(0.1)  # Rate limiting
        
        # Add new holders to database
        if active_new_holders:
            self.add_new_holders(active_new_holders)
        
        return len(active_new_holders)
    
    def add_new_holders(self, new_holders):
        """Add new holders to the database"""
        conn = sqlite3.connect('murf_holders.db')
        cursor = conn.cursor()
        
        for holder in new_holders:
            cursor.execute('''
                INSERT OR REPLACE INTO murf_holders 
                (address, total_received, total_sent, current_balance, tx_count, first_tx_date, last_tx_date, rank, is_airdrop_recipient)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                holder['address'],
                holder['total_received'],
                holder['total_sent'],
                holder['current_balance'],
                holder['tx_count'],
                holder['first_tx_date'],
                holder['last_tx_date'],
                9999,  # Temporary rank
                False  # Not from airdrop
            ))
        
        conn.commit()
        conn.close()
        
        print(f"Added {len(new_holders)} new holders to database")
    
    def refresh_holders_data(self):
        """Full refresh of holders data (hourly) - OPTIMIZED with threading"""
        print("Starting hourly holders refresh...")
        
        # Update from OTC participants first
        new_holders = self.update_holders_from_otc()
        
        # Then do full scan of existing holders
        print("Scanning existing holders for balance updates (OPTIMIZED)...")
        
        conn = sqlite3.connect('murf_holders.db')
        cursor = conn.cursor()
        cursor.execute('SELECT address FROM murf_holders ORDER BY current_balance DESC')
        addresses = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"Processing {len(addresses)} addresses with 10 concurrent threads...")
        
        # Process in batches of 50 addresses
        batch_size = 50
        updated_holders = []
        
        for i in range(0, len(addresses), batch_size):
            batch = addresses[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(addresses) + batch_size - 1) // batch_size
            
            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} addresses)...")
            
            # Get balances for this batch using threading
            batch_results = self.get_balance_batch(batch)
            
            for result in batch_results:
                updated_holders.append(result)
                
                if result['current_balance'] > 0:
                    print(f"  {result['address'][:50]}... - {result['current_balance']:,} MURF")
                # Don't print for 0 balance to reduce spam
            
            # Small delay between batches to be nice to API
            time.sleep(0.1)
        
        # Update database with new balances
        print("Updating database with new balances...")
        self.update_holders_balances(updated_holders)
        
        # Re-rank holders
        print("Re-ranking holders...")
        self.rerank_holders()
        
        self.last_refresh = datetime.now()
        active_count = len([h for h in updated_holders if h['current_balance'] > 0])
        print(f"Holders refresh completed at {self.last_refresh}")
        print(f"Active holders: {active_count}")
        
        return active_count
    
    def update_holders_balances(self, updated_holders):
        """Update holders balances in database"""
        conn = sqlite3.connect('murf_holders.db')
        cursor = conn.cursor()
        
        for holder in updated_holders:
            cursor.execute('''
                UPDATE murf_holders 
                SET current_balance = ?
                WHERE address = ?
            ''', (
                holder['current_balance'],
                holder['address']
            ))
        
        conn.commit()
        conn.close()
    
    def rerank_holders(self):
        """Re-rank holders by current balance"""
        conn = sqlite3.connect('murf_holders.db')
        cursor = conn.cursor()
        
        # Get all holders sorted by balance
        cursor.execute('''
            SELECT address, current_balance 
            FROM murf_holders 
            WHERE current_balance > 0
            ORDER BY current_balance DESC
        ''')
        
        holders = cursor.fetchall()
        
        # Update ranks
        for rank, (address, balance) in enumerate(holders, 1):
            cursor.execute('''
                UPDATE murf_holders 
                SET rank = ?
                WHERE address = ?
            ''', (rank, address))
        
        conn.commit()
        conn.close()
        
        print(f"Re-ranked {len(holders)} active holders")
    
    def should_refresh(self):
        """Check if holders data should be refreshed"""
        if self.last_refresh is None:
            return True
        
        time_since_refresh = datetime.now() - self.last_refresh
        return time_since_refresh.total_seconds() >= self.refresh_interval
    
    def get_holders_data(self):
        """Get current holders data (with auto-refresh if needed)"""
        if self.should_refresh():
            print("Holders data needs refresh...")
            # Run refresh in background thread
            refresh_thread = threading.Thread(target=self.refresh_holders_data)
            refresh_thread.daemon = True
            refresh_thread.start()
        
        # Return current data from database
        return self.holders_db.get_top_holders(20), self.holders_db.get_holder_statistics()
    
    def start_background_refresh(self):
        """Start background refresh thread"""
        def background_refresh():
            while True:
                time.sleep(self.refresh_interval)
                self.refresh_holders_data()
        
        refresh_thread = threading.Thread(target=background_refresh)
        refresh_thread.daemon = True
        refresh_thread.start()
        print("Background holders refresh started (hourly)")

def main():
    """Test the smart holders manager"""
    manager = SmartHoldersManager()
    
    print("Smart Holders Manager Test")
    print("=" * 50)
    
    # Test OTC participants extraction
    otc_participants = manager.extract_otc_participants()
    print(f"OTC Participants: {len(otc_participants)}")
    
    # Test holders update
    new_holders_count = manager.update_holders_from_otc()
    print(f"New holders added: {new_holders_count}")
    
    # Test full refresh
    active_holders = manager.refresh_holders_data()
    print(f"Active holders: {active_holders}")

if __name__ == "__main__":
    main()
