#!/usr/bin/env python3
"""
Debug script untuk cek kenapa OTC transaction belum terdeteksi
"""

import requests
import json
from datetime import datetime

def fetch_keeta_data(limit=100):
    """Fetch data dari Keeta API"""
    url = f"https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit={limit}"
    
    try:
        print(f"🔍 Fetching data dari: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def hex_to_decimal(hex_str):
    """Convert hex to decimal"""
    try:
        return int(hex_str, 16)
    except:
        return 0

def analyze_recent_transactions(data):
    """Analyze recent transactions untuk cari OTC"""
    if not data or 'history' not in data:
        print("❌ No history data found")
        return
    
    history = data['history']
    print(f"📊 Total history entries: {len(history)}")
    
    # MURF token ID
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    
    type_7_found = 0
    recent_blocks = []
    
    for i, entry in enumerate(history[:10]):  # Check last 10 entries
        print(f"\n🔍 Checking entry {i+1}:")
        
        if 'voteStaple' in entry and 'blocks' in entry['voteStaple']:
            blocks = entry['voteStaple']['blocks']
            print(f"  📦 Blocks in entry: {len(blocks)}")
            
            for j, block in enumerate(blocks):
                if 'operations' in block:
                    operations = block['operations']
                    print(f"    🔧 Operations in block {j+1}: {len(operations)}")
                    
                    for k, op in enumerate(operations):
                        op_type = op.get('type', 'unknown')
                        token = op.get('token', '')
                        
                        print(f"      📋 Operation {k+1}: Type {op_type}, Token: {token[:20]}...")
                        
                        # Check for Type 7 with MURF token
                        if op_type == 7 and murf_token in token:
                            type_7_found += 1
                            amount = hex_to_decimal(op.get('amount', '0x0'))
                            amount_formatted = f"{amount/1e18:.2f}" if amount > 0 else "0"
                            
                            print(f"        ✅ FOUND TYPE 7 MURF TRANSACTION!")
                            print(f"        💰 Amount: {amount_formatted} MURF")
                            print(f"        🕐 Block hash: {block.get('$hash', 'N/A')}")
                            print(f"        📅 Date: {block.get('date', 'N/A')}")
                            
                            recent_blocks.append({
                                'block_hash': block.get('$hash', ''),
                                'date': block.get('date', ''),
                                'amount': amount_formatted,
                                'operation': op
                            })
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Type 7 MURF transactions found: {type_7_found}")
    
    if recent_blocks:
        print(f"\n🕐 Recent Type 7 MURF transactions:")
        for block in recent_blocks:
            print(f"  • {block['date'][:19]} - {block['amount']} MURF")
            print(f"    Hash: {block['block_hash'][:20]}...")
    else:
        print(f"\n❌ No recent Type 7 MURF transactions found")
        print(f"💡 Possible reasons:")
        print(f"  • Transaction belum confirmed")
        print(f"  • Transaction bukan Type 7")
        print(f"  • Token ID berbeda")
        print(f"  • API delay")

def check_api_delay():
    """Check if there's API delay"""
    print("\n⏰ Checking API response time...")
    
    start_time = datetime.now()
    data = fetch_keeta_data(limit=10)
    end_time = datetime.now()
    
    response_time = (end_time - start_time).total_seconds()
    print(f"📡 API response time: {response_time:.2f} seconds")
    
    if response_time > 5:
        print("⚠️  Slow API response - might be delay in transaction detection")
    else:
        print("✅ API response is fast")

def main():
    print("🔍 Debug OTC Transaction Detection")
    print("=" * 50)
    
    # Check API delay
    check_api_delay()
    
    # Fetch and analyze data
    print("\n📊 Fetching latest data...")
    data = fetch_keeta_data(limit=100)
    
    if data:
        analyze_recent_transactions(data)
        
        print(f"\n💡 Debugging Tips:")
        print(f"1. Cek apakah transaksi sudah confirmed di blockchain")
        print(f"2. Pastikan transaksi adalah Type 7 (OTC/SWAP)")
        print(f"3. Pastikan token ID benar: keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm")
        print(f"4. API mungkin ada delay 1-2 menit")
        print(f"5. Coba refresh dashboard setelah beberapa menit")
    else:
        print("❌ Failed to fetch data from API")

if __name__ == "__main__":
    main()
