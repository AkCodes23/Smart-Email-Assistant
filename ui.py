"""
User interface utilities using Rich library for beautiful console output
"""
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, IntPrompt
from rich.table import Table


class EmailUI:
    """Rich-based user interface for Smart Email Assistant"""
    
    def __init__(self):
        self.console = Console()
    
    def display_welcome(self):
        """Display welcome banner"""
        welcome_text = """
🚀 Smart Email Assistant Tool
Built with Google Agent Dev Kit Framework

This tool will help you:
• Connect to your Gmail inbox
• Summarize email content with AI
• Identify unreplied emails
• Generate smart reply drafts
• Export results to CSV
        """
        
        self.console.print(Panel(
            welcome_text.strip(),
            title="[bold blue]Welcome[/bold blue]",
            border_style="blue"
        ))
    
    def display_progress(self, description: str, total: int = None):
        """Display progress indicator"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
    
    def display_email_table(self, emails: List[Dict[str, Any]], show_drafts: bool = False):
        """Display emails in a formatted table"""
        if not emails:
            self.console.print("[yellow]No emails to display[/yellow]")
            return
        
        # Create table
        table = Table(title="📧 Email Analysis Results")
        
        table.add_column("Sender", style="cyan", no_wrap=False, width=20)
        table.add_column("Subject", style="magenta", width=25)
        table.add_column("Summary", style="green", width=50)
        table.add_column("Replied", style="yellow", justify="center", width=8)
        
        if show_drafts:
            table.add_column("Draft Reply", style="blue", width=35)
        
        # Add rows
        for email in emails[:20]:  # Limit to first 20 for display
            sender = self._truncate_text(email.get('sender', 'Unknown'), 25)
            subject = self._truncate_text(email.get('subject', 'No Subject'), 30)
            summary = self._truncate_text(email.get('ai_summary', 'No summary'), 40)
            replied = "✅ Yes" if email.get('replied', False) else "❌ No"
            
            if show_drafts:
                draft = self._truncate_text(email.get('draft_reply', 'N/A'), 35)
                table.add_row(sender, subject, summary, replied, draft)
            else:
                table.add_row(sender, subject, summary, replied)
        
        self.console.print(table)
        
        if len(emails) > 20:
            self.console.print(f"\n[yellow]Showing first 20 of {len(emails)} emails. Full data exported to CSV.[/yellow]")
    
    def display_detailed_summaries(self, emails: List[Dict[str, Any]]):
        """Display detailed summaries for each email"""
        if not emails:
            return
        
        self.console.print("\n[bold blue]📋 Detailed Email Summaries[/bold blue]")
        
        for i, email in enumerate(emails[:10], 1):  # Show first 10 detailed summaries
            sender = email.get('sender', 'Unknown')
            subject = email.get('subject', 'No Subject')
            summary = email.get('ai_summary', 'No summary available')
            replied = "✅ Replied" if email.get('replied', False) else "❌ Unreplied"
            
            # Clean sender for display
            display_sender = sender.split('<')[0].strip().strip('"') if '<' in sender else sender
            
            panel_content = f"""
[bold cyan]From:[/bold cyan] {display_sender}
[bold magenta]Subject:[/bold magenta] {subject}
[bold yellow]Status:[/bold yellow] {replied}

[bold green]📋 Summary:[/bold green]
{summary}
            """
            
            self.console.print(Panel(
                panel_content.strip(),
                title=f"[bold blue]Email #{i}[/bold blue]",
                border_style="blue",
                padding=(1, 2)
            ))
        
        if len(emails) > 10:
            self.console.print("\n[dim]Showing first 10 detailed summaries. View CSV for complete analysis.[/dim]")
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text for table display"""
        if not text:
            return ""
        
        # For bullet-point summaries, show first few bullet points
        if "•" in text:
            lines = text.split('\n')
            bullet_points = [line.strip() for line in lines if line.strip().startswith('•')]
            
            if bullet_points:
                # Show first 2-3 bullet points that fit in the space
                result = ""
                for point in bullet_points[:3]:
                    if len(result + point) <= max_length - 3:
                        result += point + "\n"
                    else:
                        break
                
                if result:
                    return result.strip() + ("..." if len(bullet_points) > result.count('•') else "")
        
        # Regular text truncation
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def display_unreplied_emails(self, emails: List[Dict[str, Any]]):
        """Display unreplied emails with draft replies"""
        unreplied = [email for email in emails if not email.get('replied', False)]
        
        if not unreplied:
            self.console.print("[green]🎉 All emails have been replied to![/green]")
            return
        
        self.console.print(f"\n[red]📥 Found {len(unreplied)} unreplied emails:[/red]")
        
        for i, email in enumerate(unreplied[:10], 1):  # Show first 10
            sender = email.get('sender', 'Unknown')
            subject = email.get('subject', 'No Subject')
            draft = email.get('draft_reply', 'No draft available')
            
            # Clean draft text to prevent display issues
            if draft and len(draft) > 500:
                draft = draft[:500] + "..."
            
            # Remove any problematic characters that might cause display issues
            draft = draft.replace('\r', '').replace('\x00', '')
            
            panel_content = f"""
[bold]From:[/bold] {sender}
[bold]Subject:[/bold] {subject}

[bold]Suggested Reply:[/bold]
{draft}
            """
            
            self.console.print(Panel(
                panel_content.strip(),
                title=f"[red]Unreplied Email #{i}[/red]",
                border_style="red"
            ))
        
        if len(unreplied) > 10:
            self.console.print(f"\n[yellow]Showing first 10 of {len(unreplied)} unreplied emails.[/yellow]")
    
    def get_user_settings(self) -> Dict[str, Any]:
        """Get user preferences for email processing"""
        settings = {}
        
        self.console.print("\n[bold]📝 Configuration Settings[/bold]")
        
        # Number of emails to process
        settings['max_emails'] = IntPrompt.ask(
            "How many recent emails to analyze?",
            default=50,
            show_default=True
        )
        
        # Whether to check reply status (can be slow)
        settings['check_replies'] = Confirm.ask(
            "Check reply status? (slower but more accurate)",
            default=True
        )
        
        # Whether to generate draft replies
        settings['generate_drafts'] = Confirm.ask(
            "Generate draft replies for unreplied emails?",
            default=True
        )
        
        return settings
    
    def display_error(self, error_message: str):
        """Display error message"""
        self.console.print(Panel(
            f"[red]❌ Error: {error_message}[/red]",
            title="[red]Error[/red]",
            border_style="red"
        ))
    
    def display_success(self, message: str):
        """Display success message"""
        self.console.print(f"[green]✅ {message}[/green]")
    
    def display_info(self, message: str):
        """Display info message"""
        self.console.print(f"[blue]ℹ️  {message}[/blue]")
    
    def display_warning(self, message: str):
        """Display warning message"""
        self.console.print(f"[yellow]⚠️  {message}[/yellow]")
    
    def show_processing_step(self, step: str):
        """Show current processing step"""
        self.console.print(f"\n[bold blue]🔄 {step}[/bold blue]")
    
    def wait_for_user(self):
        """Wait for user to press enter"""
        self.console.input("\n[dim]Press Enter to continue...[/dim]")
