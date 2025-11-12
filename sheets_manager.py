"""
Google Sheets Manager Module
Handles all Google Sheets operations for logging Discord messages
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import List, Dict
import logging
import json
import os


class SheetsManager:
    """Manages Google Sheets operations for Discord message logging."""

    def __init__(self, credentials_file: str, spreadsheet_name: str):
        """
        Initialize Google Sheets manager.

        Args:
            credentials_file: Path to Google service account JSON credentials
            spreadsheet_name: Name of the Google Sheet to use
        """
        self.logger = logging.getLogger(__name__)

        # Define the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        try:
            # Check if credentials_file is a JSON string or file path
            # First check if GOOGLE_SHEETS_CREDENTIALS_JSON env variable exists
            json_creds = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')

            if json_creds:
                # Use JSON from environment variable
                self.logger.info("Loading credentials from GOOGLE_SHEETS_CREDENTIALS_JSON environment variable")
                try:
                    creds_dict = json.loads(json_creds)
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON in GOOGLE_SHEETS_CREDENTIALS_JSON: {e}")
                    raise
            elif os.path.isfile(credentials_file):
                # Use file path (traditional method)
                self.logger.info(f"Loading credentials from file: {credentials_file}")
                creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
            else:
                # Try to parse credentials_file as JSON string (fallback)
                self.logger.info("Attempting to parse credentials as JSON string")
                try:
                    creds_dict = json.loads(credentials_file)
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                except json.JSONDecodeError:
                    raise FileNotFoundError(
                        f"Credentials file not found: {credentials_file}. "
                        f"Please provide either a valid file path or set GOOGLE_SHEETS_CREDENTIALS_JSON environment variable."
                    )

            # Authenticate and connect
            self.client = gspread.authorize(creds)

            # Open or create the spreadsheet
            try:
                self.spreadsheet = self.client.open(spreadsheet_name)
                self.worksheet = self.spreadsheet.sheet1
            except gspread.SpreadsheetNotFound:
                self.logger.info(f"Creating new spreadsheet: {spreadsheet_name}")
                self.spreadsheet = self.client.create(spreadsheet_name)
                self.worksheet = self.spreadsheet.sheet1
                self._setup_headers()

            # Ensure headers exist
            if self.worksheet.row_values(1) == []:
                self._setup_headers()

            self.logger.info(f"Connected to Google Sheet: {spreadsheet_name}")

        except Exception as e:
            self.logger.error(f"Failed to initialize Google Sheets: {e}")
            raise

    def _setup_headers(self):
        """Set up column headers in the worksheet."""
        headers = [
            'timestamp',
            'date',
            'message_id',
            'message_body',
            'sentiment',
            'channel_id',
            'channel_name',
            'server_name',
            'discord_userName'
        ]
        self.worksheet.update('A1:I1', [headers])
        self.logger.info("Headers set up in worksheet")

    def log_message(self, message_data: Dict[str, str]) -> bool:
        """
        Log a single message to Google Sheets.

        Args:
            message_data: Dictionary containing message data with keys:
                - timestamp
                - date
                - message_id
                - message_body
                - sentiment
                - channel_id
                - channel_name
                - server_name
                - discord_userName

        Returns:
            True if successful, False otherwise
        """
        try:
            row = [
                message_data.get('timestamp', ''),
                message_data.get('date', ''),
                message_data.get('message_id', ''),
                message_data.get('message_body', ''),
                message_data.get('sentiment', ''),
                message_data.get('channel_id', ''),
                message_data.get('channel_name', ''),
                message_data.get('server_name', ''),
                message_data.get('discord_userName', '')
            ]

            self.worksheet.append_row(row, value_input_option='RAW')
            self.logger.debug(f"Logged message {message_data.get('message_id')} to sheet")
            return True

        except Exception as e:
            self.logger.error(f"Failed to log message to sheet: {e}")
            return False

    def log_messages_batch(self, messages: List[Dict[str, str]]) -> bool:
        """
        Log multiple messages to Google Sheets in a batch.

        Args:
            messages: List of message data dictionaries

        Returns:
            True if successful, False otherwise
        """
        try:
            rows = []
            for message_data in messages:
                row = [
                    message_data.get('timestamp', ''),
                    message_data.get('date', ''),
                    message_data.get('message_id', ''),
                    message_data.get('message_body', ''),
                    message_data.get('sentiment', ''),
                    message_data.get('channel_id', ''),
                    message_data.get('channel_name', ''),
                    message_data.get('server_name', ''),
                    message_data.get('discord_userName', '')
                ]
                rows.append(row)

            if rows:
                self.worksheet.append_rows(rows, value_input_option='RAW')
                self.logger.info(f"Logged {len(rows)} messages to sheet")
            return True

        except Exception as e:
            self.logger.error(f"Failed to batch log messages to sheet: {e}")
            return False

    def get_last_message_id(self) -> str:
        """
        Get the last logged message ID from the sheet.

        Returns:
            Last message ID or empty string if none found
        """
        try:
            # Get all message IDs (column C)
            message_ids = self.worksheet.col_values(3)
            if len(message_ids) > 1:  # Skip header
                return message_ids[-1]
            return ''
        except Exception as e:
            self.logger.error(f"Failed to get last message ID: {e}")
            return ''
