# Smart Email Assistant

> An intelligent command-line tool designed to streamline your email management process by integrating with the Gmail API and leveraging the power of Groq's AI for fast, insightful analysis.

This tool helps you quickly get on top of your inbox by summarizing recent emails, identifying which ones need a reply, and even drafting intelligent responses for you.

---

## ✨ Core Features

* **🤖 AI-Powered Summarization**: Uses the high-speed Groq AI engine to generate concise, easy-to-read summaries of your emails, so you can grasp the content at a glance.
* **📫 Unreplied Email Detection**: Intelligently scans your email threads to accurately identify messages that you have not yet replied to.
* **✍️ Smart Reply Generation**: For every unreplied email, the assistant drafts a context-aware, ready-to-send reply, saving you valuable time.
* **📊 Clear & Concise Reporting**: Displays the results in well-organized tables directly in your terminal, including a summary of statistics and a list of all processed emails.
* **📄 CSV Data Export**: Automatically exports all the analyzed data—including summaries and draft replies—into a timestamped CSV file for your records or further analysis.
* **⚙️ Flexible Configuration**: Allows you to customize the number of emails to fetch and choose whether to perform reply analysis and draft generation.
* **🔑 Simple Authentication**: Guides you through a one-time setup for Gmail and Groq API keys, with a built-in check for all necessary prerequisites.
* **🤫 Automatic OAuth Bypass (Optional)**: Includes an experimental mode (`auto_gmail_agent`) to simplify the Google OAuth flow for repeated use.

---

## 🚀 How It Works

The application follows a clear, step-by-step process to manage your emails:

1.  **Prerequisite Check**: Verifies that your `credentials.json` for the Gmail API and your `GROQ_API_KEY` in the `.env` file are present.
2.  **User Configuration**: Prompts you to specify how many emails you want to analyze and whether you need to check for replies and generate drafts.
3.  **Agent Initialization**: Securely connects to the Gmail API and initializes the Groq AI agent.
4.  **Fetch Emails**: Retrieves the most recent emails from your Gmail inbox based on your input.
5.  **AI Analysis & Summarization**: For each email, it sends the content to the Groq AI, which returns a summary. The application also checks the reply status of each email thread if requested.
6.  **Draft Generation**: For emails identified as unreplied, it uses the AI to generate a relevant reply draft.
7.  **Display & Export**: The results are displayed in your terminal, and a full report is saved as a CSV file in the `output` directory.

---

## 🛠️ Tech Stack

* **Language**: Python 3
* **AI Engine**: Groq API for Large Language Model (LLM) inference
* **Email Service**: Google Gmail API
* **CLI Display**: Rich (for beautiful terminal output)
* **Dependencies**: `google-api-python-client`, `google-auth-oauthlib`, `groq`, `python-dotenv`, `pandas`

---
