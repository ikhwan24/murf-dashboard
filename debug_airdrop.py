#!/usr/bin/env python3
"""
Debug Airdrop Scanner - Check what's in the airdrop wallet
"""

import requests
import json

def hex_to_decimal(hex_str):
    """Convert hexadecimal string to decimal integer."""
    if hex_str.startswith('0x'):
        return int(hex_str, 16)
    return int(hex_str)

def main():
    airdrop_wallet = "keeta_aablrt5p4in4mehyxxunow3kp4c7rs2v4mh6v4z6qtfnt7sw5cxtw4r3b5oxtwi"
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    
    print("=" * 80)
    print("DEBUG AIRDROP WALLET")
    print("=" * 80)
    print(f"Airdrop Wallet: {airdrop_wallet}")
    print(f"Target Token: {murf_token}")
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
    
    # Analyze first few entries in detail
    for i, entry in enumerate(data['history'][:3]):  # Only first 3 entries
        print(f"\n--- HISTORY ENTRY {i+1} ---")
        print(f"Entry keys: {list(entry.keys())}")
        
        if entry.get('voteStaple') and entry['voteStaple'].get('blocks'):
            print(f"Found {len(entry['voteStaple']['blocks'])} blocks")
            
            for j, block in enumerate(entry['voteStaple']['blocks'][:2]):  # Only first 2 blocks
                print(f"\n  --- BLOCK {j+1} ---")
                print(f"  Block keys: {list(block.keys())}")
                print(f"  Block date: {block.get('date')}")
                print(f"  Block hash: {block.get('$hash')}")
                print(f"  Block account: {block.get('account')}")
                
                operations = block.get('operations', [])
                print(f"  Operations count: {len(operations)}")
                
                # Check first few operations
                for k, op in enumerate(operations[:5]):  # Only first 5 operations
                    print(f"\n    Operation {k+1}:")
                    print(f"      Type: {op.get('type')}")
                    print(f"      Token: {op.get('token')}")
                    print(f"      Amount: {op.get('amount')}")
                    print(f"      From: {op.get('from')}")
                    print(f"      To: {op.get('to')}")
                    
                    # Check if this is MURF token
                    if op.get('token') == murf_token:
                        amount = hex_to_decimal(op.get('amount', '0x0'))
                        print(f"      *** MURF TOKEN DETECTED! Amount: {amount:,} MURF ***")
                        print(f"      *** Type: {op.get('type')} ({'SEND' if op.get('type') == 7 else 'RECEIVE' if op.get('type') == 0 else 'OTHER'}) ***")
                        
                        if op.get('type') == 7:
                            print(f"      *** AIRDROP: {airdrop_wallet} -> {op.get('to')} ***")
                        elif op.get('type') == 0:
                            print(f"      *** RECEIVE: {op.get('from')} -> {airdrop_wallet} ***")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Check the output above to see if MURF transactions are found")
    print("Look for 'MURF TOKEN DETECTED' messages")

if __name__ == "__main__":
    main()
