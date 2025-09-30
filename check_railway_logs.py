#!/usr/bin/env python3
"""
Check Railway Logs - Debug exchange rate issue
"""

import requests
import json

def check_railway_deployment():
    """Check if Railway deployment is working"""
    print("🔍 Checking Railway Deployment Status")
    print("=" * 40)
    
    # URL Railway dashboard Anda
    railway_url = "https://web-production-ed260.up.railway.app"
    
    try:
        print(f"🌐 Testing URL: {railway_url}")
        response = requests.get(railway_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Railway deployment is LIVE!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Length: {len(response.text)} characters")
            
            # Cek apakah ada data MURF di response
            if "MURF" in response.text:
                print("✅ MURF data found in response")
            else:
                print("❌ MURF data NOT found in response")
                
            # Cek apakah ada exchange rate
            if "250,000" in response.text:
                print("⚠️  Hardcoded exchange rate (250,000) still present")
            else:
                print("✅ No hardcoded exchange rate found")
                
            # Cek apakah ada data real-time
            if "KTA Price" in response.text:
                print("✅ KTA Price data found")
            else:
                print("❌ KTA Price data NOT found")
                
        else:
            print(f"❌ Railway deployment issue!")
            print(f"   Status Code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("   Possible issues:")
        print("   1. Railway still building")
        print("   2. Network connection issue")
        print("   3. Railway service down")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    print("🚀 Railway Deployment Checker")
    print("=" * 50)
    
    check_railway_deployment()
    
    print("\n🔧 Possible Solutions:")
    print("1. Wait 2-3 minutes for Railway to rebuild")
    print("2. Check Railway dashboard for build status")
    print("3. Force restart Railway service")
    print("4. Check Railway logs for errors")

if __name__ == "__main__":
    main()
