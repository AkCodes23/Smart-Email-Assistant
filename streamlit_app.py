"""
Streamlit Web UI for Smart Email Assistant
Built with Google Agent Dev Kit Framework
"""
import asyncio
import os
import sys
import threading
import time
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv

from ai_agent import EmailAIAgent
from data_processor import DataProcessor
from free_ai_agent import FreeAIAgent

# Import Gmail agents
try:
    from auto_gmail_agent import AutoGmailAgent as GmailAgent
    gmail_mode = "🚀 Automatic OAuth Bypass"
except ImportError:
    from gmail_agent import GmailAgent
    gmail_mode = "📧 Standard Gmail Agent"

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Smart Email Assistant",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    
    .email-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitEmailAssistant:
    """Streamlit Web UI for Smart Email Assistant"""
    
    def __init__(self):
        self.gmail_agent = None
        self.ai_agent = None
        self.data_processor = DataProcessor()
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send'
        ]
    
    def show_header(self):
        """Display main header"""
        st.markdown('<h1 class="main-header">📧 Smart Email Assistant</h1>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">Built with Google Agent Dev Kit Framework | {gmail_mode}</div>', unsafe_allow_html=True)
    
    def show_sidebar_config(self):
        """Show configuration options in sidebar"""
        st.sidebar.header("⚙️ Configuration")
        
        # Email settings
        st.sidebar.subheader("📧 Email Settings")
        max_emails = st.sidebar.slider("Number of emails to analyze", 1, 50, 10)
        check_replies = st.sidebar.checkbox("Check reply status (slower but accurate)", value=True)
        generate_drafts = st.sidebar.checkbox("Generate reply drafts", value=True)
        
        # AI Service selection
        st.sidebar.subheader("🤖 AI Service")
        ai_service = st.sidebar.selectbox(
            "Choose AI service",
            ["Auto-detect (Recommended)", "Free AI Only", "OpenAI Only", "No AI (Basic)"]
        )
        
        # API Status
        st.sidebar.subheader("🔧 System Status")
        self.show_api_status()
        
        return {
            'max_emails': max_emails,
            'check_replies': check_replies,
            'generate_drafts': generate_drafts,
            'ai_service': ai_service
        }
    
    def show_api_status(self):
        """Show API connection status"""
        # Check Gmail credentials
        if os.path.exists('credentials.json'):
            st.sidebar.success("✅ Gmail credentials found")
        else:
            st.sidebar.error("❌ Gmail credentials missing")
        
        # Check AI services
        ai_services = []
        
        if os.getenv('GEMINI_API_KEY'):
            ai_services.append("🤖 Gemini")
        
        if os.getenv('OPENAI_API_KEY'):
            ai_services.append("🧠 OpenAI")
        
        if os.getenv('GROQ_API_KEY'):
            ai_services.append("⚡ Groq")
        
        # Check if Ollama is running
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=1)
            if response.status_code == 200:
                ai_services.append("🏠 Ollama")
        except:
            pass
        
        if ai_services:
            st.sidebar.success(f"AI Services: {', '.join(ai_services)}")
        else:
            st.sidebar.warning("⚠️ No AI services configured")
    
    def initialize_agents(self, ai_service_choice):
        """Initialize Gmail and AI agents"""
        if self.gmail_agent is None:
            try:
                with st.spinner("🔄 Initializing Gmail Agent..."):
                    self.gmail_agent = GmailAgent(self.scopes)
                st.success("✅ Gmail Agent initialized!")
            except Exception as e:
                st.error(f"❌ Gmail initialization failed: {e}")
                return False
        
        if self.ai_agent is None:
            try:
                with st.spinner("🔄 Initializing AI Agent..."):
                    if ai_service_choice == "Free AI Only":
                        self.ai_agent = FreeAIAgent()
                        st.success("✅ Free AI Agent initialized!")
                    elif ai_service_choice == "OpenAI Only":
                        self.ai_agent = EmailAIAgent()
                        st.success("✅ OpenAI Agent initialized!")
                    elif ai_service_choice == "No AI (Basic)":
                        self.ai_agent = None
                        st.info("ℹ️ Running without AI processing")
                    else:  # Auto-detect
                        try:
                            self.ai_agent = FreeAIAgent()
                            st.success("✅ Free AI Agent initialized!")
                        except:
                            try:
                                self.ai_agent = EmailAIAgent()
                                st.success("✅ OpenAI Agent initialized!")
                            except:
                                self.ai_agent = None
                                st.warning("⚠️ No AI service available, using basic mode")
            except Exception as e:
                st.error(f"❌ AI initialization failed: {e}")
                self.ai_agent = None
        
        return True
    
    def fetch_emails(self, max_emails, check_replies):
        """Fetch and analyze emails"""
        if not self.gmail_agent:
            st.error("❌ Gmail agent not initialized")
            return []
        
        # Get user profile
        with st.spinner("📊 Getting Gmail profile..."):
            profile = self.gmail_agent.get_user_profile()
            if profile['email']:
                st.success(f"✅ Connected to: {profile['email']}")
            else:
                st.error("❌ Could not get Gmail profile")
                return []
        
        # Fetch emails
        with st.spinner(f"📥 Fetching {max_emails} recent emails..."):
            emails = self.gmail_agent.get_recent_emails(max_results=max_emails)
        
        if not emails:
            st.warning("⚠️ No emails found in inbox")
            return []
        
        st.success(f"✅ Retrieved {len(emails)} emails")
        
        # Check reply status
        if check_replies:
            with st.spinner("🔍 Checking reply status..."):
                progress_bar = st.progress(0)
                for i, email in enumerate(emails):
                    replied = self.gmail_agent.check_if_replied(
                        email['thread_id'], 
                        email['timestamp']
                    )
                    email['replied'] = replied
                    progress_bar.progress((i + 1) / len(emails))
                progress_bar.empty()
            st.success("✅ Reply status checked")
        else:
            for email in emails:
                email['replied'] = False
        
        # AI Processing
        if self.ai_agent:
            with st.spinner("🤖 Generating AI summaries..."):
                emails = self.ai_agent.batch_process_emails(emails)
            st.success("✅ AI summaries generated")
        
        return emails
    
    def generate_reply_drafts(self, emails):
        """Generate reply drafts for unreplied emails"""
        if not self.ai_agent:
            st.warning("⚠️ No AI agent available for reply generation")
            return emails
        
        unreplied = [email for email in emails if not email.get('replied', False)]
        
        if not unreplied:
            st.success("🎉 All emails have been replied to!")
            return emails
        
        with st.spinner(f"✍️ Generating {len(unreplied)} reply drafts..."):
            emails = self.ai_agent.generate_reply_drafts_for_unreplied(emails)
        
        st.success(f"✅ Generated {len(unreplied)} reply drafts")
        return emails
    
    def display_summary_metrics(self, emails):
        """Display summary metrics"""
        if not emails:
            return
        
        total_emails = len(emails)
        unreplied = sum(1 for email in emails if not email.get('replied', False))
        replied = total_emails - unreplied
        with_drafts = sum(1 for email in emails if email.get('reply_draft'))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📧 Total Emails", total_emails)
        
        with col2:
            st.metric("✅ Replied", replied)
        
        with col3:
            st.metric("⏳ Unreplied", unreplied)
        
        with col4:
            st.metric("✍️ Drafts Generated", with_drafts)
    
    def display_emails_table(self, emails):
        """Display emails in a nice table"""
        if not emails:
            return
        
        # Prepare data for table
        table_data = []
        for email in emails:
            table_data.append({
                'From': email.get('sender', 'Unknown')[:30],
                'Subject': email.get('subject', 'No Subject')[:50],
                'Date': email.get('date', '')[:20] if email.get('date') else 'Unknown',
                'Replied': '✅' if email.get('replied', False) else '❌',
                'AI Summary': email.get('ai_summary', 'No summary')[:60] + '...' if email.get('ai_summary') and len(email.get('ai_summary', '')) > 60 else email.get('ai_summary', 'No summary'),
                'Has Draft': '✍️' if email.get('reply_draft') else '—'
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
    
    def display_unreplied_emails(self, emails):
        """Display unreplied emails with drafts"""
        unreplied = [email for email in emails if not email.get('replied', False)]
        
        if not unreplied:
            st.success("🎉 All emails have been replied to!")
            return
        
        st.subheader(f"⏳ Unreplied Emails ({len(unreplied)})")
        
        for i, email in enumerate(unreplied, 1):
            with st.expander(f"📧 {i}. {email.get('subject', 'No Subject')[:50]}"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write("**From:**", email.get('sender', 'Unknown'))
                    st.write("**Date:**", email.get('date', 'Unknown'))
                    st.write("**Summary:**", email.get('ai_summary', 'No summary available'))
                
                with col2:
                    if email.get('reply_draft'):
                        st.write("**Suggested Reply:**")
                        st.text_area(
                            f"Draft {i}",
                            email['reply_draft'],
                            height=150,
                            key=f"draft_{i}"
                        )
                    else:
                        st.info("No reply draft generated")
    
    def export_results(self, emails):
        """Export results to CSV"""
        if not emails:
            return
        
        with st.spinner("📊 Exporting to CSV..."):
            filepath = self.data_processor.export_to_csv(emails)
        
        if filepath and os.path.exists(filepath):
            st.success(f"✅ Results exported to: {filepath}")
            
            # Provide download button
            with open(filepath, 'rb') as file:
                st.download_button(
                    label="📥 Download CSV Report",
                    data=file.read(),
                    file_name=os.path.basename(filepath),
                    mime='text/csv'
                )
        else:
            st.error("❌ Export failed")

def main():
    """Main Streamlit application"""
    app = StreamlitEmailAssistant()
    
    # Show header
    app.show_header()
    
    # Show sidebar configuration
    settings = app.show_sidebar_config()
    
    # Main content
    st.header("🚀 Email Analysis Dashboard")
    
    # Check prerequisites
    if not os.path.exists('credentials.json'):
        st.error("❌ Gmail credentials missing")
        st.info("""
        **Setup Required:**
        1. Go to Google Cloud Console
        2. Create OAuth 2.0 credentials
        3. Download as `credentials.json`
        4. Place in project directory
        """)
        return
    
    # Initialize agents button
    if st.button("🔄 Initialize System", type="primary"):
        if app.initialize_agents(settings['ai_service']):
            st.session_state.agents_initialized = True
        else:
            st.session_state.agents_initialized = False
    
    # Check if agents are initialized
    if not st.session_state.get('agents_initialized', False):
        st.info("👆 Click 'Initialize System' to start")
        return
    
    # Analyze emails button
    if st.button("📧 Analyze Emails", type="primary"):
        emails = app.fetch_emails(settings['max_emails'], settings['check_replies'])
        
        if emails:
            # Generate reply drafts if requested
            if settings['generate_drafts']:
                emails = app.generate_reply_drafts(emails)
            
            # Store emails in session state
            st.session_state.emails = emails
            st.session_state.analysis_complete = True
            
            st.success("🎉 Email analysis completed!")
    
    # Display results if analysis is complete
    if st.session_state.get('analysis_complete', False) and st.session_state.get('emails'):
        emails = st.session_state.emails
        
        # Summary metrics
        st.header("📊 Summary")
        app.display_summary_metrics(emails)
        
        # Emails table
        st.header("📧 All Emails")
        app.display_emails_table(emails)
        
        # Unreplied emails
        if settings['generate_drafts']:
            app.display_unreplied_emails(emails)
        
        # Export section
        st.header("📥 Export Results")
        if st.button("📊 Export to CSV"):
            app.export_results(emails)
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Google Agent Dev Kit Framework")

if __name__ == "__main__":
    main()
