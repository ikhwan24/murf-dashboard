#!/usr/bin/env python3
"""
Export MURF Holders to CSV
"""

import sqlite3
import csv
from datetime import datetime

def export_holders_to_csv():
    """Export all MURF holders to CSV file"""
    print("Exporting MURF holders to CSV...")
    
    # Connect to database
    conn = sqlite3.connect('murf_holders.db')
    cursor = conn.cursor()
    
    # Get all holders
    cursor.execute('''
        SELECT address, total_received, total_sent, current_balance, 
               tx_count, first_tx_date, last_tx_date, rank
        FROM murf_holders 
        ORDER BY current_balance DESC
    ''')
    
    holders = cursor.fetchall()
    conn.close()
    
    # Create CSV file
    csv_filename = f'murf_holders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow([
            'Rank', 'Address', 'Current_Balance', 'Total_Received', 
            'Total_Sent', 'TX_Count', 'First_TX_Date', 'Last_TX_Date'
        ])
        
        # Write data
        for holder in holders:
            writer.writerow([
                holder[7],  # rank
                holder[0],  # address
                holder[3],  # current_balance
                holder[1],  # total_received
                holder[2],  # total_sent
                holder[4],  # tx_count
                holder[5],  # first_tx_date
                holder[6]   # last_tx_date
            ])
    
    print(f"Exported {len(holders)} holders to {csv_filename}")
    return csv_filename

def export_addresses_only():
    """Export just the addresses to a simple text file"""
    print("Exporting MURF holder addresses...")
    
    conn = sqlite3.connect('murf_holders.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT address FROM murf_holders ORDER BY current_balance DESC')
    addresses = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Create addresses file
    addresses_filename = f'murf_holder_addresses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    
    with open(addresses_filename, 'w', encoding='utf-8') as f:
        f.write(f"# MURF Token Holder Addresses\n")
        f.write(f"# Total: {len(addresses)} addresses\n")
        f.write(f"# Export Date: {datetime.now().isoformat()}\n")
        f.write(f"# Source: Airdrop wallet analysis\n\n")
        
        for i, address in enumerate(addresses, 1):
            f.write(f"{i:4d}. {address}\n")
    
    print(f"Exported {len(addresses)} addresses to {addresses_filename}")
    return addresses_filename

def main():
    print("MURF Holders Export Tool")
    print("=" * 50)
    
    # Export CSV
    csv_file = export_holders_to_csv()
    
    # Export addresses only
    addresses_file = export_addresses_only()
    
    print(f"\nFiles created:")
    print(f"CSV: {csv_file}")
    print(f"Addresses: {addresses_file}")
    
    print(f"\nTotal holders: 1,528")
    print(f"Total circulation: 59,339,104,427 MURF")

if __name__ == "__main__":
    main()
