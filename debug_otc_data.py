#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def fetch_keeta_data(limit=200):
    """Fetch data from Keeta API"""
    url = "https://api.keeta.com/v1/account/history"
    params = {
        "account": "keeta_aab4nfsiygnkaypqbwjp422xl4m4hsljz3bnq4unpfzs4blhyfr5ca2lsr3jeay",
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def analyze_otc_data(data):
    """Analyze OTC transactions from API data"""
    if not data or 'history' not in data:
        print("No history data found")
        return []
    
    otc_transactions = []
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
    
    print(f"Analyzing {len(data['history'])} history entries...")
    
    for i, entry in enumerate(data['history']):
        if 'operations' in entry:
            operations = entry['operations']
            
            # Look for Type 7 KTA operations
            type_7_kta = None
            type_0_murf = None
            
            for op in operations:
                if op.get('type') == 7 and op.get('token') == kta_token:
                    type_7_kta = op
                elif op.get('type') == 0 and op.get('token') == murf_token:
                    type_0_murf = op
            
            # If we found both Type 7 KTA and Type 0 MURF in the same block
            if type_7_kta and type_0_murf:
                try:
                    # Parse KTA amount
                    kta_amount_hex = type_7_kta.get('amount', '0x0')
                    kta_amount = int(kta_amount_hex, 16) / 1e18
                    
                    # Parse MURF amount
                    murf_amount_hex = type_0_murf.get('amount', '0x0')
                    murf_amount = int(murf_amount_hex, 16)
                    
                    if kta_amount > 0 and murf_amount > 0:
                        exchange_rate = murf_amount / kta_amount
                        
                        otc_transaction = {
                            'tx_hash': entry.get('$hash', 'N/A'),
                            'block_hash': entry.get('$hash', 'N/A'),
                            'kta_amount': kta_amount,
                            'murf_amount': murf_amount,
                            'exchange_rate': exchange_rate,
                            'from_address': type_7_kta.get('from', 'N/A'),
                            'to_address': type_0_murf.get('to', 'N/A'),
                            'timestamp': entry.get('date', datetime.now().isoformat())
                        }
                        
                        otc_transactions.append(otc_transaction)
                        print(f"Found OTC: {kta_amount:.2f} KTA <-> {murf_amount:,.0f} MURF (Rate: {exchange_rate:,.0f})")
                
                except Exception as e:
                    print(f"Error parsing OTC transaction: {e}")
    
    print(f"Total OTC transactions found: {len(otc_transactions)}")
    return otc_transactions

if __name__ == "__main__":
    print("Debugging OTC Data...")
    
    # Fetch data from API
    data = fetch_keeta_data(limit=200)
    if data:
        print(f"API data fetched: {len(data.get('history', []))} entries")
        
        # Analyze OTC data
        otc_transactions = analyze_otc_data(data)
        
        if otc_transactions:
            print(f"\nOTC Transactions Summary:")
            for i, tx in enumerate(otc_transactions[:5]):  # Show first 5
                print(f"  {i+1}. {tx['kta_amount']:.2f} KTA <-> {tx['murf_amount']:,.0f} MURF")
                print(f"     Rate: 1 KTA = {tx['exchange_rate']:,.0f} MURF")
                print(f"     Time: {tx['timestamp']}")
                print(f"     Hash: {tx['tx_hash'][:20]}...")
                print()
        else:
            print("No OTC transactions found in API data")
    else:
        print("Failed to fetch API data")
