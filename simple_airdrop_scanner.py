#!/usr/bin/env python3
"""
Simple Airdrop Scanner - Find MURF recipients from airdrop wallet
"""

import requests
import json
from datetime import datetime

def hex_to_decimal(hex_str):
    """Convert hexadecimal string to decimal integer."""
    if hex_str.startswith('0x'):
        return int(hex_str, 16)
    return int(hex_str)

def main():
    airdrop_wallet = "keeta_aablrt5p4in4mehyxxunow3kp4c7rs2v4mh6v4z6qtfnt7sw5cxtw4r3b5oxtwi"
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    user_address = "keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay"
    
    print("=" * 80)
    print("SIMPLE AIRDROP SCANNER")
    print("=" * 80)
    print(f"Airdrop Wallet: {airdrop_wallet}")
    print(f"Target Token: {murf_token}")
    print(f"User Address: {user_address}")
    print()
    
    # Get airdrop wallet history
    url = f"https://rep2.main.network.api.keeta.com/api/node/ledger/account/{airdrop_wallet}/history"
    params = {'limit': 1000}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
    
    if not data or not data.get('history'):
        print("No history data found")
        return
    
    print(f"Found {len(data['history'])} history entries")
    
    # Analyze transactions
    holders = {}
    airdrop_count = 0
    user_found = False
    
    for entry in data['history']:
        if entry.get('voteStaple') and entry['voteStaple'].get('blocks'):
            for block in entry['voteStaple']['blocks']:
                operations = block.get('operations', [])
                block_date = block.get('date')
                block_hash = block.get('$hash')
                
                for op in operations:
                    # Look for MURF token Type 7 (SEND) operations
                    if op.get('token') == murf_token and op.get('type') == 7:
                        to_address = op.get('to')
                        amount = hex_to_decimal(op.get('amount', '0x0'))
                        
                        if to_address and to_address != airdrop_wallet:
                            # This is airdrop wallet sending MURF to recipients
                            if to_address not in holders:
                                holders[to_address] = {
                                    'received': 0, 'sent': 0, 'tx_count': 0,
                                    'first_tx': block_date, 'last_tx': block_date
                                }
                            
                            holders[to_address]['received'] += amount
                            holders[to_address]['tx_count'] += 1
                            holders[to_address]['last_tx'] = block_date
                            
                            airdrop_count += 1
                            
                            # Check if this is the user
                            if to_address == user_address:
                                user_found = True
                                print(f"FOUND USER! Received {amount:,} MURF in block {block_hash[:16]}...")
    
    print(f"\nFound {airdrop_count} MURF airdrop transactions")
    print(f"Found {len(holders)} unique recipients")
    
    # Check user
    print("\n" + "=" * 80)
    print("USER ADDRESS CHECK")
    print("=" * 80)
    if user_found:
        user_data = holders[user_address]
        print("USER ADDRESS FOUND!")
        print(f"Total Received: {user_data['received']:,} MURF")
        print(f"Total Sent: {user_data['sent']:,} MURF")
        print(f"Current Balance: {user_data['received'] - user_data['sent']:,} MURF")
        print(f"Transaction Count: {user_data['tx_count']}")
        print(f"First TX: {user_data['first_tx']}")
        print(f"Last TX: {user_data['last_tx']}")
    else:
        print("USER ADDRESS NOT FOUND")
    
    # Show top holders
    print("\n" + "=" * 80)
    print("TOP MURF HOLDERS")
    print("=" * 80)
    sorted_holders = sorted(holders.items(), 
                          key=lambda x: x[1]['received'], 
                          reverse=True)
    
    for i, (address, data) in enumerate(sorted_holders[:10], 1):
        current_balance = data['received'] - data['sent']
        print(f"{i:2d}. {address[:50]}...")
        print(f"    Received: {data['received']:,} MURF")
        print(f"    Current Balance: {current_balance:,} MURF")
        print(f"    TX Count: {data['tx_count']}")
        print(f"    First TX: {data['first_tx']}")
        print()
    
    # Summary
    total_received = sum(data['received'] for data in holders.values())
    total_sent = sum(data['sent'] for data in holders.values())
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Recipients: {len(holders)}")
    print(f"Total MURF Airdropped: {total_received:,}")
    print(f"Total MURF Sent Back: {total_sent:,}")
    print(f"Net MURF in Circulation: {total_received - total_sent:,}")
    print(f"User Found: {'YES' if user_found else 'NO'}")

if __name__ == "__main__":
    main()
