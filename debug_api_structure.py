#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def debug_api_structure():
    """Debug API structure to understand data format"""
    api_url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history"
    
    try:
        print("[DEBUG] Fetching API data...")
        response = requests.get(api_url, params={"limit": 10}, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] API data fetched: {len(data.get('history', []))} entries")
            
            # Analyze first few entries
            for i, entry in enumerate(data['history'][:3]):
                print(f"\n[ENTRY {i+1}] Structure:")
                print(f"  Keys: {list(entry.keys())}")
                
                if 'operations' in entry:
                    print(f"  Operations: {len(entry['operations'])}")
                    for j, op in enumerate(entry['operations'][:3]):
                        print(f"    Op {j+1}: type={op.get('type')}, token={op.get('token', '')[:30]}...")
                        print(f"           amount={op.get('amount', 'N/A')}, from={op.get('from', 'N/A')[:20]}...")
                        print(f"           to={op.get('to', 'N/A')[:20]}...")
                else:
                    print("  No operations found")
                
                if '$hash' in entry:
                    print(f"  Hash: {entry['$hash'][:20]}...")
                if 'date' in entry:
                    print(f"  Date: {entry['date']}")
                    
        else:
            print(f"[ERROR] API Error: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    debug_api_structure()
