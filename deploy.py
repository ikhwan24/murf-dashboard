#!/usr/bin/env python3
"""
MURF Dashboard Deploy Script
Pilih platform untuk deploy dashboard ke public
"""

import os
import sys

def show_menu():
    """Show deployment options"""
    print("🚀 MURF Dashboard Deploy Options")
    print("=" * 50)
    print("1. Railway (Recommended - Free & Easy)")
    print("2. Heroku (Popular - Free tier limited)")
    print("3. Vercel (Static - Need modification)")
    print("4. DigitalOcean (Paid - More control)")
    print("5. Manual Deploy Instructions")
    print("0. Exit")
    print("=" * 50)

def railway_deploy():
    """Deploy to Railway"""
    print("\n🚀 Deploying to Railway...")
    print("Railway adalah platform yang mudah dan gratis!")
    
    print("\n📋 Langkah-langkah:")
    print("1. Buka https://railway.app")
    print("2. Sign up dengan GitHub")
    print("3. Click 'New Project'")
    print("4. Pilih 'Deploy from GitHub repo'")
    print("5. Pilih repository ini")
    print("6. Railway akan otomatis deploy!")
    
    print("\n✅ File yang sudah disiapkan:")
    print("• requirements.txt - Dependencies")
    print("• Procfile - Start command")
    print("• railway.json - Railway config")
    print("• Dashboard sudah production-ready")
    
    print("\n🌐 Setelah deploy, dashboard akan tersedia di URL Railway")

def heroku_deploy():
    """Deploy to Heroku"""
    print("\n🚀 Deploying to Heroku...")
    print("Heroku adalah platform populer untuk Python apps!")
    
    print("\n📋 Langkah-langkah:")
    print("1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli")
    print("2. Run: heroku login")
    print("3. Run: heroku create murf-dashboard")
    print("4. Run: git add .")
    print("5. Run: git commit -m 'Deploy'")
    print("6. Run: git push heroku main")
    
    print("\n✅ File yang sudah disiapkan:")
    print("• requirements.txt - Dependencies")
    print("• Procfile - Start command")
    print("• Dashboard sudah production-ready")
    
    print("\n🌐 Setelah deploy, dashboard akan tersedia di https://murf-dashboard.herokuapp.com")

def vercel_deploy():
    """Deploy to Vercel (Static)"""
    print("\n🚀 Deploying to Vercel...")
    print("Vercel bagus untuk static sites, tapi perlu modifikasi untuk Python!")
    
    print("\n⚠️  Catatan: Vercel tidak support Python server langsung")
    print("Perlu convert ke static site atau gunakan Vercel Functions")
    
    print("\n📋 Alternative untuk Vercel:")
    print("1. Convert dashboard ke static HTML/JS")
    print("2. Gunakan Vercel Functions untuk API calls")
    print("3. Atau pilih Railway/Heroku yang lebih mudah")

def digitalocean_deploy():
    """Deploy to DigitalOcean"""
    print("\n🚀 Deploying to DigitalOcean...")
    print("DigitalOcean App Platform memberikan kontrol lebih!")
    
    print("\n📋 Langkah-langkah:")
    print("1. Buka https://cloud.digitalocean.com")
    print("2. Sign up dan buat account")
    print("3. Go to 'Apps' section")
    print("4. Click 'Create App'")
    print("5. Connect GitHub repository")
    print("6. Configure build settings")
    print("7. Deploy!")
    
    print("\n💰 DigitalOcean App Platform: $5/month minimum")
    print("✅ Lebih stabil dan reliable untuk production")

def manual_instructions():
    """Show manual deploy instructions"""
    print("\n📋 Manual Deploy Instructions")
    print("=" * 50)
    
    print("\n🔧 Prerequisites:")
    print("• Python 3.8+")
    print("• Git")
    print("• Platform account (Railway/Heroku/etc)")
    
    print("\n📁 Files yang sudah disiapkan:")
    print("• real_live_dashboard.py - Main dashboard")
    print("• requirements.txt - Python dependencies")
    print("• Procfile - Start command")
    print("• railway.json - Railway config")
    print("• DEPLOY.md - Detailed instructions")
    
    print("\n🚀 Production Features:")
    print("• Dynamic port binding (PORT env var)")
    print("• 0.0.0.0 binding untuk external access")
    print("• Error handling")
    print("• Auto-refresh data")
    print("• CORS headers")
    
    print("\n📊 Dashboard Features:")
    print("• Live KTA price dari CoinGecko")
    print("• Real-time MURF data dari Keeta API")
    print("• Type 7 OTC transaction monitoring")
    print("• Price history chart")
    print("• Donation section")
    print("• Auto-refresh setiap 30 detik")

def main():
    while True:
        show_menu()
        choice = input("\nPilih opsi (0-5): ").strip()
        
        if choice == "1":
            railway_deploy()
        elif choice == "2":
            heroku_deploy()
        elif choice == "3":
            vercel_deploy()
        elif choice == "4":
            digitalocean_deploy()
        elif choice == "5":
            manual_instructions()
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Pilihan tidak valid!")
        
        input("\nPress Enter to continue...")
        print("\n" + "="*50)

if __name__ == "__main__":
    main()
