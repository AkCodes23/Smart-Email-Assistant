"""
Smart Email Assistant Tool - Main Application
Built with Google Agent Dev Kit Framework

This tool integrates with Gmail API and uses AI to:
- Summarize email content
- Identify unreplied emails
- Generate smart reply drafts
- Export results to CSV
"""
import os
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv

from data_processor import DataProcessor
from groq_ai_agent import GroqAIAgent
from ui import EmailUI

# Import our custom agents and utilities
try:
    # Try the automatic bypass agent first
    from auto_gmail_agent import AutoGmailAgent as GmailAgent
    print("🚀 Using automatic OAuth bypass mode")
except ImportError:
    # Fallback to regular agent
    from gmail_agent import GmailAgent
    print("📧 Using standard Gmail agent")

# Load environment variables
load_dotenv()


class SmartEmailAssistant:
    """Main application class orchestrating all agents"""
    
    def __init__(self):
        self.ui = EmailUI()
        self.gmail_agent = None
        self.ai_agent = None
        self.data_processor = DataProcessor()
        
        # Gmail API scopes
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send'
        ]
    
    def initialize_agents(self) -> bool:
        """Initialize Gmail and AI agents"""
        try:
            self.ui.show_processing_step("Initializing Gmail Agent...")
            self.gmail_agent = GmailAgent(self.scopes)
            self.ui.display_success("Gmail API connection established!")
            
            self.ui.show_processing_step("Initializing Groq AI Agent...")
            
            # Use only Groq AI
            groq_key = os.getenv('GROQ_API_KEY')
            if not groq_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            self.ai_agent = GroqAIAgent()
            self.ui.display_success("Groq AI Agent initialized successfully!")
            
            return True
            
        except FileNotFoundError as e:
            self.ui.display_error(f"Configuration file missing: {e}")
            self.ui.display_info("Please ensure credentials.json is in the project directory")
            return False
            
        except ValueError as e:
            self.ui.display_error(f"Environment configuration error: {e}")
            self.ui.display_info("Please check your .env file and API keys")
            return False
            
        except Exception as e:
            self.ui.display_error(f"Failed to initialize agents: {e}")
            return False
    
    def fetch_and_analyze_emails(self, max_emails: int, check_replies: bool) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail and analyze them"""
        
        # Get user profile first
        profile = self.gmail_agent.get_user_profile()
        if profile['email']:
            self.ui.display_info(f"Connected to Gmail account: {profile['email']}")
        
        # Fetch emails
        self.ui.show_processing_step(f"Fetching {max_emails} recent emails from Gmail...")
        emails = self.gmail_agent.get_recent_emails(max_results=max_emails)
        
        if not emails:
            self.ui.display_warning("No emails found in inbox")
            return []
        
        self.ui.display_success(f"Retrieved {len(emails)} emails")
        
        # Check reply status if requested
        if check_replies:
            self.ui.show_processing_step("Analyzing email threads for reply status...")
            with self.ui.display_progress("Checking replies...") as progress:
                task = progress.add_task("Processing...", total=len(emails))
                
                for email in emails:
                    replied = self.gmail_agent.check_if_replied(
                        email['thread_id'], 
                        email['timestamp']
                    )
                    email['replied'] = replied
                    progress.update(task, advance=1)
        else:
            # Default all to unreplied for faster processing
            for email in emails:
                email['replied'] = False
        
        # Generate AI summaries
        self.ui.show_processing_step("Generating AI-powered email summaries...")
        try:
            emails = self.ai_agent.batch_process_emails(emails)
        except Exception as e:
            self.ui.display_warning(f"AI summarization failed: {e}")
            # Add fallback summaries
            for email in emails:
                if not email.get('ai_summary'):
                    email['ai_summary'] = f"Email from {email.get('sender', 'Unknown')} regarding {email.get('subject', 'No subject')}"
        
        return emails
    
    def generate_reply_drafts(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate reply drafts for unreplied emails"""
        unreplied_count = sum(1 for email in emails if not email.get('replied', False))
        
        if unreplied_count == 0:
            self.ui.display_success("All emails have been replied to!")
            return emails
        
        self.ui.show_processing_step(f"Generating reply drafts for {unreplied_count} unreplied emails...")
        try:
            return self.ai_agent.generate_reply_drafts_for_unreplied(emails)
        except Exception as e:
            self.ui.display_warning(f"AI draft generation failed: {e}")
            # Add fallback drafts for unreplied emails
            for email in emails:
                if not email.get('replied', False) and not email.get('draft_reply'):
                    sender_name = email.get('sender', 'Unknown').split('@')[0].split('<')[0].strip().strip('"')
                    email['draft_reply'] = f"""Hi {sender_name},

Thank you for your email regarding "{email.get('subject', 'your message')}".

I have received your message and will review it shortly. I'll get back to you with a response as soon as possible.

Best regards"""
            return emails
    
    def display_results(self, emails: List[Dict[str, Any]], show_drafts: bool = True):
        """Display analysis results to user"""
        
        # Show summary statistics
        self.data_processor.display_summary_table(emails)
        
        # Show email table
        self.ui.display_email_table(emails, show_drafts=False)
        
        # Show detailed summaries
        self.ui.display_detailed_summaries(emails)
        
        # Show unreplied emails with drafts
        if show_drafts:
            self.ui.display_unreplied_emails(emails)
    
    def export_results(self, emails: List[Dict[str, Any]]) -> str:
        """Export results to CSV"""
        self.ui.show_processing_step("Exporting results to CSV...")
        filepath = self.data_processor.export_to_csv(emails)
        
        if filepath:
            self.ui.display_success(f"Results exported to: {filepath}")
        
        return filepath
    
    def run(self):
        """Main application flow"""
        # Display welcome
        self.ui.display_welcome()
        
        # Check prerequisites
        if not self.check_prerequisites():
            return
        
        # Get user settings
        settings = self.ui.get_user_settings()
        
        # Initialize agents
        if not self.initialize_agents():
            return
        
        try:
            # Fetch and analyze emails
            emails = self.fetch_and_analyze_emails(
                settings['max_emails'], 
                settings['check_replies']
            )
            
            if not emails:
                return
            
            # Generate reply drafts if requested
            if settings['generate_drafts']:
                emails = self.generate_reply_drafts(emails)
            
            # Display results
            self.display_results(emails, settings['generate_drafts'])
            
            # Export to CSV
            self.export_results(emails)
            
            self.ui.display_success("Email analysis completed successfully!")
            
        except KeyboardInterrupt:
            self.ui.display_warning("\nOperation cancelled by user")
            
        except Exception as e:
            self.ui.display_error(f"An error occurred: {e}")
            import traceback
            print(traceback.format_exc())
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        
        # Check for credentials.json
        if not os.path.exists('credentials.json'):
            self.ui.display_error("credentials.json not found")
            self.ui.display_info("""
Please set up Gmail API credentials:
1. Go to Google Cloud Console
2. Create a project and enable Gmail API
3. Create OAuth 2.0 credentials
4. Download as credentials.json
5. Place in project root directory
            """)
            return False
        
        # Check for Groq API key
        groq_key = os.getenv('GROQ_API_KEY')
        
        if not groq_key:
            self.ui.display_error("Groq API key not found")
            self.ui.display_info("""
Please set up your Groq API key in your .env file:
GROQ_API_KEY=your_groq_api_key_here

Get your free API key from: https://console.groq.com/
            """)
            return False
        
        self.ui.display_success("✅ Groq API key found")
        
        return True


def main():
    """Entry point for the Smart Email Assistant"""
    try:
        app = SmartEmailAssistant()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()