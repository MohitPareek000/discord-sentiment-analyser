"""
Discord Sentiment Analysis Bot
Monitors all messages across servers, analyzes sentiment, logs to Google Sheets,
and posts negative messages to a specific channel.
"""

import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import logging
import os
from typing import Optional
from dotenv import load_dotenv
from sentiment_analyzer import SentimentAnalyzer
from sheets_manager import SheetsManager

# Load environment variables from .env file
load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SentimentBot(commands.Bot):
    """Discord bot that monitors messages and analyzes sentiment."""

    def __init__(self, sheets_credentials: str, spreadsheet_name: str,
                 negative_channel_name: str = "discord_negative_ticket",
                 admin_server_name: str = None):
        """
        Initialize the sentiment bot.

        Args:
            sheets_credentials: Path to Google Sheets credentials JSON
            spreadsheet_name: Name of the Google Sheet
            negative_channel_name: Name of channel to post negative messages
            admin_server_name: Name of admin server for centralized posting (optional)
        """
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        intents.members = True

        super().__init__(command_prefix='!', intents=intents)

        # Initialize components
        self.sentiment_analyzer = SentimentAnalyzer('sentiment.md')
        logger.info(f"Sentiment Analyzer: {self.sentiment_analyzer.get_sentiment_rules_info()}")
        self.sheets_manager = SheetsManager(sheets_credentials, spreadsheet_name)
        self.negative_channel_name = negative_channel_name
        self.admin_server_name = admin_server_name  # Centralized admin server
        self.negative_channels = {}  # guild_id: channel mapping
        self.central_negative_channel = None  # Central channel in admin server
        self.processed_messages = set()  # Track processed message IDs to prevent duplicates

        logger.info("SentimentBot initialized")

    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Bot setup hook called")

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'Logged in as {self.user.name} ({self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} servers')

        # Find negative channels in all guilds
        await self._find_negative_channels()

        logger.info('Bot is ready!')

    async def _find_negative_channels(self):
        """Find and cache the negative ticket channels in all guilds."""
        # If admin server is specified, find the central channel
        if self.admin_server_name:
            admin_guild = discord.utils.get(self.guilds, name=self.admin_server_name)
            if admin_guild:
                central_channel = discord.utils.get(admin_guild.text_channels, name=self.negative_channel_name)
                if central_channel:
                    self.central_negative_channel = central_channel
                    logger.info(f"✓ Central negative channel found in admin server '{self.admin_server_name}': {central_channel.name}")
                    logger.info("All negative messages from all servers will be posted to this central channel")
                else:
                    logger.error(f"Central negative channel '{self.negative_channel_name}' not found in admin server '{self.admin_server_name}'")
            else:
                logger.error(f"Admin server '{self.admin_server_name}' not found")

        # If no central channel, find channels in each guild
        if not self.central_negative_channel:
            for guild in self.guilds:
                channel = discord.utils.get(guild.text_channels, name=self.negative_channel_name)
                if channel:
                    self.negative_channels[guild.id] = channel
                    logger.info(f"Found negative channel in {guild.name}: {channel.name}")
                else:
                    logger.warning(f"Negative channel '{self.negative_channel_name}' not found in {guild.name}")

    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild."""
        logger.info(f"Joined new guild: {guild.name} ({guild.id})")
        # Look for negative channel
        channel = discord.utils.get(guild.text_channels, name=self.negative_channel_name)
        if channel:
            self.negative_channels[guild.id] = channel
            logger.info(f"Found negative channel in {guild.name}")

    async def on_message(self, message):
        """
        Called when a message is sent in any channel the bot can see.

        Args:
            message: Discord message object
        """
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        # Ignore DMs
        if not message.guild:
            return

        # Process the message
        await self._process_message(message)

        # Process commands
        await self.process_commands(message)

    async def _process_message(self, message):
        """
        Process a message: analyze sentiment, log to sheets, and post if negative.

        Args:
            message: Discord message object
        """
        try:
            # Check if we've already processed this message (prevent duplicates)
            if message.id in self.processed_messages:
                logger.debug(f"Skipping already processed message {message.id}")
                return

            # Add to processed set
            self.processed_messages.add(message.id)

            # Clean up old processed messages (keep only last 1000)
            if len(self.processed_messages) > 1000:
                # Remove oldest half
                messages_to_remove = list(self.processed_messages)[:500]
                for msg_id in messages_to_remove:
                    self.processed_messages.discard(msg_id)
            # Extract message data
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            date = message.created_at.strftime('%Y-%m-%d')
            message_id = str(message.id)
            message_body = message.content
            channel_id = str(message.channel.id)
            channel_name = message.channel.name
            server_name = message.guild.name
            # Use the actual Discord username (the @username format)
            # For new username system: use name (which is the @username)
            # For old system: use name#discriminator
            if message.author.discriminator and message.author.discriminator != "0":
                discord_username = f"{message.author.name}#{message.author.discriminator}"
            else:
                # New username system - just use the name (which is the @username)
                discord_username = message.author.name

            # Analyze sentiment
            sentiment = self.sentiment_analyzer.analyze(message_body)

            # Prepare data for Google Sheets
            message_data = {
                'timestamp': timestamp,
                'date': date,
                'message_id': message_id,
                'message_body': message_body,
                'sentiment': sentiment,
                'channel_id': channel_id,
                'channel_name': channel_name,
                'server_name': server_name,
                'discord_userName': discord_username
            }

            # Log to Google Sheets
            success = self.sheets_manager.log_message(message_data)
            if success:
                logger.debug(f"Logged message {message_id} to Google Sheets")
            else:
                logger.error(f"Failed to log message {message_id} to Google Sheets")

            # If sentiment is negative, post to negative channel
            if sentiment == 'negative':
                await self._post_negative_message(message, message_data)

        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}", exc_info=True)

    async def _post_negative_message(self, original_message, message_data):
        """
        Post negative sentiment message to the designated channel.
        Uses central admin channel if configured, otherwise posts to server's own channel.

        Args:
            original_message: Original Discord message object
            message_data: Processed message data dictionary
        """
        try:
            # Use central channel if available, otherwise use guild-specific channel
            if self.central_negative_channel:
                negative_channel = self.central_negative_channel
            else:
                # Get the negative channel for this guild
                negative_channel = self.negative_channels.get(original_message.guild.id)

                if not negative_channel:
                    logger.warning(
                        f"No negative channel found for guild {original_message.guild.name}. "
                        f"Attempting to find channel '{self.negative_channel_name}'..."
                    )
                    # Try to find it again
                    channel = discord.utils.get(
                        original_message.guild.text_channels,
                        name=self.negative_channel_name
                    )
                    if channel:
                        self.negative_channels[original_message.guild.id] = channel
                        negative_channel = channel
                        logger.info(f"Found negative channel in {original_message.guild.name}")
                    else:
                        logger.error(
                            f"Channel '{self.negative_channel_name}' does not exist in "
                            f"{original_message.guild.name}. Please create it first."
                        )
                        return

            # Create embed for better formatting
            embed = discord.Embed(
                title="🚨 Negative Sentiment Detected",
                description=message_data['message_body'][:4000],  # Discord limit
                color=discord.Color.red(),
                timestamp=original_message.created_at
            )

            # Add fields
            embed.add_field(name="User", value=message_data['discord_userName'], inline=True)
            embed.add_field(name="Server", value=message_data['server_name'], inline=True)
            embed.add_field(name="Channel", value=f"#{message_data['channel_name']}", inline=True)
            embed.add_field(name="Message ID", value=message_data['message_id'], inline=True)
            embed.add_field(name="Channel ID", value=message_data['channel_id'], inline=True)
            embed.add_field(name="Timestamp", value=message_data['timestamp'], inline=True)

            # Add link to original message
            message_link = f"https://discord.com/channels/{original_message.guild.id}/{original_message.channel.id}/{original_message.id}"
            embed.add_field(name="Original Message", value=f"[Jump to message]({message_link})", inline=False)

            # Add matched patterns for debugging
            matched_patterns = self.sentiment_analyzer.get_matched_patterns(message_data['message_body'])
            if matched_patterns:
                embed.add_field(
                    name="Matched Patterns",
                    value=", ".join(matched_patterns),
                    inline=False
                )

            # Send to negative channel
            await negative_channel.send(embed=embed)
            logger.info(
                f"Posted negative message from {message_data['discord_userName']} "
                f"in {message_data['server_name']} to negative channel"
            )

        except discord.Forbidden:
            logger.error(f"No permission to send to channel {negative_channel.name}")
        except Exception as e:
            logger.error(f"Error posting negative message: {e}", exc_info=True)


def main():
    """Main function to run the bot."""
    # Get configuration from environment variables
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'credentials.json')
    SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'Discord Messages Log')
    NEGATIVE_CHANNEL_NAME = os.getenv('NEGATIVE_CHANNEL_NAME', 'discord_negative_ticket')
    ADMIN_SERVER_NAME = os.getenv('ADMIN_SERVER_NAME', None)  # Optional centralized admin server

    if not BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN environment variable not set!")
        return

    # Create and run bot
    try:
        bot = SentimentBot(
            sheets_credentials=SHEETS_CREDENTIALS,
            spreadsheet_name=SPREADSHEET_NAME,
            negative_channel_name=NEGATIVE_CHANNEL_NAME,
            admin_server_name=ADMIN_SERVER_NAME
        )
        bot.run(BOT_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)


if __name__ == '__main__':
    main()
