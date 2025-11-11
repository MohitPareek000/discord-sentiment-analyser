# Discord Sentiment Analysis Bot

A Discord bot that monitors all messages across all servers, analyzes sentiment based on custom rules, logs data to Google Sheets, and automatically posts negative sentiment messages to a dedicated channel.

## Features

- **Real-time Message Monitoring**: Monitors all messages across all Discord servers the bot is in
- **Hybrid Sentiment Analysis**: Combines rule-based patterns from `sentiment.md` with 2223+ real negative examples from `sentimentManual.md`
- **Multi-language Support**: Detects negative sentiment in English and Hindi/Hinglish
- **Google Sheets Logging**: Automatically logs all messages with comprehensive data points
- **Centralized Notifications**: Posts all negative messages from all servers to a single admin channel
- **Multi-server Support**: Works across multiple Discord servers simultaneously

## Data Points Captured

Each message is logged with the following information:
1. `timestamp` - Full timestamp (YYYY-MM-DD HH:MM:SS)
2. `date` - Date only (YYYY-MM-DD)
3. `message_id` - Unique Discord message ID
4. `message_body` - The actual message content
5. `sentiment` - Either "negative" or "neutral"
6. `channel_id` - Discord channel ID
7. `channel_name` - Name of the channel
8. `server_name` - Name of the Discord server
9. `discord_userName` - Username of the message author

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- A Discord account with permission to create bots
- A Google Cloud Platform account

### 2. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
   - PRESENCE INTENT
5. Click "Reset Token" and copy your bot token (you'll need this later)
6. Go to "OAuth2" > "URL Generator"
7. Select scopes: `bot`
8. Select bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - Embed Links
9. Copy the generated URL and use it to invite the bot to your servers

### 3. Google Sheets API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Enable Google Drive API (same process)
5. Create Service Account credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and click "Create"
   - Skip granting roles (click "Continue" then "Done")
6. Create a key for the service account:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose "JSON" format
   - Save the downloaded file as `credentials.json` in your project directory
7. Share your Google Sheet with the service account email:
   - Open the email from the credentials.json file (`client_email`)
   - Share your Google Sheet with this email (give "Editor" permission)

### 4. Create Discord Channel

**Option A: Centralized Admin Server (Recommended)**
1. Create a dedicated "Admin" Discord server
2. Create a text channel named `discord_negative_ticket` in this server
3. All negative messages from ALL servers will be posted to this single channel
4. Set `ADMIN_SERVER_NAME=Admin` in your `.env` file (exact server name)

**Option B: Per-Server Channels**
1. In each Discord server, create a text channel named `discord_negative_ticket`
2. Leave `ADMIN_SERVER_NAME` empty in your `.env` file
3. Negative messages will be posted to each server's own channel

Ensure the bot has permission to send messages in the channel(s).

### 5. Installation

```bash
# Clone or download the project
cd discordMessages_sentiment

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   GOOGLE_SHEETS_CREDENTIALS=credentials.json
   SPREADSHEET_NAME=discord_messages_sentiment
   NEGATIVE_CHANNEL_NAME=discord_negative_ticket
   ADMIN_SERVER_NAME=Admin
   ```

   **Note**: Set `ADMIN_SERVER_NAME` to your admin server's exact name, or leave it empty/remove it to post to each server's own channel.

3. Place your `credentials.json` file in the project directory

### 7. Running the Bot

```bash
python discord_bot.py
```

The bot will:
- Connect to Discord
- Log all messages to Google Sheets
- Analyze sentiment for each message
- Post negative sentiment messages to the designated channel

## Project Structure

```
discordMessages_sentiment/
├── discord_bot.py           # Main bot file
├── sentiment_analyzer.py    # Sentiment analysis logic
├── sheets_manager.py        # Google Sheets integration
├── sentiment.md             # Sentiment analysis rules (rule-based)
├── sentimentManual.md       # 2223+ real negative examples (example-based)
├── SENTIMENT_PATTERNS.md    # Detailed pattern documentation
├── SECURITY.md              # Security best practices
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## Sentiment Analysis Rules

The bot uses a **hybrid approach** with **three layers of analysis** to identify negative sentiment:

### 1. Pattern Matching (158 Patterns)

**sentiment.md** - Rule-based pattern definitions organized by priority:
   - **Critical Signals** (100 patterns, HIGH priority): quit, refund, frustrated, confusion, help-seeking questions, doubts, negative contractions
   - **Support Failures** (21 patterns, HIGH priority): unable to reach, not responding, ticket issues
   - **Technical Issues** (13 patterns, MEDIUM priority): login problems, platform failures, access issues
   - **Negative Language** (24 patterns, VARIABLE priority): specific negative words in English and Hindi, sarcasm

### 2. Advanced Context Analysis

Goes beyond simple pattern matching to understand message context:
   - **Word Proximity**: Detects problem words near emotion words within 10-word windows
   - **Negative Intensifiers**: "very frustrated", "extremely disappointed", "bahut pareshan"
   - **Contextual Negations**: "not good", "no help", "nahi achha"
   - **Problem + Help Combinations**: "issue" + "please help", "dikkat" + "madad"
   - **Repeated Themes**: Same negative word appearing multiple times
   - **Multiple Questions**: 2+ question marks indicating confusion/frustration
   - **Urgent Language**: "asap help", "urgent issue", "jaldi madad"
   - **Communication Failures**: "no response", "haven't heard", "koi nahi mila"
   - **Time Frustration**: "still waiting", "days no reply", "kab tak"
   - **Consequence Statements**: "affecting career", "wasting money", "regret joining"

Context analysis assigns a score (0-10+). A score of 2 or higher flags the message as negative.

### 3. Real-World Examples

**sentimentManual.md** - 2223+ Real Negative Examples
   - Contains actual negative feedback messages from real users
   - **All messages in sentimentManual.md are treated as NEGATIVE examples**
   - The bot has learned patterns from these examples and integrated them into its analysis
   - Includes refund requests, support failures, technical issues, escalations, and more

### How It Works

1. Check if message is a coding/positive question (exclusion patterns)
2. Run pattern matching across all 158 patterns
3. If no patterns match, perform context analysis
4. Combine results: negative if ANY pattern matches OR context score >= 2
5. Messages flagged as "negative" if they meet criteria, otherwise "neutral"

### Multi-language Support
- English: Full support with native patterns
- Hindi/Hinglish: Roman script support for common phrases

**For detailed documentation**, see [SENTIMENT_PATTERNS.md](SENTIMENT_PATTERNS.md)

## Troubleshooting

### Bot is not receiving messages
- Ensure MESSAGE CONTENT INTENT is enabled in Discord Developer Portal
- Check that the bot has "Read Messages/View Channels" permission

### Google Sheets errors
- Verify `credentials.json` is in the correct location
- Ensure the service account email has "Editor" access to your Google Sheet
- Check that both Google Sheets API and Google Drive API are enabled

### Negative messages not posting
- Verify a channel named `discord_negative_ticket` exists in your server
- Check bot has "Send Messages" and "Embed Links" permissions in that channel
- Review logs in `discord_bot.log` for error messages

## Logs

The bot creates a log file `discord_bot.log` with detailed information about:
- Bot startup and connection
- Message processing
- Sentiment analysis results
- Google Sheets operations
- Errors and warnings

## Security Notes

**CRITICAL SECURITY REQUIREMENTS:**

- **NEVER** commit `.env` or `credentials.json` to version control (already in `.gitignore`)
- **NEVER** share your Discord bot token publicly or commit it to any file
- **IMMEDIATELY REGENERATE** your bot token if it's ever exposed
- Keep your bot token secret and only store it in the `.env` file
- Only share your Google Sheet with the service account email
- Regularly rotate credentials if compromised
- If you accidentally expose a token:
  1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
  2. Select your application
  3. Go to "Bot" section
  4. Click "Reset Token" immediately
  5. Update your `.env` file with the new token

## Support

For issues or questions:
1. Check the `discord_bot.log` file for error details
2. Verify all setup steps were completed correctly
3. Ensure all required permissions are granted

## License

This project is for internal use. Modify as needed for your requirements.
