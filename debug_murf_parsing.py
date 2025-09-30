#!/usr/bin/env python3
"""
Debug script untuk cek kenapa MURF amount = 0
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

def debug_murf_parsing(data):
    """Debug MURF parsing untuk OTC transactions"""
    if not data or 'history' not in data:
        print("❌ No data")
        return
    
    history = data['history']
    print(f"📊 Debugging MURF parsing in {len(history)} history entries...")
    
    # Token IDs
    kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    
    otc_count = 0
    
    for i, entry in enumerate(history[:10]):  # Check first 10 entries
        print(f"\n🔍 Entry {i+1}:")
        
        if 'voteStaple' in entry and 'blocks' in entry['voteStaple']:
            blocks = entry['voteStaple']['blocks']
            
            for j, block in enumerate(blocks):
                if 'operations' in block:
                    operations = block['operations']
                    print(f"  📦 Block {j+1}: {len(operations)} operations")
                    
                    # Cari OTC pair
                    type7_kta = None
                    type0_murf = None
                    
                    for k, op in enumerate(operations):
                        op_type = op.get('type')
                        token = op.get('token', '')
                        amount_hex = op.get('amount', '0x0')
                        amount_decimal = hex_to_decimal(amount_hex)
                        amount_formatted = amount_decimal / 1e18
                        
                        print(f"    🔧 Op {k+1}: Type {op_type}, Token: {token[:30]}..., Amount: {amount_hex} = {amount_formatted}")
                        
                        # Type 7 dengan KTA token
                        if op_type == 7 and kta_token in token:
                            type7_kta = {
                                'amount': amount_decimal,
                                'from': op.get('from', 'N/A'),
                                'exact': op.get('exact', False)
                            }
                            print(f"      ✅ Found Type 7 KTA: {amount_formatted} KTA")
                        
                        # Type 0 dengan MURF token
                        elif op_type == 0 and murf_token in token:
                            type0_murf = {
                                'amount': amount_decimal,
                                'to': op.get('to', 'N/A')
                            }
                            print(f"      ✅ Found Type 0 MURF: {amount_formatted} MURF")
                    
                    # Jika ada keduanya, ini adalah OTC transaction
                    if type7_kta and type0_murf:
                        kta_amount = type7_kta['amount'] / 1e18
                        murf_amount = type0_murf['amount'] / 1e18
                        
                        print(f"      🎯 OTC PAIR FOUND!")
                        print(f"        KTA: {kta_amount:.6f}")
                        print(f"        MURF: {murf_amount:.6f}")
                        print(f"        Exchange Rate: 1 KTA = {murf_amount/kta_amount:.2f} MURF" if kta_amount > 0 else "        Exchange Rate: N/A")
                        
                        otc_count += 1
                    elif type7_kta:
                        print(f"      ⚠️  Type 7 KTA found but no Type 0 MURF")
                    elif type0_murf:
                        print(f"      ⚠️  Type 0 MURF found but no Type 7 KTA")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ OTC pairs found: {otc_count}")

def main():
    print("🔍 Debug MURF Parsing")
    print("=" * 50)
    
    data = fetch_keeta_data(limit=100)
    if data:
        debug_murf_parsing(data)
    else:
        print("❌ Failed to fetch data")

if __name__ == "__main__":
    main()
