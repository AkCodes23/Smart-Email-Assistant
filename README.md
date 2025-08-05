# Google Agent Dev Kit - Smart Email Assistant

## Overview
This is a Smart Email Assistant Tool built using Google Agent Dev Kit framework that automates email management tasks including summarization and intelligent reply generation.

## Features
- Connect to Gmail API
- Summarize emails with clear bullet points
- Identify unreplied emails
- Generate smart, context-aware reply drafts
- Export results to CSV format

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Google API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials file as `credentials.json`
6. Place it in the project root directory

### 3. Environment Variables
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_SCOPES=https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send
```

### 4. Run the Application
```bash
python main.py
```

## Usage
The tool will:
1. Authenticate with Gmail
2. Fetch recent emails
3. Analyze and summarize content
4. Generate reply drafts for unreplied emails
5. Display results and save to CSV

## Output
- Console display with rich formatting
- CSV export with columns: Sender, Subject, Email Summary, Replied (Yes/No), Draft Reply
