#!/usr/bin/env python3
"""
Check Keeta API for OTC transactions
"""

import urllib.request
import json

def check_keeta_api():
    url = "https://rep2.main.network.api.keeta.com/api/node/ledger/history?limit=20"
    murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
    
    try:
        print(f"Fetching data from: {url}")
        response = urllib.request.urlopen(url, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        print(f"Total blocks: {len(data.get('blocks', []))}")
        
        otc_count = 0
        otc_transactions = []
        
        for block in data.get('blocks', []):
            block_hash = block.get('$hash', 'N/A')
            print(f"\nBlock: {block_hash[:20]}...")
            
            for operation in block.get('operations', []):
                if operation.get('type') == 7:
                    token = operation.get('token', '')
                    if token == murf_token:
                        otc_count += 1
                        amount = operation.get('amount', '0x0')
                        from_addr = operation.get('from', '')
                        
                        otc_transactions.append({
                            'block_hash': block_hash,
                            'amount': amount,
                            'from': from_addr,
                            'token': token
                        })
                        
                        print(f"  ✅ OTC Transaction found:")
                        print(f"     Token: {token[:20]}...")
                        print(f"     Amount: {amount}")
                        print(f"     From: {from_addr[:20]}...")
                    else:
                        print(f"  ❌ Type 7 but different token: {token[:20]}...")
                else:
                    print(f"  - Type {operation.get('type')} transaction")
        
        print(f"\n📊 Summary:")
        print(f"OTC transactions for MURF token: {otc_count}")
        print(f"Total OTC transactions found: {len(otc_transactions)}")
        
        if otc_transactions:
            print(f"\n🔗 Latest OTC Block Hash: {otc_transactions[0]['block_hash']}")
            print(f"🔗 Explorer Link: https://explorer.test.keeta.com/block/{otc_transactions[0]['block_hash']}")
        
        return otc_transactions
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    check_keeta_api()
