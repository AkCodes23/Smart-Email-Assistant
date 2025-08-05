"""
Groq AI Agent for Smart Email Assistant
Uses Groq's fast inference API with Llama models
"""
import os
from typing import Any, Dict, List

from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)


class GroqAIAgent:
    """AI Agent using Groq API for email summarization and reply generation"""
    
    def __init__(self):
        """Initialize Groq AI Agent with API key"""
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            self.model = "llama-3.3-70b-versatile"
            print("🚀 Groq AI Agent initialized successfully with Llama 3.3 70B")
        except ImportError:
            raise ImportError("Groq library not installed. Run: pip install groq")
        except Exception as e:
            raise Exception(f"Failed to initialize Groq client: {e}")
    
    def summarize_email(self, subject: str, body: str, sender: str) -> str:
        """Generate AI summary of email content"""
        try:
            # Prepare the prompt for concise summaries
            prompt = f"""
Summarize this email in 2-3 short, clear bullet points. Be concise and direct.

Email Details:
From: {sender}
Subject: {subject}
Content: {body[:1500]}

Focus only on the main point and any important actions/deadlines.
"""
            
            # Call Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150,
                top_p=1,
                stream=False
            )
            
            summary = completion.choices[0].message.content.strip()
            
            # Clean up the summary and ensure bullet points
            if not summary.startswith("•"):
                # If no bullet points, format it properly
                lines = summary.split('\n')
                formatted_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("•") and not line.startswith("-"):
                        formatted_lines.append(f"• {line}")
                    elif line:
                        formatted_lines.append(line)
                
                if formatted_lines:
                    summary = '\n'.join(formatted_lines)
            
            return summary
            
        except Exception as e:
            print(f"⚠️ Groq error: {e}")
            return self._generate_fallback_summary(subject, body, sender)
    
    def generate_reply_draft(self, subject: str, body: str, sender: str) -> str:
        """Generate AI reply draft for email"""
        try:
            # Handle empty or very short bodies
            if not body or len(body.strip()) < 10:
                print("     ⚠️ Empty/short body, using subject for context")
                body = f"Email regarding: {subject}"
            
            # Prepare the prompt
            prompt = f"""Write a professional email reply for this message. Be concise, polite, and appropriate to the context.

From: {sender}
Subject: {subject}
Body: {body[:800]}

Write a brief professional reply:"""
            
            # Call Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300,
                top_p=1,
                stream=False
            )
            
            reply = completion.choices[0].message.content.strip()
            
            # Add subject line if not present
            if not reply.startswith("Subject:"):
                reply_subject = f"Re: {subject}" if not subject.startswith("Re:") else subject
                reply = f"Subject: {reply_subject}\n\n{reply}"
            
            return reply
            
        except Exception as e:
            print(f"⚠️ Groq error: {e}")
            return self._generate_fallback_reply(subject, sender, api_error=True)
    
    def _generate_fallback_summary(self, subject: str, body: str, sender: str) -> str:
        """Generate a simple fallback summary when AI fails"""
        # Extract sender name
        sender_name = sender.split('@')[0].split('.')[0].title() if '@' in sender else sender
        if '<' in sender:
            sender_name = sender.split('<')[0].strip().strip('"') or sender_name
        
        # Create simple summary
        clean_body = body.replace('\n', ' ').replace('\r', ' ').strip()
        
        if len(clean_body) > 100:
            body_preview = clean_body[:100] + "..."
        else:
            body_preview = clean_body or "No content available"
        
        return f"• Email from {sender_name} about {subject}\n• {body_preview}"
    
    def _generate_fallback_reply(self, subject: str, sender: str, api_error: bool = False) -> str:
        """Generate a fallback reply when AI fails"""
        sender_name = sender.split('@')[0].split('.')[0].title() if '@' in sender else sender
        if '<' in sender:
            sender_name = sender.split('<')[0].strip().strip('"') or sender_name
        
        prefix = "[API Error] " if api_error else ""
        
        return f"""{prefix}Hi {sender_name},

Thank you for your email regarding "{subject}".

I have received your message and will review it shortly. I'll get back to you with a response as soon as possible.

Best regards"""
    
    def batch_process_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple emails with AI summaries"""
        print(f"🤖 Processing {len(emails)} emails with Groq AI...")
        
        for i, email in enumerate(emails, 1):
            try:
                print(f"   Processing email {i}/{len(emails)}...")
                
                summary = self.summarize_email(
                    email.get('subject', ''),
                    email.get('body', ''),
                    email.get('sender', '')
                )
                
                email['ai_summary'] = summary
                
            except Exception as e:
                print(f"⚠️ Error processing email {i}: {e}")
                email['ai_summary'] = f"Error processing: {str(e)[:50]}..."
        
        return emails
    
    def generate_reply_drafts_for_unreplied(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate reply drafts for unreplied emails"""
        unreplied = [email for email in emails if not email.get('replied', False)]
        
        print(f"✍️ Generating {len(unreplied)} reply drafts with Groq...")
        
        for i, email in enumerate(unreplied, 1):
            try:
                print(f"   Generating draft {i}/{len(unreplied)}...")
                
                subject = email.get('subject', '')
                body = email.get('body', '')
                sender = email.get('sender', '')
                
                # Debug info
                print(f"     Subject: {subject[:30]}...")
                print(f"     Body length: {len(body)} chars")
                print(f"     Body preview: {body[:50] if body else 'EMPTY'}...")
                print(f"     Sender: {sender[:30]}...")
                
                draft = self.generate_reply_draft(subject, body, sender)
                
                # Ensure we have a valid reply
                if draft and len(draft.strip()) > 10:
                    email['draft_reply'] = draft
                    print(f"     ✅ Draft saved ({len(draft)} chars)")
                else:
                    # Generate a basic fallback reply
                    sender_name = email.get('sender', '').split('@')[0].split('.')[0].title()
                    email['draft_reply'] = f"""Hi {sender_name},

Thank you for your email regarding "{email.get('subject', 'your message')}".

I have received your message and will review it shortly. I'll get back to you with a response as soon as possible.

Best regards"""
                    print("     ⚠️ Using fallback reply")
                
            except Exception as e:
                print(f"⚠️ Error generating draft {i}: {e}")
                email['draft_reply'] = f"Error generating draft: {str(e)[:50]}..."
        
        return emails