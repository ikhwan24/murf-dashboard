#!/usr/bin/env python3
"""
Test Smart Holders Manager
"""

from smart_holders_manager import SmartHoldersManager
from murf_holders_db import MURFHoldersDB

def test_smart_holders():
    print("Testing Smart Holders Manager...")
    print("=" * 50)
    
    try:
        # Initialize manager
        manager = SmartHoldersManager()
        print("[OK] Smart Holders Manager initialized")
        
        # Test database connection
        holders_db = MURFHoldersDB()
        print("[OK] Holders database connected")
        
        # Test OTC participants extraction
        print("\n[INFO] Extracting OTC participants...")
        otc_participants = manager.extract_otc_participants()
        print(f"[OK] Found {len(otc_participants)} OTC participants")
        
        # Test holders update from OTC
        print("\n[INFO] Updating holders from OTC...")
        new_holders_count = manager.update_holders_from_otc()
        print(f"[OK] Added {new_holders_count} new holders")
        
        # Test current holders data
        print("\n[INFO] Getting current holders data...")
        top_holders, holder_stats = manager.get_holders_data()
        
        if top_holders:
            print(f"[OK] Top holders: {len(top_holders)}")
            for i, holder in enumerate(top_holders[:5]):
                address = holder['address'][:20] if isinstance(holder, dict) else str(holder[0])[:20]
                balance = holder['current_balance'] if isinstance(holder, dict) else holder[2]
                print(f"  {i+1}. {address}... - {balance:,} MURF")
        else:
            print("[WARN] No holders found")
            
        if holder_stats:
            print(f"[OK] Holder statistics: {holder_stats}")
        else:
            print("[WARN] No holder statistics")
            
        # Test refresh
        print("\n[INFO] Testing full refresh...")
        active_holders = manager.refresh_holders_data()
        print(f"[OK] Active holders after refresh: {active_holders}")
        
        print("\n[SUCCESS] All tests completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smart_holders()
