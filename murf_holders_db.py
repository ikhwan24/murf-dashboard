#!/usr/bin/env python3
"""
MURF Holders Database - Store and manage MURF token holders data
"""

import sqlite3
import json
from datetime import datetime

class MURFHoldersDB:
    def __init__(self, db_path="murf_holders.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for MURF holders"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS murf_holders (
                address TEXT PRIMARY KEY,
                total_received INTEGER,
                total_sent INTEGER,
                current_balance INTEGER,
                tx_count INTEGER,
                first_tx_date TEXT,
                last_tx_date TEXT,
                rank INTEGER,
                is_airdrop_recipient BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holder_statistics (
                id INTEGER PRIMARY KEY,
                total_holders INTEGER,
                total_murf_circulation INTEGER,
                total_airdropped INTEGER,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"MURF holders database initialized: {self.db_path}")
    
    def save_holders_data(self, holders_data, statistics):
        """Save holders data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM murf_holders')
        cursor.execute('DELETE FROM holder_statistics')
        
        # Save holders with ranking
        sorted_holders = sorted(holders_data.items(), 
                              key=lambda x: x[1]['received'], 
                              reverse=True)
        
        for rank, (address, data) in enumerate(sorted_holders, 1):
            current_balance = data['received'] - data['sent']
            is_airdrop_recipient = data['received'] > 0
            
            cursor.execute('''
                INSERT OR REPLACE INTO murf_holders 
                (address, total_received, total_sent, current_balance, tx_count, 
                 first_tx_date, last_tx_date, rank, is_airdrop_recipient)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (address, data['received'], data['sent'], current_balance, 
                  data['tx_count'], data['first_tx'], data['last_tx'], 
                  rank, is_airdrop_recipient))
        
        # Save statistics
        cursor.execute('''
            INSERT INTO holder_statistics 
            (total_holders, total_murf_circulation, total_airdropped, last_updated)
            VALUES (?, ?, ?, ?)
        ''', (statistics['total_holders'], statistics['total_circulation'], 
              statistics['total_airdropped'], statistics['last_updated']))
        
        conn.commit()
        conn.close()
        print(f"Saved {len(holders_data)} holders to database")
    
    def get_top_holders(self, limit=20):
        """Get top MURF holders"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT address, total_received, current_balance, tx_count, rank
            FROM murf_holders 
            ORDER BY current_balance DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        holders = []
        for row in results:
            holders.append({
                'address': row[0],
                'total_received': row[1],
                'current_balance': row[2],
                'tx_count': row[3],
                'rank': row[4]
            })
        
        return holders
    
    def get_holder_statistics(self):
        """Get holder statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Calculate statistics from murf_holders table
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_holders,
                    SUM(current_balance) as total_circulation,
                    COUNT(CASE WHEN is_airdrop_recipient = 1 THEN 1 END) as total_airdropped
                FROM murf_holders 
                WHERE current_balance > 0
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'total_holders': result[0] or 0,
                    'total_circulation': result[1] or 0,
                    'total_airdropped': result[2] or 0,
                    'last_updated': datetime.now().isoformat()
                }
            else:
                return {
                    'total_holders': 0,
                    'total_circulation': 0,
                    'total_airdropped': 0,
                    'last_updated': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error getting holder statistics: {e}")
            return {
                'total_holders': 0,
                'total_circulation': 0,
                'total_airdropped': 0,
                'last_updated': datetime.now().isoformat()
            }
    
    def get_holder_by_address(self, address):
        """Get specific holder by address"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT address, total_received, total_sent, current_balance, 
                   tx_count, first_tx_date, last_tx_date, rank
            FROM murf_holders 
            WHERE address = ?
        ''', (address,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'address': result[0],
                'total_received': result[1],
                'total_sent': result[2],
                'current_balance': result[3],
                'tx_count': result[4],
                'first_tx_date': result[5],
                'last_tx_date': result[6],
                'rank': result[7]
            }
        return None
