#!/usr/bin/env python3
"""
MURF Dashboard Runner
Script untuk menjalankan dashboard MURF Token
"""

import sys
import os
from dashboard import MURFDashboard
from web_dashboard import app

def main():
    """Main function untuk menjalankan dashboard"""
    print("🚀 MURF Token Dashboard")
    print("=" * 50)
    print("Choose dashboard type:")
    print("1. Desktop Dashboard (matplotlib)")
    print("2. Web Dashboard (Flask)")
    print("3. Console Statistics")
    print()
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            print("📊 Starting Desktop Dashboard...")
            dashboard = MURFDashboard()
            dashboard.create_dashboard()
            
        elif choice == "2":
            print("🌐 Starting Web Dashboard...")
            print("📊 Dashboard will be available at: http://localhost:5000")
            print("🔄 Auto-refresh every 30 seconds")
            print("Press Ctrl+C to stop")
            app.run(debug=True, host='0.0.0.0', port=5000)
            
        elif choice == "3":
            print("📊 Console Statistics:")
            print()
            dashboard = MURFDashboard()
            dashboard.print_statistics()
            
        else:
            print("❌ Invalid choice. Please run again and select 1, 2, or 3.")
            
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
