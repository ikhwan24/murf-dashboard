#!/usr/bin/env python3
"""
Trigger Railway Deployment
- Force push to trigger Railway auto-deploy
- Check deployment status
"""

import subprocess
import time
from datetime import datetime

def trigger_deployment():
    print("Railway Deployment Trigger")
    print("=" * 50)
    
    try:
        # Get current commit
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True)
        current_commit = result.stdout.strip()[:8]
        print(f"Current Commit: {current_commit}")
        
        # Get current time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Trigger Time: {timestamp}")
        
        # Create empty commit to trigger deployment
        commit_message = f"Trigger Railway deployment - {timestamp}"
        
        print(f"\n[INFO] Creating trigger commit...")
        subprocess.run(['git', 'commit', '--allow-empty', '-m', commit_message], 
                      check=True)
        
        print(f"[INFO] Pushing to GitHub...")
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print(f"\n[SUCCESS] Deployment trigger sent to Railway!")
        print(f"[INFO] Railway should start deployment within 1-2 minutes")
        print(f"[INFO] Check your Railway dashboard for deployment status")
        
        # Show recent commits
        print(f"\n[INFO] Recent commits:")
        subprocess.run(['git', 'log', '--oneline', '-3'])
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git command failed: {e}")
    except Exception as e:
        print(f"[ERROR] Deployment trigger failed: {e}")

def check_railway_status():
    print(f"\n" + "=" * 50)
    print("Railway Deployment Checklist:")
    print("=" * 50)
    print("1. ✅ Check Railway Dashboard:")
    print("   - Go to https://railway.app/dashboard")
    print("   - Select your MURF dashboard project")
    print("   - Check 'Deployments' tab")
    
    print(f"\n2. ✅ Verify GitHub Connection:")
    print("   - Settings > Source > GitHub Repository")
    print("   - Should show: ikhwan24/murf-dashboard")
    print("   - Branch: main")
    
    print(f"\n3. ✅ Manual Deploy (if needed):")
    print("   - Press CMD+K (or Ctrl+K)")
    print("   - Type 'Deploy Latest Commit'")
    print("   - Press Enter")
    
    print(f"\n4. ✅ Check Deployment Logs:")
    print("   - Click on latest deployment")
    print("   - View build and deploy logs")
    print("   - Look for errors or success messages")

if __name__ == "__main__":
    trigger_deployment()
    check_railway_status()
