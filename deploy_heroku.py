#!/usr/bin/env python3
"""
Heroku Deploy Script untuk MURF Dashboard
"""

import os
import subprocess
import sys

def check_heroku_cli():
    """Check if Heroku CLI is installed"""
    try:
        result = subprocess.run(['heroku', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Heroku CLI sudah terinstall")
            return True
        else:
            print("❌ Heroku CLI belum terinstall")
            return False
    except FileNotFoundError:
        print("❌ Heroku CLI belum terinstall")
        return False

def install_heroku_cli():
    """Install Heroku CLI"""
    print("📦 Installing Heroku CLI...")
    print("Please install manually from: https://devcenter.heroku.com/articles/heroku-cli")
    return False

def create_heroku_app():
    """Create Heroku app"""
    print("📱 Creating Heroku app...")
    try:
        result = subprocess.run(['heroku', 'create', 'murf-dashboard'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Heroku app created")
            return True
        else:
            print(f"❌ Failed to create app: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def deploy_to_heroku():
    """Deploy to Heroku"""
    print("🚀 Deploying to Heroku...")
    
    try:
        # Check if git is initialized
        if not os.path.exists('.git'):
            print("📁 Initializing git repository...")
            subprocess.run(['git', 'init'], check=True)
        
        # Add all files
        print("📦 Adding files to git...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit
        print("💾 Committing changes...")
        subprocess.run(['git', 'commit', '-m', 'Deploy MURF Dashboard'], check=True)
        
        # Add Heroku remote
        print("🔗 Adding Heroku remote...")
        subprocess.run(['heroku', 'git:remote', '-a', 'murf-dashboard'], check=True)
        
        # Deploy
        print("🚀 Deploying to Heroku...")
        subprocess.run(['git', 'push', 'heroku', 'main'], check=True)
        
        # Open app
        print("🌐 Opening app...")
        subprocess.run(['heroku', 'open'], check=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deploy failed: {e}")
        return False

def main():
    print("🚀 MURF Dashboard Heroku Deploy")
    print("=" * 40)
    
    # Check Heroku CLI
    if not check_heroku_cli():
        print("\n📋 Install Heroku CLI first:")
        print("1. Download from: https://devcenter.heroku.com/articles/heroku-cli")
        print("2. Install and restart terminal")
        print("3. Run: heroku login")
        return
    
    # Create app
    if not create_heroku_app():
        print("❌ Failed to create Heroku app")
        return
    
    # Deploy
    if deploy_to_heroku():
        print(f"\n🎉 Dashboard berhasil di-deploy!")
        print(f"🌐 Akses di: https://murf-dashboard.herokuapp.com")
        print("\n📊 Features:")
        print("• Live KTA price dari CoinGecko")
        print("• Real-time MURF data dari Keeta API")
        print("• Type 7 OTC transaction monitoring")
        print("• Price history chart")
        print("• Donation section")
    else:
        print("\n❌ Deploy gagal. Coba manual:")
        print("1. heroku login")
        print("2. heroku create murf-dashboard")
        print("3. git add .")
        print("4. git commit -m 'Deploy'")
        print("5. git push heroku main")

if __name__ == "__main__":
    main()
