#!/usr/bin/env python3
"""
Debug Live Dashboard - Cek kenapa exchange rate belum berubah
"""

import requests
import json
import re

def check_dashboard_data():
    """Check live dashboard data"""
    print("🔍 Debugging Live Dashboard")
    print("=" * 40)
    
    url = "https://web-production-ed260.up.railway.app"
    
    try:
        print(f"🌐 Fetching: {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Dashboard is LIVE!")
            
            # Cek apakah ada hardcoded exchange rate
            if "250,000" in response.text:
                print("❌ HARDCODED exchange rate (250,000) still present!")
                
                # Cari semua exchange rate di HTML
                exchange_rates = re.findall(r'(\d{1,3}(?:,\d{3})*)\s*MURF', response.text)
                print(f"📊 Exchange rates found: {exchange_rates}")
                
                # Cek apakah ada data OTC
                if "OTC" in response.text:
                    print("✅ OTC data present")
                else:
                    print("❌ OTC data missing")
                    
                # Cek apakah ada data real-time
                if "KTA Price" in response.text:
                    print("✅ KTA Price data present")
                else:
                    print("❌ KTA Price data missing")
                    
            else:
                print("✅ No hardcoded exchange rate found!")
                
            # Cek apakah ada data MURF
            if "MURF" in response.text:
                print("✅ MURF data present")
            else:
                print("❌ MURF data missing")
                
            # Cek response length
            print(f"📏 Response length: {len(response.text)} characters")
            
        else:
            print(f"❌ Dashboard error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_api_endpoint():
    """Check API endpoint for data"""
    print("\n🔍 Checking API Endpoint")
    print("=" * 40)
    
    try:
        # Cek apakah ada API endpoint
        api_url = "https://web-production-ed260.up.railway.app/api/data"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ API endpoint found!")
            data = response.json()
            print(f"📊 API data keys: {list(data.keys())}")
            
            if 'exchange_rate_murf' in data:
                rate = data['exchange_rate_murf']
                print(f"🎯 Exchange rate from API: {rate:,.0f} MURF")
                
                if rate == 250000:
                    print("❌ API still returning hardcoded rate!")
                else:
                    print("✅ API returning dynamic rate!")
            else:
                print("❌ Exchange rate not found in API")
                
        else:
            print(f"❌ API endpoint error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API check error: {e}")

def main():
    print("🚀 Live Dashboard Debugger")
    print("=" * 50)
    
    check_dashboard_data()
    check_api_endpoint()
    
    print("\n🔧 Possible Issues:")
    print("1. Railway belum deploy fix yang benar")
    print("2. Database kosong - fallback ke hardcode")
    print("3. OTC data tidak ditemukan")
    print("4. Logic error dalam kode")

if __name__ == "__main__":
    main()
