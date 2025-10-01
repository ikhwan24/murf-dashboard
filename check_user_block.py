#!/usr/bin/env python3
"""
Check specific block hash for user's MURF transactions
"""

import requests
import json
from datetime import datetime

def hex_to_decimal(hex_str):
    """Convert hexadecimal string to decimal integer."""
    if hex_str.startswith('0x'):
        return int(hex_str, 16)
    return int(hex_str)

def get_block_by_hash(block_hash):
    """Get block by hash from Keeta API"""
    url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history"
    params = {
        'limit': 1,
        'blockHash': block_hash
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data and data.get('history'):
            for entry in data['history']:
                if entry.get('voteStaple') and entry['voteStaple'].get('blocks'):
                    for block in entry['voteStaple']['blocks']:
                        if block.get('$hash') == block_hash:
                            return block
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching block data: {e}")
        return None

def check_user_address_in_block(block, user_address):
    """Check if user address appears in block operations"""
    operations = block.get('operations', [])
    user_found = False
    
    print(f"Block Date: {block.get('date')}")
    print(f"Block Account: {block.get('account')}")
    print(f"Block Hash: {block.get('$hash')}")
    print(f"Operations Count: {len(operations)}")
    print()
    
    for i, op in enumerate(operations):
        print(f"Operation {i+1}:")
        print(f"  Type: {op.get('type')}")
        print(f"  Token: {op.get('token')}")
        print(f"  Amount: {op.get('amount')}")
        print(f"  From: {op.get('from')}")
        print(f"  To: {op.get('to')}")
        
        # Check if user address appears
        if op.get('from') == user_address or op.get('to') == user_address:
            user_found = True
            print(f"  *** USER ADDRESS FOUND! ***")
            if op.get('token') == "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm":
                amount = hex_to_decimal(op.get('amount', '0x0'))
                print(f"  *** MURF TOKEN DETECTED! Amount: {amount:,} MURF ***")
        print()
    
    return user_found

def main():
    user_address = "keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay"
    block_hash = "E84E91DC24C9782B9FF7B15003A4EDDED2BD6E97392617CF5F1A49F82E4005EA"
    
    print("=" * 80)
    print("CHECKING USER BLOCK FOR MURF TRANSACTIONS")
    print("=" * 80)
    print(f"User Address: {user_address}")
    print(f"Block Hash: {block_hash}")
    print()
    
    # Try to get block by hash
    print("Fetching block by hash...")
    block = get_block_by_hash(block_hash)
    
    if block:
        print("Block found!")
        print("=" * 80)
        user_found = check_user_address_in_block(block, user_address)
        
        if user_found:
            print("SUCCESS: User address found in this block!")
        else:
            print("WARNING: User address NOT found in this block")
    else:
        print("ERROR: Block not found in recent history")
        print("This block might be older than the API limit (200 blocks)")
        print("=" * 80)
        print("ALTERNATIVE: Let's check if we can find your address in recent blocks...")
        
        # Try to find user in recent blocks
        url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history"
        params = {'limit': 200}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('history'):
                print(f"Checking {len(data['history'])} recent history entries...")
                found_in_recent = False
                
                for entry in data['history']:
                    if entry.get('voteStaple') and entry['voteStaple'].get('blocks'):
                        for block in entry['voteStaple']['blocks']:
                            operations = block.get('operations', [])
                            for op in operations:
                                if (op.get('from') == user_address or op.get('to') == user_address) and \
                                   op.get('token') == "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm":
                                    found_in_recent = True
                                    amount = hex_to_decimal(op.get('amount', '0x0'))
                                    print(f"FOUND: {amount:,} MURF in block {block.get('$hash')[:16]}...")
                
                if not found_in_recent:
                    print("User address not found in recent 200 blocks")
                    print("This suggests the block is older than API limit")
        
        except Exception as e:
            print(f"Error checking recent blocks: {e}")

if __name__ == "__main__":
    main()
