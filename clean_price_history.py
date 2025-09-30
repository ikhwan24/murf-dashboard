#!/usr/bin/env python3

import sqlite3

def clean_price_history():
    """Clean all price history data from database"""
    conn = sqlite3.connect('price_history.db')
    cursor = conn.cursor()
    
    try:
        # Clear all price history data
        cursor.execute('DELETE FROM price_history')
        conn.commit()
        print("[OK] All price history data cleared from database")
        
        # Verify database is empty
        cursor.execute('SELECT COUNT(*) FROM price_history')
        count = cursor.fetchone()[0]
        print(f"[VERIFY] Database now has {count} price history records")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clean_price_history()
