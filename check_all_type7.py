#!/usr/bin/env python3
"""
Check semua Type 7 transactions untuk debug
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

def analyze_all_type7(data):
    """Analyze semua Type 7 transactions"""
    if not data or 'history' not in data:
        print("❌ No data")
        return
    
    history = data['history']
    print(f"📊 Analyzing {len(history)} history entries...")
    
    all_type7 = []
    murf_type7 = []
    
    for i, entry in enumerate(history):
        if 'voteStaple' in entry and 'blocks' in entry['voteStaple']:
            blocks = entry['voteStaple']['blocks']
            
            for j, block in enumerate(blocks):
                if 'operations' in block:
                    operations = block['operations']
                    
                    for k, op in enumerate(operations):
                        if op.get('type') == 7:  # Type 7 transaction
                            token = op.get('token', '')
                            amount = hex_to_decimal(op.get('amount', '0x0'))
                            amount_formatted = f"{amount/1e18:.6f}" if amount > 0 else "0"
                            
                            type7_info = {
                                'entry': i+1,
                                'block': j+1,
                                'operation': k+1,
                                'token': token,
                                'amount': amount_formatted,
                                'date': block.get('date', 'N/A'),
                                'hash': block.get('$hash', 'N/A'),
                                'from': op.get('from', 'N/A'),
                                'exact': op.get('exact', False)
                            }
                            
                            all_type7.append(type7_info)
                            
                            # Check if it's MURF token
                            if 'keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm' in token:
                                murf_type7.append(type7_info)
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Total Type 7 transactions found: {len(all_type7)}")
    print(f"✅ MURF Type 7 transactions found: {len(murf_type7)}")
    
    if all_type7:
        print(f"\n🔍 All Type 7 transactions:")
        for i, tx in enumerate(all_type7):
            print(f"\n  {i+1}. Entry {tx['entry']}, Block {tx['block']}, Op {tx['operation']}")
            print(f"     🕐 Date: {tx['date']}")
            print(f"     💰 Amount: {tx['amount']}")
            print(f"     🪙 Token: {tx['token'][:30]}...")
            print(f"     👤 From: {tx['from'][:30]}...")
            print(f"     ✅ Exact: {tx['exact']}")
            print(f"     🔗 Hash: {tx['hash'][:20]}...")
    
    if murf_type7:
        print(f"\n🎯 MURF Type 7 transactions:")
        for i, tx in enumerate(murf_type7):
            print(f"\n  {i+1}. Entry {tx['entry']}, Block {tx['block']}, Op {tx['operation']}")
            print(f"     🕐 Date: {tx['date']}")
            print(f"     💰 Amount: {tx['amount']} MURF")
            print(f"     👤 From: {tx['from'][:30]}...")
            print(f"     ✅ Exact: {tx['exact']}")
            print(f"     🔗 Hash: {tx['hash'][:20]}...")
    else:
        print(f"\n❌ No MURF Type 7 transactions found")
        print(f"💡 Possible reasons:")
        print(f"  • Transaction belum confirmed")
        print(f"  • Transaction bukan Type 7")
        print(f"  • Token ID salah")
        print(f"  • API delay")

def main():
    print("🔍 Check All Type 7 Transactions")
    print("=" * 50)
    
    data = fetch_keeta_data(limit=100)
    if data:
        analyze_all_type7(data)
    else:
        print("❌ Failed to fetch data")

if __name__ == "__main__":
    main()
