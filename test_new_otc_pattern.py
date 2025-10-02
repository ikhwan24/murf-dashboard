#!/usr/bin/env python3
"""
Test New OTC Pattern Detection
Test the transaction provided by user
"""

import json
from real_live_dashboard import RealLiveAPIClient

def test_new_otc_transaction():
    print("Testing New OTC Transaction Pattern...")
    print("=" * 60)
    
    # Transaction data provided by user
    transaction = {
        "version": 1,
        "date": "2025-10-02T12:38:41.654Z",
        "previous": "CB43A4515F9FA68CDC3340210117CD76CFD28D9A69D01539E12A9CC028D0BBA1",
        "account": "keeta_aabdoy4sfb3wfmsbsdmwwva6rgwily5uoyc3ckkfjvscpajii6qelf3dxh6veoa",
        "purpose": 0,
        "signer": "keeta_aabdoy4sfb3wfmsbsdmwwva6rgwily5uoyc3ckkfjvscpajii6qelf3dxh6veoa",
        "network": "0x5382",
        "operations": [
            {
                "type": 7,
                "amount": "0x1AB3F00",  # 28,000,000 MURF
                "token": "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm",  # MURF
                "from": "keeta_aabmzag2e2qttlrmiws3iyje6l73oe7x4skuoyqinuiwmr5cfpnmfzvqkqd2zlq",
                "exact": True
            },
            {
                "type": 0,
                "to": "keeta_aabmzag2e2qttlrmiws3iyje6l73oe7x4skuoyqinuiwmr5cfpnmfzvqkqd2zlq",
                "amount": "0x7B2A557A6D9780000",  # 560 KTA
                "token": "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"  # KTA
            }
        ],
        "$hash": "4CC50BFC2DB17DFF952DCD4BC78DF4DE2199A73150A5025455D6C767EC4BF49D",
        "$opening": False,
        "signature": "C1B098B56F44F7C8A9C44286A4ABA51BED19DEDF6E73CB46F49574E50DC2A648301A1DC776543487BCEFF4D995679CBA115DA7A7B6E71BBCD1C40B6E505156DF"
    }
    
    print("[INFO] Transaction Analysis:")
    print(f"  - Hash: {transaction['$hash']}")
    print(f"  - Account: {transaction['account'][:30]}...")
    print(f"  - Date: {transaction['date']}")
    
    # Analyze operations
    operations = transaction['operations']
    print(f"\n[INFO] Operations ({len(operations)}):")
    
    for i, op in enumerate(operations):
        op_type = op.get('type')
        token = op.get('token', '')
        amount_hex = op.get('amount', '0x0')
        
        # Convert hex to decimal
        try:
            amount_decimal = int(amount_hex, 16)
        except:
            amount_decimal = 0
        
        print(f"  {i+1}. Type {op_type}:")
        print(f"     - Token: {token[:30]}...")
        print(f"     - Amount (hex): {amount_hex}")
        print(f"     - Amount (decimal): {amount_decimal:,}")
        
        # Identify token type
        murf_token = "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"
        kta_token = "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg"
        
        if murf_token in token:
            if op_type == 7:
                print(f"     - MURF SEND: {amount_decimal:,} MURF")
                print(f"     - From: {op.get('from', 'N/A')[:30]}...")
            elif op_type == 0:
                print(f"     - MURF RECEIVE: {amount_decimal:,} MURF")
                print(f"     - To: {op.get('to', 'N/A')[:30]}...")
        elif kta_token in token:
            kta_amount = amount_decimal / 1e18
            if op_type == 7:
                print(f"     - KTA SEND: {kta_amount:.2f} KTA")
                print(f"     - From: {op.get('from', 'N/A')[:30]}...")
            elif op_type == 0:
                print(f"     - KTA RECEIVE: {kta_amount:.2f} KTA")
                print(f"     - To: {op.get('to', 'N/A')[:30]}...")
    
    # Test with API client
    print(f"\n[INFO] Testing with API Client:")
    try:
        client = RealLiveAPIClient()
        
        # Create mock API response
        mock_data = {
            "blocks": [transaction]
        }
        
        print(f"[INFO] Running analyze_keeta_data...")
        result = client.analyze_keeta_data(mock_data)
        
        print(f"\n[RESULT] Analysis Result:")
        print(f"  - Total Blocks: {result.get('total_blocks', 0)}")
        print(f"  - OTC Transactions: {len(result.get('type_7_murf_txs', []))}")
        
        if result.get('type_7_murf_txs'):
            otc_tx = result['type_7_murf_txs'][0]
            print(f"\n[SUCCESS] OTC Transaction Detected:")
            print(f"  - Hash: {otc_tx.get('tx_hash', 'N/A')}")
            print(f"  - KTA Amount: {otc_tx.get('kta_amount', 0):.2f}")
            print(f"  - MURF Amount: {otc_tx.get('murf_amount', 0):,}")
            print(f"  - Exchange Rate: 1 KTA = {otc_tx.get('exchange_rate', 0):,.0f} MURF")
            print(f"  - From: {otc_tx.get('from_address', 'N/A')[:30]}...")
            print(f"  - To: {otc_tx.get('to_address', 'N/A')[:30]}...")
        else:
            print(f"\n[ERROR] OTC Transaction NOT detected!")
            print(f"[DEBUG] This should be detected as Pattern 2: Type 7 MURF + Type 0 KTA")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_otc_transaction()
