#!/usr/bin/env python3
"""
Analyze detailed trade information for Type 7 MURF transactions
"""

import requests
import json
from datetime import datetime

def hex_to_decimal(hex_string):
    """Convert hex string to decimal"""
    try:
        if hex_string.startswith('0x'):
            hex_string = hex_string[2:]
        return int(hex_string, 16)
    except:
        return 0

def analyze_trade_details():
    """Analyze detailed trade information"""
    print("🔍 Analyzing Trade Details for Type 7 MURF Transactions")
    print("=" * 60)
    
    # Fetch data from Keeta API
    url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit=100"
    print(f"📡 Fetching data from: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return
    
    if not data or 'history' not in data:
        print("❌ No history data found")
        return
    
    print(f"📊 Total history entries: {len(data['history'])}")
    
    # MURF token ID
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
    
    type_7_trades = []
    
    # Analyze each history entry
    for entry in data['history']:
        if 'voteStaple' in entry and 'blocks' in entry['voteStaple']:
            blocks = entry['voteStaple']['blocks']
            
            for block in blocks:
                if 'operations' in block:
                    operations = block['operations']
                    
                    # Look for Type 7 MURF transaction
                    type_7_op = None
                    related_ops = []
                    
                    for op in operations:
                        if (op.get('type') == 7 and 
                            op.get('token') == murf_token):
                            type_7_op = op
                        elif op.get('type') == 0:  # Regular transfer
                            related_ops.append(op)
                    
                    if type_7_op:
                        tx_hash = block.get('$hash', 'N/A')
                        date = block.get('date', 'N/A')
                        
                        # Get MURF amount
                        murf_amount_hex = type_7_op.get('amount', '0x0')
                        murf_amount = hex_to_decimal(murf_amount_hex)
                        
                        # Look for KTA amount in related operations
                        kta_amount = 0
                        kta_recipient = None
                        
                        for op in related_ops:
                            if op.get('token') == kta_token:
                                kta_amount_hex = op.get('amount', '0x0')
                                kta_amount_raw = hex_to_decimal(kta_amount_hex)
                                # Convert from wei to KTA (divide by 1e18)
                                kta_amount = kta_amount_raw / 1e18
                                kta_recipient = op.get('to', 'N/A')
                                break
                        
                        trade_info = {
                            'tx_hash': tx_hash,
                            'date': date,
                            'murf_amount': murf_amount,
                            'murf_amount_hex': murf_amount_hex,
                            'kta_amount': kta_amount,
                            'kta_recipient': kta_recipient,
                            'from_address': type_7_op.get('from', 'N/A'),
                            'exact': type_7_op.get('exact', False),
                            'all_operations': operations
                        }
                        
                        type_7_trades.append(trade_info)
                        
                        print(f"\n✅ FOUND TYPE 7 TRADE:")
                        print(f"   🔗 TX Hash: {tx_hash}")
                        print(f"   💰 MURF Amount: {murf_amount:,} MURF ({murf_amount_hex})")
                        print(f"   💎 KTA Amount: {kta_amount:,} KTA")
                        print(f"   👤 From: {type_7_op.get('from', 'N/A')}")
                        print(f"   📅 Date: {date}")
                        print(f"   🔢 Total operations in block: {len(operations)}")
                        
                        if kta_amount > 0:
                            exchange_rate = kta_amount / murf_amount if murf_amount > 0 else 0
                            print(f"   📊 Exchange Rate: 1 KTA = {exchange_rate:,.0f} MURF")
                            print(f"   📊 Exchange Rate: 1 MURF = {1/exchange_rate:.8f} KTA")
                        
                        print(f"   📋 All operations in block:")
                        for i, op in enumerate(operations, 1):
                            op_type = op.get('type', 'N/A')
                            op_token = op.get('token', 'N/A')
                            op_amount = op.get('amount', '0x0')
                            op_amount_dec = hex_to_decimal(op_amount)
                            
                            if op_type == 7:
                                print(f"      {i}. Type {op_type} (OTC) - {op_amount_dec:,} MURF")
                            elif op_type == 0:
                                print(f"      {i}. Type {op_type} (Transfer) - {op_amount_dec:,} {op_token[:20]}...")
                            else:
                                print(f"      {i}. Type {op_type} - {op_amount_dec:,} {op_token[:20]}...")
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total Type 7 MURF trades found: {len(type_7_trades)}")
    
    if type_7_trades:
        print(f"\n🔗 Explorer Links:")
        for trade in type_7_trades:
            print(f"   https://explorer.keeta.com/block/{trade['tx_hash']}")
    
    print("\n" + "=" * 60)
    print("✅ Analysis completed!")

if __name__ == "__main__":
    analyze_trade_details()
