#!/usr/bin/env python3
"""
Check specific address for MURF token balance
"""

import sqlite3
import requests
from datetime import datetime

def check_address_balance(address):
    """Check if specific address has MURF token balance"""
    print(f"Checking address: {address}")
    print("=" * 60)
    
    # Check in keeta_sdk_balances.db
    try:
        conn = sqlite3.connect("keeta_sdk_balances.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT address, balance, last_updated 
            FROM token_balances 
            WHERE address = ? AND token = ?
        ''', (address, "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print(f"FOUND in database!")
            print(f"Address: {result[0]}")
            print(f"Balance: {result[1]:,} MURF")
            print(f"Last Updated: {result[2]}")
            return True
        else:
            print("NOT FOUND in database")
            return False
            
    except Exception as e:
        print(f"Error checking database: {e}")
        return False

def check_address_in_all_addresses(address):
    """Check if address exists in all addresses list"""
    try:
        conn = sqlite3.connect("keeta_sdk_balances.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT address, has_murf_balance 
            FROM addresses 
            WHERE address = ?
        ''', (address,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print(f"Address exists in all addresses list")
            print(f"Has MURF balance: {bool(result[1])}")
            return True
        else:
            print("Address NOT FOUND in all addresses list")
            return False
            
    except Exception as e:
        print(f"Error checking addresses: {e}")
        return False

def check_address_via_api(address):
    """Check address balance via API"""
    print(f"Checking address via API...")
    
    try:
        # Get recent transactions for this address
        url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history"
        params = {'limit': 200}
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])
            
            balance = 0
            transactions = []
            
            for entry in history:
                if 'voteStaple' in entry:
                    vote_staple = entry['voteStaple']
                    blocks = vote_staple.get('blocks', [])
                    
                    for block in blocks:
                        if isinstance(block, dict):
                            operations = block.get('operations', [])
                            if isinstance(operations, list):
                                for op in operations:
                                    if isinstance(op, dict):
                                        if op.get('token') == "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm":
                                            from_addr = op.get('from', '')
                                            to_addr = op.get('to', '')
                                            
                                            if from_addr == address or to_addr == address:
                                                amount = hex_to_decimal(op.get('amount', '0'))
                                                tx_type = "SEND" if from_addr == address else "RECEIVE"
                                                
                                                transactions.append({
                                                    'type': tx_type,
                                                    'amount': amount,
                                                    'date': block.get('date', ''),
                                                    'block_hash': block.get('$hash', '')
                                                })
                                                
                                                if from_addr == address:
                                                    balance -= amount
                                                elif to_addr == address:
                                                    balance += amount
            
            print(f"API Analysis Results:")
            print(f"Total MURF transactions: {len(transactions)}")
            print(f"Calculated balance: {max(0, balance):,} MURF")
            
            if transactions:
                print(f"\nRecent MURF transactions:")
                for i, tx in enumerate(transactions[:5], 1):
                    print(f"  {i}. {tx['type']}: {tx['amount']:,} MURF ({tx['date']})")
            
            return max(0, balance)
        else:
            print(f"API Error: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"Error checking via API: {e}")
        return 0

def hex_to_decimal(hex_str):
    """Convert hexadecimal string to decimal integer."""
    try:
        if hex_str.startswith('0x'):
            return int(hex_str, 16)
        return int(hex_str)
    except:
        return 0

def main():
    address = "keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay"
    
    print("MURF Token Holder Check")
    print("=" * 60)
    
    # Check 1: Database lookup
    print("1. Checking database...")
    found_in_db = check_address_balance(address)
    print()
    
    # Check 2: All addresses list
    print("2. Checking all addresses list...")
    found_in_all = check_address_in_all_addresses(address)
    print()
    
    # Check 3: API analysis
    print("3. Checking via API analysis...")
    api_balance = check_address_via_api(address)
    print()
    
    # Summary
    print("SUMMARY:")
    print("=" * 60)
    print(f"Address: {address}")
    print(f"Found in database: {'YES' if found_in_db else 'NO'}")
    print(f"Found in all addresses: {'YES' if found_in_all else 'NO'}")
    print(f"API calculated balance: {api_balance:,} MURF")
    
    if api_balance > 0:
        print(f"Your address IS a MURF holder with {api_balance:,} MURF!")
    else:
        print(f"Your address is NOT detected as a MURF holder")

if __name__ == "__main__":
    main()
