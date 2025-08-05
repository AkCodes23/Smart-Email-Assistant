#!/usr/bin/env python3
"""
Smart Email Assistant - Project Cleanup Script
Removes unnecessary files while preserving core functionality
"""
import os
import shutil
from pathlib import Path


def cleanup_project():
    """Remove unnecessary files and directories"""
    
    # Files to remove (testing, development, alternative implementations)
    files_to_remove = [
        # Testing & Development Files
        'quick_test.py',
        'quick_test.bat',
        'test_app.py',
        'test_automatic.bat',
        'test_auto_auth.py',
        'test_backend.bat',
        'test_backend.py',
        'test_bypass.py',
        'test_desktop.bat',
        'test_desktop_client.py',
        'test_oauth.py',
        'test_one_email.bat',
        'test_reply.py',
        'test_simple_oauth.bat',
        'test_web_client.py',
        'test_web_oauth.bat',
        'validate_setup.py',
        'validate.py',
        'final_verification.py',
        
        # Alternative/Unused Agent Files
        'ai_agent.py',  # Using groq_ai_agent.py instead
        'free_ai_agent.py',  # Using groq_ai_agent.py instead
        'gmail_agent_simple.py',  # Using auto_gmail_agent.py instead
        
        # Setup & Utility Scripts
        'setup.py',
        'setup.bat',
        'setup_desktop_client.bat',
        'setup_native_client.py',
        'setup_streamlit.bat',
        'demo.py',
        'quick_start.py',
        'simple_gmail_test.py',
        'check_quota.py',
        'check_quotas.bat',
        'oauth_checker.py',
        
        # Fix & Debug Scripts
        'fix_oauth_consent.py',
        'fix_oauth_error.bat',
        'get_groq_key.bat',
        
        # Alternative Run Scripts
        'run.bat',
        'run_auto.bat',
        'run_free_ai.bat',
        'run_groq.bat',
        'run_streamlit.bat',
        'run_viewer.py',
        
        # Documentation Files (optional - can be removed if not needed)
        'AUTOMATIC_BYPASS_COMPLETE.md',
        'BACKEND_FIXED.md',
        'FIXED_COMPLETE.md',
        'FREE_AI_SETUP.md',
        'ISSUES_ANALYSIS.md',
        'OAUTH_SETUP_FIX.md',
        'PROJECT_SUMMARY.md',
        'REQUIREMENTS_CHECK.md',
        'SETUP_COMPLETE.md',
        'STREAMLIT_UI_GUIDE.md',
        'SUCCESS.md',
        'TECHNICAL_DOCS.md',
        'WARNINGS_FIXED.md',
        
        # Template & Example Files
        '.env.example',
        'credentials.json.template',
        'credentials_desktop_template.json',
        'client_secret_457434825539-vm4e7hv0uv3b6eb81pj34q2b6s9v5etd.apps.googleusercontent.com.json',
        
        # Temporary/Generated Files
        '100',
        '123.json',
        'token.pickle',
        
        # Alternative Requirements
        'requirements_streamlit.txt',
    ]
    
    # Directories to remove
    dirs_to_remove = [
        'Code',  # Empty directory
    ]
    
    print("🧹 Smart Email Assistant - Project Cleanup")
    print("=" * 50)
    
    removed_files = []
    not_found_files = []
    
    # Remove files
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                removed_files.append(file_path)
                print(f"✅ Removed: {file_path}")
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
        else:
            not_found_files.append(file_path)
    
    # Remove directories
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                removed_files.append(f"{dir_path}/")
                print(f"✅ Removed directory: {dir_path}/")
            except Exception as e:
                print(f"❌ Failed to remove directory {dir_path}: {e}")
    
    # Clean old CSV files from output directory (keep the directory)
    output_dir = Path('output')
    if output_dir.exists():
        csv_files = list(output_dir.glob('*.csv'))
        if len(csv_files) > 3:  # Keep only the 3 most recent
            csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for old_csv in csv_files[3:]:
                try:
                    old_csv.unlink()
                    removed_files.append(str(old_csv))
                    print(f"✅ Removed old CSV: {old_csv}")
                except Exception as e:
                    print(f"❌ Failed to remove {old_csv}: {e}")
    
    print("\n" + "=" * 50)
    print("📊 Cleanup Summary:")
    print(f"✅ Files removed: {len(removed_files)}")
    print(f"ℹ️  Files not found (already clean): {len(not_found_files)}")
    
    print("\n🎯 CORE FILES PRESERVED:")
    essential_files = [
        'main.py',
        'auto_gmail_agent.py', 
        'groq_ai_agent.py',
        'ui.py',
        'data_processor.py',
        'email_viewer.py',
        'streamlit_app.py',
        'config.py',
        '.env',
        'credentials.json',
        'requirements.txt',
        'README.md',
        '.gitignore'
    ]
    
    for essential_file in essential_files:
        if os.path.exists(essential_file):
            print(f"✅ {essential_file}")
        else:
            print(f"⚠️  {essential_file} (missing)")
    
    print("\n🚀 Project cleaned successfully!")
    print("Your Smart Email Assistant is ready to run with:")
    print("  python main.py              # Main application")
    print("  streamlit run email_viewer.py  # Web interface")
    
    return len(removed_files)

if __name__ == "__main__":
    removed_count = cleanup_project()
    print(f"\n✨ Cleanup complete! Removed {removed_count} unnecessary files.")
