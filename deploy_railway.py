#!/usr/bin/env python3
"""
Railway Deploy Script untuk MURF Dashboard
"""

import os
import subprocess
import sys

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI sudah terinstall")
            return True
        else:
            print("❌ Railway CLI belum terinstall")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI belum terinstall")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("📦 Installing Railway CLI...")
    try:
        # Try npm first
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed via npm")
        return True
    except subprocess.CalledProcessError:
        try:
            # Try with npx
            subprocess.run(['npx', '@railway/cli', '--version'], check=True)
            print("✅ Railway CLI available via npx")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Railway CLI")
            return False

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    
    try:
        # Login to Railway
        print("🔐 Logging in to Railway...")
        subprocess.run(['railway', 'login'], check=True)
        
        # Initialize project
        print("📁 Initializing Railway project...")
        subprocess.run(['railway', 'init'], check=True)
        
        # Deploy
        print("🚀 Deploying...")
        subprocess.run(['railway', 'up'], check=True)
        
        # Get URL
        print("🔗 Getting deployment URL...")
        result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"✅ Dashboard deployed successfully!")
            print(f"🌐 URL: {url}")
            return url
        else:
            print("✅ Deployed but couldn't get URL")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Deploy failed: {e}")
        return None

def main():
    print("🚀 MURF Dashboard Railway Deploy")
    print("=" * 40)
    
    # Check Railway CLI
    if not check_railway_cli():
        if not install_railway_cli():
            print("\n📋 Manual installation:")
            print("1. Install Node.js: https://nodejs.org")
            print("2. Run: npm install -g @railway/cli")
            print("3. Run: railway login")
            print("4. Run: railway init")
            print("5. Run: railway up")
            return
    
    # Deploy
    url = deploy_to_railway()
    
    if url:
        print(f"\n🎉 Dashboard berhasil di-deploy!")
        print(f"🌐 Akses di: {url}")
        print("\n📊 Features:")
        print("• Live KTA price dari CoinGecko")
        print("• Real-time MURF data dari Keeta API")
        print("• Type 7 OTC transaction monitoring")
        print("• Price history chart")
        print("• Donation section")
    else:
        print("\n❌ Deploy gagal. Coba manual:")
        print("1. railway login")
        print("2. railway init")
        print("3. railway up")

if __name__ == "__main__":
    main()
