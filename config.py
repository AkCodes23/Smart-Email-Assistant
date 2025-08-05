"""
Configuration settings for Smart Email Assistant
"""

# Email processing settings
DEFAULT_EMAIL_LIMIT = 50
MAX_EMAIL_LIMIT = 200

# AI model settings
AI_MODEL = "gpt-3.5-turbo"
AI_TEMPERATURE = 0.3
MAX_TOKENS = 500

# Summary settings
MAX_SUMMARY_BULLETS = 4
MAX_EMAIL_BODY_LENGTH = 2000

# Reply generation settings
MAX_REPLY_LENGTH = 300
INCLUDE_GREETING = True
INCLUDE_CLOSING = True

# Export settings
OUTPUT_DIRECTORY = "output"
CSV_ENCODING = "utf-8"

# Gmail API settings
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

# Rate limiting
REQUESTS_PER_MINUTE = 60
BATCH_SIZE = 10
