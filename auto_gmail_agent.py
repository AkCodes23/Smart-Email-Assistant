#!/usr/bin/env python3
"""
Auto-Bypass Gmail Agent - Handles OAuth automatically with multiple fallback methods
"""
import base64
import os
import pickle
import re
import webbrowser
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import importlib
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    oauth_flow = importlib.import_module('google_auth_oauthlib.flow')
    InstalledAppFlow = oauth_flow.InstalledAppFlow
except ImportError as e:
    print(f"⚠️ Google API libraries not found: {e}")
    print("Please install: pip install google-auth google-auth-oauthlib google-api-python-client")
    raise

class AutoGmailAgent:
    """Gmail Agent with automatic OAuth bypass methods"""
    
    def __init__(self, scopes: List[str]):
        self.scopes = scopes
        self.service = None
        self.authenticate()
    
    def authenticate(self) -> None:
        """Smart authentication with multiple automatic bypass methods"""
        creds = None
        
        # Check if token.pickle exists (previous authentication)
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired token...")
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "credentials.json not found. Please download it from Google Cloud Console."
                    )
                
                print("🔐 Starting smart Gmail authentication...")
                creds = self._smart_authenticate()
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail API connection established!")
    
    def _smart_authenticate(self):
        """Try multiple authentication methods automatically"""
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.scopes)
        
        # Method 1: Multiple port attempts with random port fallback
        print("🌐 Method 1: Trying browser authentication with multiple ports...")
        ports = [8080, 8090, 9090, 8000, 8888, 0]  # 0 = random available port
        
        for i, port in enumerate(ports, 1):
            try:
                port_desc = f"port {port}" if port != 0 else "random available port"
                print(f"   Attempt {i}/6: {port_desc}...")
                
                creds = flow.run_local_server(
                    port=port,
                    open_browser=True,
                    success_message='🎉 Gmail authentication successful! You can close this tab.',
                    bind_addr='127.0.0.1'
                )
                print(f"✅ Success! Authenticated via browser on {port_desc}")
                return creds
                
            except Exception as e:
                if "redirect_uri_mismatch" in str(e):
                    print(f"   ⚠️ Redirect URI mismatch on {port_desc}")
                elif "port" in str(e).lower() or "address" in str(e).lower():
                    print(f"   ⚠️ Port {port} unavailable")
                else:
                    print(f"   ⚠️ Failed: {str(e)[:30]}...")
                continue
        
        # Method 2: Console-based authentication (newer google-auth-oauthlib versions)
        print("\n🖥️ Method 2: Trying console-based authentication...")
        try:
            creds = flow.run_console()
            print("✅ Success! Console authentication worked")
            return creds
        except Exception as e:
            print(f"   ⚠️ Console method failed: {str(e)[:50]}...")
        
        # Method 3: Headless authentication (no browser opening)
        print("\n🤖 Method 3: Trying headless authentication...")
        try:
            creds = flow.run_local_server(
                port=8080,
                open_browser=False,
                bind_addr='127.0.0.1'
            )
            print("✅ Success! Headless authentication worked")
            return creds
        except Exception as e:
            print(f"   ⚠️ Headless method failed: {str(e)[:50]}...")
        
        # Method 4: Enhanced manual authentication with better UX
        print("\n📱 Method 4: Smart manual authentication...")
        return self._enhanced_manual_auth(flow)
    
    def _enhanced_manual_auth(self, flow):
        """Enhanced manual authentication with improved user experience"""
        print("🔧 Using one-time manual setup (future runs will be automatic)")
        
        # Set out-of-band redirect URI
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        # Generate auth URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        print("\n" + "="*60)
        print("🌐 AUTOMATIC BROWSER OPENING...")
        print("="*60)
        
        # Try to open browser automatically
        try:
            webbrowser.open(auth_url)
            print("✅ Browser opened automatically!")
            print("📋 After granting permissions, copy the authorization code shown")
        except Exception:
            print("⚠️ Could not open browser automatically")
            print(f"🔗 Please manually open: {auth_url}")
        
        print("="*60)
        
        # Get authorization code with better prompts
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            try:
                auth_code = input("\n🔑 Paste the authorization code here: ").strip()
                
                if not auth_code:
                    print("❌ Empty code. Please try again.")
                    attempts += 1
                    continue
                
                if len(auth_code) < 20:
                    print("❌ Code seems too short. Please copy the complete code.")
                    attempts += 1
                    continue
                
                print("🔄 Validating authorization code...")
                flow.fetch_token(code=auth_code)
                print("✅ Authorization successful!")
                return flow.credentials
                
            except Exception as e:
                attempts += 1
                if attempts < max_attempts:
                    print(f"❌ Code validation failed: {str(e)[:50]}...")
                    print(f"💡 Please try again ({attempts}/{max_attempts})")
                else:
                    print(f"❌ All attempts failed. Please check your code: {e}")
                    raise
        
        raise Exception("Manual authentication failed after maximum attempts")
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get user's Gmail profile information"""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return {
                'email': profile.get('emailAddress', ''),
                'messages_total': profile.get('messagesTotal', 0),
                'threads_total': profile.get('threadsTotal', 0)
            }
        except Exception as e:
            print(f"❌ Error getting user profile: {e}")
            return {'email': '', 'messages_total': 0, 'threads_total': 0}
    
    def get_recent_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent emails (simplified for testing)"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            print(f"📥 Processing {len(messages)} recent emails...")
            
            for message in messages[:max_results]:  # Limit processing
                try:
                    msg = self.service.users().messages().get(
                        userId='me', 
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    headers = msg['payload'].get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    date_header = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                    
                    # Get email body
                    body = self._extract_email_body(msg['payload'])
                    
                    # Get timestamp
                    timestamp = int(msg.get('internalDate', 0)) / 1000
                    
                    emails.append({
                        'id': message['id'],
                        'thread_id': msg.get('threadId', ''),
                        'subject': subject,
                        'sender': sender,
                        'date': date_header,
                        'body': body,
                        'timestamp': timestamp,
                        'snippet': msg.get('snippet', '')
                    })
                except Exception as e:
                    print(f"⚠️ Error processing message {message['id']}: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return []
    
    def _extract_email_body(self, payload):
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        import base64
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data and not body:  # Use HTML only if no plain text
                        import base64
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            # Single part message
            if payload['mimeType'] in ['text/plain', 'text/html']:
                data = payload['body'].get('data', '')
                if data:
                    import base64
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body[:1000]  # Limit body length
    
    def check_if_replied(self, thread_id: str, original_timestamp: float) -> bool:
        """
        Check if an email thread has been replied to
        
        Args:
            thread_id: Gmail thread ID
            original_timestamp: Timestamp of the original email
            
        Returns:
            bool: True if thread has been replied to, False otherwise
        """
        try:
            # Get the thread
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            messages = thread.get('messages', [])
            
            # If thread has more than 1 message, check if there are replies after the original
            if len(messages) <= 1:
                return False
            
            # Check if any message in the thread is from the user (indicating a reply)
            user_profile = self.get_user_profile()
            user_email = user_profile.get('email', '').lower()
            
            for msg in messages:
                headers = msg['payload'].get('headers', [])
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                msg_timestamp = int(msg.get('internalDate', 0)) / 1000
                
                # If message is from user and after original timestamp, it's a reply
                if (user_email in sender.lower() and 
                    msg_timestamp > original_timestamp):
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking reply status for thread {thread_id}: {e}")
            return False

# Test function
def test_auto_auth():
    """Test the automatic authentication"""
    print("🧪 Testing Auto-Bypass Gmail Authentication")
    print("=" * 50)
    
    try:
        scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        agent = AutoGmailAgent(scopes)
        
        # Test profile access
        profile = agent.get_user_profile()
        if profile['email']:
            print(f"🎉 SUCCESS! Connected to: {profile['email']}")
            
            # Test email access
            emails = agent.get_recent_emails(5)
            print(f"📧 Accessed {len(emails)} recent emails")
            
            for i, email in enumerate(emails[:3], 1):
                print(f"   {i}. {email['subject'][:50]}...")
            
            return True
        else:
            print("❌ Could not get user profile")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_auto_auth()
