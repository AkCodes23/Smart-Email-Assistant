"""
Google Gmail API integration module for Smart Email Assistant
Built with Google Agent Dev Kit framework patterns
"""
import base64
import os
import pickle
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    # Use importlib to handle the problematic import
    import importlib

    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    oauth_flow = importlib.import_module('google_auth_oauthlib.flow')
    InstalledAppFlow = oauth_flow.InstalledAppFlow
except ImportError as e:
    print(f"⚠️ Google API libraries not found: {e}")
    print("Please install: pip install google-auth google-auth-oauthlib google-api-python-client")
    raise


class GmailAgent:
    """Gmail API integration agent using Google Agent Dev Kit patterns"""
    
    def __init__(self, scopes: List[str]):
        self.scopes = scopes
        self.service = None
        self.authenticate()
    
    def authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth2"""
        creds = None
        
        # Check if token.pickle exists (previous authentication)
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "credentials.json not found. Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes
                )
                
                # Smart authentication with multiple automatic methods
                print("🔐 Starting smart Gmail authentication...")
                
                # Try multiple ports automatically with random port fallback
                ports_to_try = [8080, 8090, 9090, 8000, 8888, 0]  # 0 = random port
                success = False
                
                for i, port in enumerate(ports_to_try, 1):
                    try:
                        port_desc = f"port {port}" if port != 0 else "random available port"
                        print(f"🌐 Method {i}: Trying {port_desc}...")
                        
                        creds = flow.run_local_server(
                            port=port,
                            open_browser=True,
                            success_message='🎉 Gmail authentication successful! You can close this tab.',
                            bind_addr='127.0.0.1'
                        )
                        print(f"✅ Success! Authenticated via browser on {port_desc}")
                        success = True
                        break
                        
                    except Exception as e:
                        error_msg = str(e)[:50]
                        print(f"   ⚠️ Failed: {error_msg}...")
                        continue
                
                # If all ports failed, try console authentication
                if not success:
                    try:
                        print("🖥️ Trying console-based authentication...")
                        creds = flow.run_console()
                        print("✅ Console authentication successful!")
                        success = True
                    except Exception as e:
                        print(f"   ⚠️ Console failed: {str(e)[:50]}...")
                
                # If console failed, try headless
                if not success:
                    try:
                        print("🤖 Trying headless authentication...")
                        creds = flow.run_local_server(
                            port=8080,
                            open_browser=False,
                            bind_addr='127.0.0.1'
                        )
                        print("✅ Headless authentication successful!")
                        success = True
                    except Exception as e:
                        print(f"   ⚠️ Headless failed: {str(e)[:50]}...")
                
                # Final fallback: Enhanced manual
                if not success:
                    import webbrowser
                    
                    print("📱 Using enhanced manual authentication...")
                    print("🔧 One-time setup (future runs will be automatic)")
                    
                    # Set redirect URI for out-of-band authentication  
                    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                    
                    auth_url, _ = flow.authorization_url(
                        access_type='offline',
                        include_granted_scopes='true',
                        prompt='consent'
                    )
                    
                    print(f"\n🌐 Opening browser automatically...")
                    try:
                        webbrowser.open(auth_url)
                        print("✅ Browser opened! Grant permissions and copy the code shown.")
                    except Exception:
                        print(f"⚠️ Could not open browser. Please visit: {auth_url}")
                    
                    # Get authorization code
                    while True:
                        auth_code = input("\n🔑 Paste authorization code: ").strip()
                        if auth_code:
                            break
                        print("❌ Please enter the authorization code.")
                    
                    try:
                        flow.fetch_token(code=auth_code)
                        creds = flow.credentials
                        print("✅ Manual authentication successful!")
                    except Exception as manual_error:
                        print(f"❌ Manual authentication failed: {manual_error}")
                        raise
                try:
                    print("🌐 Attempting browser-based authentication...")
                    creds = flow.run_local_server(
                        port=8080,
                        open_browser=True,
                        success_message='Authentication successful! You can close this window.',
                        bind_addr='127.0.0.1'
                    )
                    print("✅ Browser authentication successful!")
                    
                except Exception as browser_error:
                    print(f"⚠️ Browser authentication failed: {str(browser_error)}")
                    
                    # Second try: Alternative port
                    try:
                        print("🔄 Trying alternative port...")
                        creds = flow.run_local_server(
                            port=8090,
                            open_browser=True,
                            success_message='Authentication successful! You can close this window.',
                            bind_addr='127.0.0.1'
                        )
                        print("✅ Alternative port authentication successful!")
                        
                    except Exception as alt_port_error:
                        print(f"⚠️ Alternative port failed: {str(alt_port_error)}")
                        
                        # Final fallback: Manual authorization code flow
                        print("\n" + "="*70)
                        print("� MANUAL AUTHENTICATION REQUIRED")
                        print("="*70)
                        print("Google Cloud Console redirect URI configuration needed.")
                        print("\n📋 Please follow these steps:")
                        print("1. Go to Google Cloud Console > APIs & Services > Credentials")
                        print("2. Edit your OAuth 2.0 Client ID")
                        print("3. Add these Authorized redirect URIs:")
                        print("   • http://localhost:8080/")
                        print("   • http://127.0.0.1:8080/")
                        print("   • http://localhost:8090/")
                        print("   • http://127.0.0.1:8090/")
                        print("4. Save the changes")
                        print("\n🌐 For now, we'll use manual authentication:")
                        print("="*70)
                        
                        # Generate authorization URL for manual flow
                        # Set redirect URI for out-of-band authentication
                        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                        
                        auth_url, _ = flow.authorization_url(
                            access_type='offline',
                            include_granted_scopes='true',
                            prompt='consent'
                        )
                        
                        print(f"\n🔗 STEP 1: Open this URL in your browser:")
                        print(f"{auth_url}")
                        print(f"\n📝 STEP 2: Complete authentication and copy the code")
                        print(f"📋 STEP 3: Paste the authorization code below")
                        print("-" * 70)
                        
                        # Get authorization code from user
                        while True:
                            auth_code = input("\n🔑 Enter the authorization code: ").strip()
                            if auth_code:
                                break
                            print("❌ Authorization code cannot be empty. Please try again.")
                        
                        try:
                            flow.fetch_token(code=auth_code)
                            creds = flow.credentials
                            print("✅ Manual authentication successful!")
                        except Exception as manual_error:
                            print(f"❌ Manual authentication failed: {manual_error}")
                            raise
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Successfully authenticated with Gmail API")
    
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
    
    def get_recent_emails(self, max_results: int = 50, days_back: int = 7) -> List[Dict[str, Any]]:
        """Fetch recent emails from inbox with optional date filtering"""
        try:
            # Build query for recent emails
            query_parts = []
            
            # Add date filter if specified
            if days_back > 0:
                since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
                query_parts.append(f'after:{since_date}')
            
            # Combine query parts
            query = ' '.join(query_parts) if query_parts else None
            
            # Get list of messages
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            print(f"📥 Found {len(messages)} messages to process...")
            
            for i, message in enumerate(messages, 1):
                if i % 10 == 0:  # Progress indicator
                    print(f"📧 Processing email {i}/{len(messages)}...")
                
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return []
    
    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extract header information
            sender = self._get_header_value(headers, 'From')
            subject = self._get_header_value(headers, 'Subject')
            date = self._get_header_value(headers, 'Date')
            message_id_header = self._get_header_value(headers, 'Message-ID')
            thread_id = message.get('threadId', '')
            
            # Extract body
            body = self._extract_body(message['payload'])
            
            # Parse timestamp
            timestamp = self._parse_timestamp(date)
            
            return {
                'id': message_id,
                'thread_id': thread_id,
                'sender': sender,
                'subject': subject,
                'body': body,
                'timestamp': timestamp,
                'message_id': message_id_header,
                'raw_date': date
            }
            
        except Exception as e:
            print(f"Error getting email details for {message_id}: {e}")
            return None
    
    def _get_header_value(self, headers: List[Dict], name: str) -> str:
        """Extract specific header value from email headers"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ""
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        try:
            # Handle different payload structures
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
                    elif part['mimeType'] == 'text/html' and not body:
                        data = part['body'].get('data', '')
                        if data:
                            html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                            # Simple HTML to text conversion
                            body = re.sub(r'<[^>]+>', '', html_body)
            else:
                # Single part message
                if payload['mimeType'] == 'text/plain':
                    data = payload['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                elif payload['mimeType'] == 'text/html':
                    data = payload['body'].get('data', '')
                    if data:
                        html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        body = re.sub(r'<[^>]+>', '', html_body)
            
            # Clean up the body
            body = body.strip()
            # Remove excessive whitespace
            body = re.sub(r'\n\s*\n', '\n\n', body)
            
        except Exception as e:
            print(f"Error extracting body: {e}")
            body = "[Error extracting email content]"
        
        return body
    
    def _parse_timestamp(self, date_str: str) -> datetime:
        """Parse email timestamp from various formats"""
        try:
            # Try parsing common email date formats
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            try:
                # Fallback parsing
                return datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
            except Exception:
                return datetime.now()
    
    def check_if_replied(self, thread_id: str, original_timestamp: datetime) -> bool:
        """Check if an email thread has been replied to by the user"""
        try:
            # Get all messages in the thread
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            messages = thread.get('messages', [])
            
            # If only one message in thread, definitely not replied
            if len(messages) <= 1:
                return False
            
            # Get user's email address
            profile = self.service.users().getProfile(userId='me').execute()
            user_email = profile.get('emailAddress', '').lower()
            
            # Check if any message after the original was sent by the user
            for message in messages:
                headers = message['payload'].get('headers', [])
                sender = self._get_header_value(headers, 'From').lower()
                date = self._get_header_value(headers, 'Date')
                
                # Skip if we can't parse the timestamp
                try:
                    msg_timestamp = self._parse_timestamp(date)
                except Exception:
                    continue
                
                # If message is from user and after original timestamp
                if (user_email in sender and 
                    msg_timestamp > original_timestamp):
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Error checking reply status for thread {thread_id}: {e}")
            return False
    
    def get_sent_emails(self, days_back: int = 30) -> List[str]:
        """Get list of sent email message IDs for reply checking"""
        try:
            # Calculate date for query
            since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['SENT'],
                q=f'after:{since_date}'
            ).execute()
            
            messages = results.get('messages', [])
            return [msg['id'] for msg in messages]
            
        except Exception as e:
            print(f"❌ Error fetching sent emails: {e}")
            return []
    
    def search_emails(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search emails with custom Gmail query"""
        try:
            print(f"🔍 Searching emails with query: {query}")
            
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            print(f"📧 Found {len(emails)} matching emails")
            return emails
            
        except Exception as e:
            print(f"❌ Error searching emails: {e}")
            return []
    
    def get_unread_emails(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get unread emails specifically"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            print(f"📬 Processing {len(messages)} unread emails...")
            
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching unread emails: {e}")
            return []
