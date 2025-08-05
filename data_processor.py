"""
Data processing and export utilities for Smart Email Assistant
"""
import csv
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd


class DataProcessor:
    """Data processing agent for email analysis results"""
    
    def __init__(self):
        self.output_dir = "output"
        self._ensure_output_dir()
    
    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def prepare_email_data_for_export(self, emails: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Prepare email data for CSV export with clean formatting"""
        export_data = []
        
        for email in emails:
            # Clean and format sender
            sender = self._clean_sender(email.get('sender', 'Unknown'))
            
            # Clean subject
            subject = email.get('subject', 'No Subject').strip()
            if len(subject) > 100:
                subject = subject[:97] + "..."
            
            # Clean summary
            summary = email.get('ai_summary', 'No summary available').strip()
            # Remove bullet points for cleaner CSV
            summary = summary.replace('•', '-').replace('\n', ' | ')
            
            # Replied status
            replied = "Yes" if email.get('replied', False) else "No"
            
            # Draft reply (clean up formatting)
            draft_reply = email.get('draft_reply', 'N/A')
            if draft_reply and draft_reply != 'N/A':
                # Clean up draft reply formatting
                draft_reply = draft_reply.replace('\n\n', ' | ').replace('\n', ' ')
                if len(draft_reply) > 300:
                    draft_reply = draft_reply[:297] + "..."
            
            # Timestamp for reference
            timestamp = email.get('timestamp', datetime.now())
            if isinstance(timestamp, datetime):
                formatted_date = timestamp.strftime('%Y-%m-%d %H:%M')
            elif isinstance(timestamp, (int, float)) and timestamp > 0:
                # Convert Unix timestamp to datetime
                try:
                    dt = datetime.fromtimestamp(timestamp)
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                except (ValueError, OSError):
                    formatted_date = str(timestamp)
            else:
                formatted_date = str(timestamp)
            
            export_data.append({
                'Sender': sender,
                'Subject': subject,
                'Date': formatted_date,
                'Email Summary': summary,
                'Replied': replied,
                'Draft Reply': draft_reply
            })
        
        return export_data
    
    def _clean_sender(self, sender: str) -> str:
        """Clean sender field for better readability"""
        try:
            # Handle formats like "John Doe <john@example.com>"
            if '<' in sender and '>' in sender:
                # Extract name part
                name_part = sender.split('<')[0].strip()
                email_part = sender.split('<')[1].split('>')[0].strip()
                
                if name_part and name_part != email_part:
                    return f"{name_part} ({email_part})"
                else:
                    return email_part
            
            return sender.strip()
            
        except Exception:
            return sender
    
    def export_to_csv(self, emails: List[Dict[str, Any]], filename: str = None) -> str:
        """Export email analysis results to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"email_analysis_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data for export
        export_data = self.prepare_email_data_for_export(emails)
        
        try:
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if export_data:
                    fieldnames = export_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(export_data)
            
            print(f"✅ Data exported to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return ""
    
    def export_to_pandas(self, emails: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert email data to pandas DataFrame for analysis"""
        export_data = self.prepare_email_data_for_export(emails)
        return pd.DataFrame(export_data)
    
    def generate_summary_stats(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics about the email analysis"""
        total_emails = len(emails)
        replied_emails = sum(1 for email in emails if email.get('replied', False))
        unreplied_emails = total_emails - replied_emails
        
        # Get unique senders
        senders = set()
        for email in emails:
            sender = email.get('sender', '')
            if '<' in sender:
                email_addr = sender.split('<')[1].split('>')[0].strip()
                senders.add(email_addr)
            else:
                senders.add(sender)
        
        # Get date range
        timestamps = [email.get('timestamp', datetime.now()) for email in emails]
        valid_timestamps = [ts for ts in timestamps if isinstance(ts, datetime)]
        
        if valid_timestamps:
            earliest = min(valid_timestamps)
            latest = max(valid_timestamps)
            date_range = f"{earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}"
        else:
            date_range = "Unknown"
        
        return {
            'total_emails': total_emails,
            'replied_emails': replied_emails,
            'unreplied_emails': unreplied_emails,
            'reply_rate': f"{(replied_emails/total_emails*100):.1f}%" if total_emails > 0 else "0%",
            'unique_senders': len(senders),
            'date_range': date_range,
            'drafts_generated': sum(1 for email in emails if email.get('draft_reply') and email.get('draft_reply') != 'N/A')
        }
    
    def display_summary_table(self, emails: List[Dict[str, Any]]) -> None:
        """Display a formatted summary table of email analysis"""
        stats = self.generate_summary_stats(emails)
        
        print("\n" + "="*60)
        print("📊 EMAIL ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total Emails Analyzed:    {stats['total_emails']}")
        print(f"Replied Emails:           {stats['replied_emails']}")
        print(f"Unreplied Emails:         {stats['unreplied_emails']}")
        print(f"Reply Rate:               {stats['reply_rate']}")
        print(f"Unique Senders:           {stats['unique_senders']}")
        print(f"Date Range:               {stats['date_range']}")
        print(f"Draft Replies Generated:  {stats['drafts_generated']}")
        print("="*60)
