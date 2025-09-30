#!/usr/bin/env python3

import sqlite3

def clean_fake_data():
    """Clean all fake OTC data from database"""
    conn = sqlite3.connect('otc_transactions.db')
    cursor = conn.cursor()
    
    try:
        # Clear all fake data
        cursor.execute('DELETE FROM otc_transactions')
        conn.commit()
        print("[OK] All fake OTC data cleared from database")
        
        # Verify database is empty
        cursor.execute('SELECT COUNT(*) FROM otc_transactions')
        count = cursor.fetchone()[0]
        print(f"[VERIFY] Database now has {count} OTC transactions")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clean_fake_data()
