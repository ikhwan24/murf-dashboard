#!/usr/bin/env python3
"""
Debug script untuk cek OTC transaction yang benar
OTC = Type 7 (KTA) + Type 0 (MURF) dalam block yang sama
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

def analyze_otc_pairs(data):
    """Analyze OTC pairs: Type 7 (KTA) + Type 0 (MURF) dalam block yang sama"""
    if not data or 'history' not in data:
        print("❌ No data")
        return
    
    history = data['history']
    print(f"📊 Analyzing {len(history)} history entries for OTC pairs...")
    
    # Token IDs
    kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    
    otc_pairs = []
    
    for i, entry in enumerate(history):
        if 'voteStaple' in entry and 'blocks' in entry['voteStaple']:
            blocks = entry['voteStaple']['blocks']
            
            for j, block in enumerate(blocks):
                if 'operations' in block:
                    operations = block['operations']
                    
                    # Cari Type 7 (KTA) dan Type 0 (MURF) dalam block yang sama
                    type7_kta = None
                    type0_murf = None
                    
                    for k, op in enumerate(operations):
                        op_type = op.get('type')
                        token = op.get('token', '')
                        
                        # Type 7 dengan KTA token
                        if op_type == 7 and kta_token in token:
                            type7_kta = {
                                'operation': k+1,
                                'amount': hex_to_decimal(op.get('amount', '0x0')),
                                'from': op.get('from', 'N/A'),
                                'exact': op.get('exact', False)
                            }
                        
                        # Type 0 dengan MURF token
                        elif op_type == 0 and murf_token in token:
                            type0_murf = {
                                'operation': k+1,
                                'amount': hex_to_decimal(op.get('amount', '0x0')),
                                'to': op.get('to', 'N/A')
                            }
                    
                    # Jika ada keduanya, ini adalah OTC pair
                    if type7_kta and type0_murf:
                        kta_amount = type7_kta['amount'] / 1e18
                        murf_amount = type0_murf['amount'] / 1e18
                        
                        otc_info = {
                            'entry': i+1,
                            'block': j+1,
                            'date': block.get('date', 'N/A'),
                            'hash': block.get('$hash', 'N/A'),
                            'kta_amount': f"{kta_amount:.6f}",
                            'murf_amount': f"{murf_amount:.6f}",
                            'from': type7_kta['from'],
                            'to': type0_murf['to'],
                            'exact': type7_kta['exact'],
                            'exchange_rate': f"{murf_amount/kta_amount:.2f}" if kta_amount > 0 else "0"
                        }
                        
                        otc_pairs.append(otc_info)
    
    print(f"\n📊 RESULTS:")
    print(f"✅ OTC pairs found: {len(otc_pairs)}")
    
    if otc_pairs:
        print(f"\n🎯 OTC Transactions (Type 7 KTA + Type 0 MURF):")
        for i, otc in enumerate(otc_pairs):
            print(f"\n  {i+1}. Entry {otc['entry']}, Block {otc['block']}")
            print(f"     🕐 Date: {otc['date']}")
            print(f"     💰 KTA Amount: {otc['kta_amount']} KTA")
            print(f"     💰 MURF Amount: {otc['murf_amount']} MURF")
            print(f"     📊 Exchange Rate: 1 KTA = {otc['exchange_rate']} MURF")
            print(f"     👤 From: {otc['from'][:30]}...")
            print(f"     👤 To: {otc['to'][:30]}...")
            print(f"     ✅ Exact: {otc['exact']}")
            print(f"     🔗 Hash: {otc['hash'][:20]}...")
    else:
        print(f"\n❌ No OTC pairs found")
        print(f"💡 OTC = Type 7 (KTA) + Type 0 (MURF) dalam block yang sama")

def main():
    print("🔍 Debug Correct OTC Detection")
    print("=" * 50)
    print("OTC = Type 7 (KTA) + Type 0 (MURF) dalam block yang sama")
    
    data = fetch_keeta_data(limit=100)
    if data:
        analyze_otc_pairs(data)
    else:
        print("❌ Failed to fetch data")

if __name__ == "__main__":
    main()
