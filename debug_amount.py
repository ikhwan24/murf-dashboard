#!/usr/bin/env python3
"""
Debug script untuk cek amount parsing
"""

import requests
import json

def hex_to_decimal(hex_str):
    """Convert hex to decimal"""
    try:
        return int(hex_str, 16)
    except:
        return 0

def debug_amount():
    """Debug amount parsing"""
    print("🔍 Debug Amount Parsing")
    print("=" * 40)
    
    # Fetch data
    url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit=5"
    print(f"📡 Fetching: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Token IDs
    kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    
    print(f"📊 Found {len(data['history'])} history entries")
    
    # Check first entry
    entry = data['history'][0]
    if 'voteStaple' in entry and 'blocks' in entry['voteStaple']:
        blocks = entry['voteStaple']['blocks']
        
        for j, block in enumerate(blocks):
            block_hash = block.get('$hash', '')
            print(f"\n📦 Block {j+1}: {block_hash[:20]}...")
            
            if 'operations' in block:
                operations = block['operations']
                print(f"  🔧 Operations: {len(operations)}")
                
                for k, op in enumerate(operations):
                    op_type = op.get('type')
                    token = op.get('token', '')
                    amount_hex = op.get('amount', '0x0')
                    amount_decimal = hex_to_decimal(amount_hex)
                    amount_formatted = amount_decimal / 1e18
                    
                    print(f"\n    Op {k+1}:")
                    print(f"      Type: {op_type}")
                    print(f"      Token: {token}")
                    print(f"      Amount Hex: {amount_hex}")
                    print(f"      Amount Decimal: {amount_decimal}")
                    print(f"      Amount Formatted: {amount_formatted}")
                    
                    # Check if this is KTA or MURF
                    if token == kta_token:
                        print(f"      ✅ KTA token found!")
                    elif token == murf_token:
                        print(f"      ✅ MURF token found!")
                    else:
                        print(f"      ❌ Other token")

if __name__ == "__main__":
    debug_amount()

