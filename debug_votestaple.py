#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def debug_votestaple():
    """Debug voteStaple structure to find OTC data"""
    api_url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history"
    
    try:
        print("[DEBUG] Fetching API data...")
        response = requests.get(api_url, params={"limit": 5}, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] API data fetched: {len(data.get('history', []))} entries")
            
            # Analyze voteStaple structure
            for i, entry in enumerate(data['history'][:2]):
                print(f"\n[ENTRY {i+1}] VoteStaple Structure:")
                
                if 'voteStaple' in entry:
                    vs = entry['voteStaple']
                    print(f"  VoteStaple keys: {list(vs.keys())}")
                    
                    if 'blocks' in vs:
                        print(f"  Blocks: {len(vs['blocks'])}")
                        for j, block in enumerate(vs['blocks'][:2]):
                            print(f"    Block {j+1}: {block[:20]}...")
                    
                    if 'votes' in vs:
                        print(f"  Votes: {len(vs['votes'])}")
                        for j, vote in enumerate(vs['votes'][:2]):
                            print(f"    Vote {j+1}: {list(vote.keys())}")
                            if 'issuer' in vote:
                                print(f"      Issuer: {vote['issuer'][:20]}...")
                            if 'validityFrom' in vote:
                                print(f"      ValidityFrom: {vote['validityFrom']}")
                    
                    if '$binary' in vs:
                        print(f"  Binary data: {len(vs['$binary'])} chars")
                        
        else:
            print(f"[ERROR] API Error: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    debug_votestaple()
