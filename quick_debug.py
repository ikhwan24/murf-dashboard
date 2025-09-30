#!/usr/bin/env python3
"""
Quick debug untuk cek MURF parsing
"""

import requests
import json

def hex_to_decimal(hex_str):
    """Convert hex to decimal"""
    try:
        return int(hex_str, 16)
    except:
        return 0

def quick_debug():
    """Quick debug untuk cek MURF parsing"""
    print("🔍 Quick Debug MURF Parsing")
    print("=" * 40)
    
    # Fetch data
    url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit=10"
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
    
    # Check first few entries
    for i, entry in enumerate(data['history'][:3]):
        print(f"\n🔍 Entry {i+1}:")
        
        if 'voteStaple' in entry and 'blocks' in entry['voteStaple']:
            blocks = entry['voteStaple']['blocks']
            
            for j, block in enumerate(blocks):
                block_hash = block.get('$hash', '')
                print(f"  📦 Block {j+1}: {block_hash[:20]}...")
                
                if 'operations' in block:
                    operations = block['operations']
                    print(f"    🔧 Operations: {len(operations)}")
                    
                    for k, op in enumerate(operations):
                        op_type = op.get('type')
                        token = op.get('token', '')
                        amount_hex = op.get('amount', '0x0')
                        amount_decimal = hex_to_decimal(amount_hex)
                        amount_formatted = amount_decimal / 1e18
                        
                        print(f"      Op {k+1}: Type {op_type}, Amount: {amount_hex} = {amount_formatted}")
                        
                        # Check if this is KTA or MURF
                        if kta_token in token:
                            print(f"        ✅ KTA token found!")
                        elif murf_token in token:
                            print(f"        ✅ MURF token found!")
                        else:
                            print(f"        ❌ Other token")

if __name__ == "__main__":
    quick_debug()

