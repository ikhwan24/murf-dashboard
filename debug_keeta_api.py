#!/usr/bin/env python3
"""
Debug script untuk menganalisis Keeta API dan mencari transaksi type 7
untuk token MURF yang spesifik
"""

import urllib.request
import json
import sys

def fetch_keeta_data():
    """Fetch data from Keeta API"""
    url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit=100"
    
    try:
        print(f"🔍 Fetching data from: {url}")
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def analyze_transactions(data):
    """Analyze transactions to find type 7 for MURF token"""
    if not data or 'history' not in data:
        print("❌ No history data found")
        return
    
    history = data['history']
    print(f"📊 Total history entries: {len(history)}")
    
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    type_7_transactions = []
    
    for entry in history:
        if 'voteStaple' in entry and 'blocks' in entry['voteStaple']:
            blocks = entry['voteStaple']['blocks']
            
            for block in blocks:
                if 'operations' in block:
                    operations = block['operations']
                    
                    for op in operations:
                        # Cek apakah ini type 7 dan token MURF
                        if (op.get('type') == 7 and 
                            op.get('token') == murf_token):
                            
                            tx_hash = block.get('$hash', 'N/A')
                            amount = op.get('amount', 'N/A')
                            from_addr = op.get('from', 'N/A')
                            
                            type_7_transactions.append({
                                'tx_hash': tx_hash,
                                'amount': amount,
                                'from': from_addr,
                                'block_date': block.get('date', 'N/A'),
                                'block_operations': len(operations)
                            })
                            
                            print(f"\n✅ FOUND TYPE 7 TRANSACTION:")
                            print(f"   🔗 TX Hash: {tx_hash}")
                            print(f"   💰 Amount: {amount}")
                            print(f"   👤 From: {from_addr}")
                            print(f"   📅 Date: {block.get('date', 'N/A')}")
                            print(f"   🔢 Operations in block: {len(operations)}")
                            
                            # Cek operasi lain dalam block yang sama
                            print(f"   📋 Other operations in same block:")
                            for i, other_op in enumerate(operations):
                                if other_op.get('type') != 7:
                                    print(f"      {i+1}. Type {other_op.get('type')} - Token: {other_op.get('token', 'N/A')[:50]}...")
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total Type 7 MURF transactions found: {len(type_7_transactions)}")
    
    if type_7_transactions:
        print(f"\n🔗 Explorer links for found transactions:")
        for i, tx in enumerate(type_7_transactions, 1):
            if tx['tx_hash'] != 'N/A':
                explorer_link = f"https://explorer.test.keeta.com/block/{tx['tx_hash']}"
                print(f"   {i}. {explorer_link}")
    
    return type_7_transactions

def main():
    print("🚀 Debug Keeta API - Mencari Type 7 MURF Transactions")
    print("=" * 60)
    
    # Fetch data
    data = fetch_keeta_data()
    if not data:
        return
    
    # Analyze transactions
    transactions = analyze_transactions(data)
    
    print("\n" + "=" * 60)
    print("✅ Debug completed!")

if __name__ == "__main__":
    main()
