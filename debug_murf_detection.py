#!/usr/bin/env python3
"""
Debug script untuk cek kenapa MURF tidak terdeteksi
"""

import requests
import json
from datetime import datetime

def fetch_keeta_data(limit=100):
    """Fetch data dari Keeta API"""
    url = f"https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit={limit}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def hex_to_decimal(hex_str):
    """Convert hex to decimal"""
    try:
        return int(hex_str, 16)
    except:
        return 0

def debug_specific_block(data):
    """Debug block 604E4BD30627DDC0068B... yang seharusnya ada MURF"""
    if not data or 'history' not in data:
        print("❌ No data")
        return
    
    history = data['history']
    target_hash = "604E4BD30627DDC0068B"
    
    # Token IDs
    kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    
    print(f"🔍 Looking for block with hash containing: {target_hash}")
    
    for i, entry in enumerate(history):
        if 'voteStaple' in entry and 'blocks' in entry['voteStaple']:
            blocks = entry['voteStaple']['blocks']
            
            for j, block in enumerate(blocks):
                block_hash = block.get('$hash', '')
                
                if target_hash in block_hash:
                    print(f"\n🎯 FOUND TARGET BLOCK!")
                    print(f"   Entry: {i+1}, Block: {j+1}")
                    print(f"   Hash: {block_hash}")
                    print(f"   Date: {block.get('date', 'N/A')}")
                    
                    if 'operations' in block:
                        operations = block['operations']
                        print(f"   Operations: {len(operations)}")
                        
                        for k, op in enumerate(operations):
                            op_type = op.get('type')
                            token = op.get('token', '')
                            amount_hex = op.get('amount', '0x0')
                            amount_decimal = hex_to_decimal(amount_hex)
                            amount_formatted = amount_decimal / 1e18
                            
                            print(f"\n     Operation {k+1}:")
                            print(f"       Type: {op_type}")
                            print(f"       Token: {token}")
                            print(f"       Amount: {amount_hex} = {amount_formatted}")
                            print(f"       From: {op.get('from', 'N/A')}")
                            print(f"       To: {op.get('to', 'N/A')}")
                            
                            # Check if this is KTA or MURF
                            if kta_token in token:
                                print(f"       ✅ This is KTA token")
                            elif murf_token in token:
                                print(f"       ✅ This is MURF token")
                            else:
                                print(f"       ❌ Unknown token")
                    
                    return
    
    print(f"❌ Block with hash {target_hash} not found")

def main():
    print("🔍 Debug MURF Detection")
    print("=" * 50)
    
    data = fetch_keeta_data(limit=100)
    if data:
        debug_specific_block(data)
    else:
        print("❌ Failed to fetch data")

if __name__ == "__main__":
    main()

