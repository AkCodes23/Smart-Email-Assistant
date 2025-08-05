#!/usr/bin/env python3
"""
Quick OAuth Test - Tests the fixed authentication
"""
import os
from gmail_agent import GmailAgent

def quick_test():
    """Quick test of the fixed OAuth authentication"""
    print("🧪 Testing Fixed OAuth Authentication")
    print("=" * 50)
    
    # Delete old token to force fresh authentication
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')
        print("🗑️ Removed old authentication token")
    
    try:
        # Test with Gmail read-only scope
        scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        print("📧 Initializing Gmail agent...")
        
        agent = GmailAgent(scopes)
        
        # Test basic functionality
        profile = agent.get_user_profile()
        
        if profile['email']:
            print(f"✅ SUCCESS! Authenticated as: {profile['email']}")
            print(f"📊 Total messages: {profile['messages_total']}")
            print(f"🧵 Total threads: {profile['threads_total']}")
            
            # Test fetching a few emails
            print("\n📥 Testing email access...")
            emails = agent.get_recent_emails(max_results=3, days_back=7)
            print(f"✅ Successfully accessed {len(emails)} recent emails")
            
            return True
        else:
            print("❌ Authentication succeeded but couldn't get user profile")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    
    if success:
        print("\n🎉 OAuth authentication is working correctly!")
        print("📋 You can now run: python main.py")
    else:
        print("\n⚠️ OAuth authentication needs troubleshooting.")
        print("📋 Try running: python oauth_checker.py for diagnosis")
