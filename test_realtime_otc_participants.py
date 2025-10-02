#!/usr/bin/env python3
"""
Test Real-time OTC Participants Addition
"""

from smart_holders_manager import SmartHoldersManager
from otc_transactions_db import OTCTransactionsDB
from murf_holders_db import MURFHoldersDB
from datetime import datetime

def test_realtime_otc_participants():
    print("Testing Real-time OTC Participants Addition...")
    print("=" * 60)
    
    try:
        # Initialize components
        smart_holders = SmartHoldersManager()
        otc_db = OTCTransactionsDB()
        holders_db = MURFHoldersDB()
        
        print("[OK] All components initialized")
        
        # Get current state
        print("\n[INFO] Current State:")
        current_otc = otc_db.get_latest_otc_transactions(limit=5)
        current_holders = holders_db.get_top_holders(10)
        
        print(f"  - OTC Transactions in DB: {len(current_otc)}")
        print(f"  - Current Holders: {len(current_holders)}")
        
        if current_otc:
            print(f"  - Latest OTC: {current_otc[0].get('from_address', 'N/A')[:20]}... -> {current_otc[0].get('to_address', 'N/A')[:20]}...")
        
        # Test OTC participant extraction
        print("\n[INFO] Testing OTC Participant Extraction:")
        otc_participants = smart_holders.extract_otc_participants()
        print(f"  - Total OTC Participants: {len(otc_participants)}")
        
        # Show sample participants
        for i, participant in enumerate(otc_participants[:5]):
            print(f"    {i+1}. {participant[:30]}...")
        
        # Test adding participants to holders
        print("\n[INFO] Testing Participant Addition:")
        initial_holder_count = len(holders_db.get_top_holders(1000))
        print(f"  - Initial Holder Count: {initial_holder_count}")
        
        new_holders_added = smart_holders.update_holders_from_otc()
        print(f"  - New Holders Added: {new_holders_added}")
        
        final_holder_count = len(holders_db.get_top_holders(1000))
        print(f"  - Final Holder Count: {final_holder_count}")
        
        # Verify the process works
        if new_holders_added > 0:
            print(f"\n[SUCCESS] Real-time addition working! Added {new_holders_added} new holders")
        else:
            print(f"\n[INFO] No new holders added (all participants already tracked)")
        
        # Test specific addresses from recent OTC
        if current_otc:
            print(f"\n[INFO] Testing Recent OTC Addresses:")
            recent_otc = current_otc[0]
            from_addr = recent_otc.get('from_address', '')
            to_addr = recent_otc.get('to_address', '')
            
            if from_addr:
                balance_from = smart_holders.get_current_balance(from_addr)
                print(f"  - Sender Balance: {balance_from:,} MURF" if balance_from else "  - Sender: No MURF balance")
            
            if to_addr:
                balance_to = smart_holders.get_current_balance(to_addr)
                print(f"  - Receiver Balance: {balance_to:,} MURF" if balance_to else "  - Receiver: No MURF balance")
        
        print(f"\n[SUCCESS] Real-time OTC participant addition test completed!")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_realtime_otc_participants()
