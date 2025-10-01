#!/usr/bin/env python3
"""
Check specific block for MURF transactions
"""

import requests
import json
from datetime import datetime

def check_specific_block(block_hash):
    """Check specific block for MURF transactions"""
    print(f"Checking block: {block_hash}")
    print("=" * 60)
    
    try:
        # Get block data from API
        url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history"
        params = {'limit': 200}
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])
            
            found_block = None
            for entry in history:
                if 'voteStaple' in entry:
                    vote_staple = entry['voteStaple']
                    blocks = vote_staple.get('blocks', [])
                    
                    for block in blocks:
                        if isinstance(block, dict):
                            if block.get('$hash') == block_hash:
                                found_block = block
                                break
                    if found_block:
                        break
            
            if found_block:
                print(f"Block found!")
                print(f"Date: {found_block.get('date', 'N/A')}")
                print(f"Account: {found_block.get('account', 'N/A')}")
                print(f"Hash: {found_block.get('$hash', 'N/A')}")
                
                # Check operations
                operations = found_block.get('operations', [])
                print(f"\nOperations ({len(operations)}):")
                
                murf_operations = []
                for i, op in enumerate(operations):
                    print(f"  {i+1}. Type: {op.get('type', 'N/A')}")
                    print(f"     Token: {op.get('token', 'N/A')}")
                    print(f"     Amount: {op.get('amount', 'N/A')}")
                    print(f"     From: {op.get('from', 'N/A')}")
                    print(f"     To: {op.get('to', 'N/A')}")
                    print()
                    
                    # Check for MURF operations
                    if op.get('token') == "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm":
                        murf_operations.append(op)
                
                if murf_operations:
                    print(f"MURF Operations found: {len(murf_operations)}")
                    for i, op in enumerate(murf_operations):
                        print(f"  MURF Op {i+1}:")
                        print(f"    Type: {op.get('type', 'N/A')}")
                        print(f"    Amount: {op.get('amount', 'N/A')}")
                        print(f"    From: {op.get('from', 'N/A')}")
                        print(f"    To: {op.get('to', 'N/A')}")
                        
                        # Check if user's address is involved
                        from_addr = op.get('from', '')
                        to_addr = op.get('to', '')
                        user_addr = "keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay"
                        
                        if from_addr == user_addr or to_addr == user_addr:
                            print(f"    *** USER ADDRESS INVOLVED! ***")
                            print(f"    User address: {user_addr}")
                            print(f"    Operation: {'SENT' if from_addr == user_addr else 'RECEIVED'}")
                            
                            # Convert amount
                            amount = hex_to_decimal(op.get('amount', '0'))
                            print(f"    Amount: {amount:,} MURF")
                else:
                    print("No MURF operations found in this block")
            else:
                print("Block not found in recent history")
                print("This block might be older than the API limit")
        else:
            print(f"API Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error checking block: {e}")

def hex_to_decimal(hex_str):
    """Convert hexadecimal string to decimal integer."""
    try:
        if hex_str.startswith('0x'):
            return int(hex_str, 16)
        return int(hex_str)
    except:
        return 0

def main():
    block_hash = "E84E91DC24C9782B9FF7B15003A4EDDED2BD6E97392617CF5F1A49F82E4005EA"
    check_specific_block(block_hash)

if __name__ == "__main__":
    main()
