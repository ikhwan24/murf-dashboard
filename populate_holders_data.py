#!/usr/bin/env python3
"""
Populate MURF holders data from airdrop scanner results
"""

import requests
import json
from datetime import datetime
from murf_holders_db import MURFHoldersDB

def hex_to_decimal(hex_str):
    """Convert hexadecimal string to decimal integer."""
    if hex_str.startswith('0x'):
        return int(hex_str, 16)
    return int(hex_str)

def fetch_holders_data():
    """Fetch MURF holders data from airdrop wallet"""
    airdrop_wallet = "keeta_aablrt5p4in4mehyxxunow3kp4c7rs2v4mh6v4z6qtfnt7sw5cxtw4r3b5oxtwi"
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    
    print("Fetching MURF holders data from airdrop wallet...")
    
    # Get airdrop wallet history
    url = f"https://rep2.main.network.api.keeta.com/api/node/ledger/account/{airdrop_wallet}/history"
    params = {'limit': 1000}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None
    
    if not data or not data.get('history'):
        print("No history data found")
        return None, None
    
    print(f"Found {len(data['history'])} history entries")
    
    # Analyze transactions
    holders = {}
    airdrop_count = 0
    
    for entry in data['history']:
        if entry.get('voteStaple') and entry['voteStaple'].get('blocks'):
            for block in entry['voteStaple']['blocks']:
                operations = block.get('operations', [])
                block_date = block.get('date')
                
                for op in operations:
                    # Look for MURF token Type 0 (RECEIVE) operations
                    if op.get('token') == murf_token and op.get('type') == 0:
                        to_address = op.get('to')
                        amount = hex_to_decimal(op.get('amount', '0x0'))
                        
                        if to_address and to_address != airdrop_wallet:
                            # This is someone receiving MURF from airdrop wallet
                            if to_address not in holders:
                                holders[to_address] = {
                                    'received': 0, 'sent': 0, 'tx_count': 0,
                                    'first_tx': block_date, 'last_tx': block_date
                                }
                            
                            holders[to_address]['received'] += amount
                            holders[to_address]['tx_count'] += 1
                            holders[to_address]['last_tx'] = block_date
                            airdrop_count += 1
    
    # Calculate statistics
    total_received = sum(data['received'] for data in holders.values())
    total_sent = sum(data['sent'] for data in holders.values())
    
    statistics = {
        'total_holders': len(holders),
        'total_circulation': total_received - total_sent,
        'total_airdropped': total_received,
        'last_updated': datetime.now().isoformat()
    }
    
    print(f"Found {airdrop_count} MURF airdrop transactions")
    print(f"Found {len(holders)} unique recipients")
    print(f"Total MURF airdropped: {total_received:,}")
    
    return holders, statistics

def main():
    print("=" * 80)
    print("POPULATING MURF HOLDERS DATA")
    print("=" * 80)
    
    # Initialize database
    db = MURFHoldersDB()
    
    # Fetch holders data
    holders_data, statistics = fetch_holders_data()
    
    if holders_data and statistics:
        # Save to database
        db.save_holders_data(holders_data, statistics)
        
        # Show top holders
        print("\n" + "=" * 80)
        print("TOP MURF HOLDERS")
        print("=" * 80)
        
        top_holders = db.get_top_holders(10)
        for i, holder in enumerate(top_holders, 1):
            print(f"{i:2d}. {holder['address'][:50]}...")
            print(f"    Balance: {holder['current_balance']:,} MURF")
            print(f"    Received: {holder['total_received']:,} MURF")
            print(f"    TX Count: {holder['tx_count']}")
            print(f"    Rank: #{holder['rank']}")
            print()
        
        # Show statistics
        stats = db.get_holder_statistics()
        if stats:
            print("=" * 80)
            print("HOLDER STATISTICS")
            print("=" * 80)
            print(f"Total Holders: {stats['total_holders']:,}")
            print(f"Total Circulation: {stats['total_circulation']:,} MURF")
            print(f"Total Airdropped: {stats['total_airdropped']:,} MURF")
            print(f"Last Updated: {stats['last_updated']}")
        
        print("\nMURF holders data successfully populated!")
        print("Ready for dashboard integration!")
    else:
        print("Failed to fetch holders data")

if __name__ == "__main__":
    main()
