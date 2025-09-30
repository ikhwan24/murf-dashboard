#!/usr/bin/env python3
"""
Debug Exchange Rate - Cek kenapa exchange rate tidak berubah
"""

import json
import urllib.request
from datetime import datetime

def hex_to_decimal(hex_string):
    """Convert hex string to decimal"""
    try:
        if hex_string.startswith('0x'):
            hex_string = hex_string[2:]
        return int(hex_string, 16)
    except:
        return 0

def fetch_keeta_data(limit=100):
    """Fetch data from Keeta API"""
    try:
        url = f"https://api.keeta.network/v1/history?limit={limit}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Error fetching Keeta data: {e}")
        return None

def analyze_otc_data(data):
    """Analyze OTC transactions"""
    if not data or 'history' not in data:
        return []
    
    blocks = data['history']
    otc_transactions = []
    
    kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    
    print(f"🔍 Analyzing {len(blocks)} blocks for OTC transactions...")
    
    for i, block in enumerate(blocks):
        if 'operations' not in block:
            continue
            
        operations = block['operations']
        kta_ops = []
        murf_ops = []
        
        # Cari Type 7 KTA dan Type 0 MURF
        for op in operations:
            if op.get('type') == 7 and op.get('token') == kta_token:
                kta_amount = hex_to_decimal(op.get('amount', '0x0')) / 1e18
                kta_ops.append({
                    'amount': kta_amount,
                    'from': op.get('from', 'N/A'),
                    'hash': block.get('$hash', 'N/A')[:12] + '...'
                })
            elif op.get('type') == 0 and op.get('token') == murf_token:
                murf_amount = hex_to_decimal(op.get('amount', '0x0'))
                murf_ops.append({
                    'amount': murf_amount,
                    'to': op.get('to', 'N/A'),
                    'hash': block.get('$hash', 'N/A')[:12] + '...'
                })
        
        # Cari pasangan dalam block yang sama
        if kta_ops and murf_ops:
            for kta_op in kta_ops:
                for murf_op in murf_ops:
                    if kta_op['amount'] > 0 and murf_op['amount'] > 0:
                        exchange_rate = murf_op['amount'] / kta_op['amount']
                        otc_transactions.append({
                            'kta_amount': kta_op['amount'],
                            'murf_amount': murf_op['amount'],
                            'exchange_rate': exchange_rate,
                            'from': kta_op['from'],
                            'to': murf_op['to'],
                            'hash': kta_op['hash'],
                            'date': block.get('date', 'N/A')
                        })
                        print(f"✅ OTC Found: {kta_op['amount']:.2f} KTA = {murf_op['amount']:,.0f} MURF (Rate: {exchange_rate:,.0f})")
    
    return otc_transactions

def main():
    print("🔍 Debug Exchange Rate - Cek kenapa tidak berubah")
    print("=" * 50)
    
    # Fetch data
    data = fetch_keeta_data(50)
    if not data:
        print("❌ Gagal fetch data")
        return
    
    # Analyze OTC
    otc_txs = analyze_otc_data(data)
    
    print(f"\n📊 Total OTC transactions found: {len(otc_txs)}")
    
    if otc_txs:
        latest = otc_txs[0]
        print(f"\n🎯 Latest OTC Transaction:")
        print(f"   KTA Amount: {latest['kta_amount']:.2f}")
        print(f"   MURF Amount: {latest['murf_amount']:,.0f}")
        print(f"   Exchange Rate: 1 KTA = {latest['exchange_rate']:,.0f} MURF")
        print(f"   Date: {latest['date']}")
        print(f"   Hash: {latest['hash']}")
        
        # Cek apakah rate berbeda dari 250,000
        if latest['exchange_rate'] != 250000:
            print(f"\n✅ Exchange rate BERBEDA dari hardcode!")
            print(f"   Hardcode: 250,000 MURF")
            print(f"   Real: {latest['exchange_rate']:,.0f} MURF")
        else:
            print(f"\n⚠️ Exchange rate SAMA dengan hardcode (250,000)")
    else:
        print("\n❌ Tidak ada OTC transactions ditemukan")
        print("   Ini mungkin kenapa exchange rate tidak berubah")

if __name__ == "__main__":
    main()
