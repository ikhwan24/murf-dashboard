#!/usr/bin/env python3
"""
Test script untuk memvalidasi parsing OTC data dari Keeta Network
"""

import json
from keeta_monitor import KeetaMonitor

def test_otc_parsing():
    """Test parsing data OTC yang sebenarnya"""
    
    # Data sample dari API yang sebenarnya
    sample_data = {
        "votes": [
            {
                "issuer": "keeta_aablpogflko72eusdhuuqgsto2rwcvy2m5mo5snmvrmbacz3qczwjtwpmzf5ufq",
                "serial": "0x5BF4",
                "blocks": [
                    "38799DE028950C9934E72587F97209E17C5CB4A38C4295C4A2CDD63CFF510816",
                    "C8221503B533E0460125585007AD314B3CBF73B1D7C3C34AAE97E90D4459136B",
                    "C86BDE339E1A8E2B6AC539E9A03A9DB525EFF2C978A95863AB8AC147E88EC9A1"
                ],
                "validityFrom": "2025-09-29T23:38:27.340Z",
                "validityTo": "3026-01-31T00:00:00.000Z",
                "signature": "3045022100C970F9EC3C8F5CA905FBBE44E0B52549F25E56220FCD6083D319624CA58C4C5502202961EA81CEE80101816BAF393FB352566B9FBA432D36111C67AE710F6CB90BB0",
                "$trusted": False,
                "$permanent": True,
                "$uid": "ID=keeta_aablpogflko72eusdhuuqgsto2rwcvy2m5mo5snmvrmbacz3qczwjtwpmzf5ufq/Serial=23540",
                "$id": "6DA7722B0F63D8A39CDFF807C37C90D9899591131EB7623D7E3DF90D2096329B"
            }
        ],
        "blocks": [
            {
                "version": 1,
                "date": "2025-09-29T23:34:50.504Z",
                "previous": "D8ADB7FCBA21DA04A3B0EFD7ED6B71629889D1664271BF6B4C29E86DF048A188",
                "account": "keeta_aab7l3uugqfwl53mwluh56n5o7zmn5v2ni7wdmlp6a4wd4aykllq6rhjjjxs6mq",
                "purpose": 0,
                "signer": "keeta_aab7l3uugqfwl53mwluh56n5o7zmn5v2ni7wdmlp6a4wd4aykllq6rhjjjxs6mq",
                "network": "0x5382",
                "operations": [
                    {
                        "type": 7,  # OTC SWAP
                        "amount": "0x649D2C967D9500000",  # 30M KTA
                        "token": "keeta_anqdilpazdekdu4acw65fj7smltcp26wbrildkqtszqvverljpwpezmd44ssg",  # KTA
                        "from": "keeta_aab4anyllhowvsnjhpbynd6fvrdm4rby3xs4aoq5m4ttlhjhnrabtyxiqnmx25y",
                        "exact": True
                    },
                    {
                        "type": 0,  # Transfer
                        "to": "keeta_aab4anyllhowvsnjhpbynd6fvrdm4rby3xs4aoq5m4ttlhjhnrabtyxiqnmx25y",
                        "amount": "0x1C9C380",  # 30M MURF
                        "token": "keeta_ao7nitutebhm2pkrfbtniepivaw324hecyb43wsxts5rrhi2p5ckgof37racm"  # MURF
                    }
                ],
                "$hash": "C8221503B533E0460125585007AD314B3CBF73B1D7C3C34AAE97E90D4459136B",
                "$opening": False,
                "signature": "01024465111FF15F214036A4E5A7FE7E18A0280E3F888C4A23959B16A89586663FF2AA392CC9E639DAA4B155EA46C85E9C9440EA0F5C946CC39A8CA1AD2F72B0"
            }
        ]
    }
    
    print("🧪 Testing OTC Parsing dengan Data Real")
    print("=" * 60)
    
    # Inisialisasi monitor
    monitor = KeetaMonitor()
    
    # Test parsing OTC operation
    otc_operation = sample_data["blocks"][0]["operations"][0]
    block_data = sample_data["blocks"][0]
    
    print(f"📊 OTC Operation Data:")
    print(f"   Type: {otc_operation['type']}")
    print(f"   Amount: {otc_operation['amount']}")
    print(f"   Token: {otc_operation['token'][:50]}...")
    print(f"   From: {otc_operation['from'][:50]}...")
    print(f"   Exact: {otc_operation['exact']}")
    print()
    
    # Test hex to decimal conversion
    kta_amount = monitor.hex_to_decimal(otc_operation['amount'])
    print(f"🔢 Hex to Decimal Conversion:")
    print(f"   {otc_operation['amount']} = {kta_amount:,}")
    print()
    
    # Test parsing transaksi
    trade_data = monitor.parse_transaction(otc_operation, block_data)
    
    if trade_data:
        print(f"✅ Parsed Trade Data:")
        print(f"   Timestamp: {trade_data['timestamp']}")
        print(f"   Block Hash: {trade_data['block_hash']}")
        print(f"   Trade Type: {trade_data['trade_type']}")
        print(f"   Amount: {trade_data['amount_decimal']:,}")
        print(f"   Is OTC: {trade_data.get('is_otc', False)}")
        
        if trade_data.get('is_otc'):
            otc_details = trade_data.get('otc_details', {})
            print(f"   OTC Details:")
            print(f"     From Address: {otc_details.get('from_address', '')[:50]}...")
            print(f"     Exact: {otc_details.get('exact', False)}")
            print(f"     OTC Type: {otc_details.get('otc_type', 'unknown')}")
            print(f"     Exchange Ratio: {otc_details.get('exchange_ratio', 0):.8f}")
            print(f"     Counterpart Amount: {otc_details.get('counterpart_amount', 0):,}")
            print(f"     Counterpart Token: {otc_details.get('counterpart_token', '')[:50]}...")
            
            # Cek related operations
            related_ops = otc_details.get('related_operations', [])
            if related_ops:
                print(f"     Related Operations: {len(related_ops)}")
                for i, op in enumerate(related_ops):
                    print(f"       {i+1}. {op['amount_decimal']:,} {op['token'][:30]}... → {op['to'][:30]}...")
    else:
        print("❌ Failed to parse trade data")
    
    print()
    print("🎯 Expected vs Actual:")
    print(f"   Expected: 30M MURF ⇄ 30M KTA (1:1 ratio)")
    print(f"   Actual KTA: {kta_amount:,}")
    
    # Cek counterpart operation
    counterpart_op = sample_data["blocks"][0]["operations"][1]
    murf_amount = monitor.hex_to_decimal(counterpart_op['amount'])
    print(f"   Actual MURF: {murf_amount:,}")
    
    if kta_amount > 0 and murf_amount > 0:
        ratio = kta_amount / murf_amount
        print(f"   Actual Ratio: {ratio:.8f}")
        print(f"   Match with image: {'✅' if ratio == 1.0 else '❌'}")

if __name__ == "__main__":
    test_otc_parsing()
