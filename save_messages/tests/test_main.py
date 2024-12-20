import unittest
from unittest.mock import patch, MagicMock
import json
import datetime
import sys
import os

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, message, handle_reaction, get_channel_name, change_timestamp_format
from database import Database

class TestMainApp(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Mock the database configuration
        self.db_config_patcher = patch('main.DATABASE_CONFIG', {
            "slack_signing_secret": "test_secret",
            "slack_token": "test_token",
            "dbname": "test_db",
            "user": "test_user",
            "password": "test_password",
            "host": "localhost",
            "port": 5432
        })
        self.db_config_patcher.start()
        
        # Mock the host configuration
        self.host_config_patcher = patch('main.HOST_CONFIG', {
            "host": "0.0.0.0",
            "port": 5000,
            "debug": True
        })
        self.host_config_patcher.start()

    def tearDown(self):
        """Clean up after each test"""
        self.db_config_patcher.stop()
        self.host_config_patcher.stop()

    def test_change_timestamp_format(self):
        """Test timestamp conversion function"""
        test_timestamp = "1609459200.000000"  # 2021-01-01 00:00:00 UTC
        expected_datetime = datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        result = change_timestamp_format(test_timestamp)
        self.assertEqual(result, expected_datetime)

    @patch('main.client')
    def test_get_channel_name(self, mock_client):
        """Test channel name retrieval"""
        mock_client.conversations_info.return_value = {
            "channel": {"name": "test-channel"}
        }
        result = get_channel_name("C123456")
        self.assertEqual(result, "test-channel")
        mock_client.conversations_info.assert_called_with(channel="C123456")

    @patch('main.client')
    @patch('main.db')
    def test_message_handler(self, mock_db, mock_client):
        """Test message event handling"""
        test_payload = {
            "event": {
                "type": "message",
                "user": "U123456",
                "channel": "C123456",
                "text": "Test message",
                "ts": "1609459200.000000"
            }
        }
        
        mock_client.users_info.return_value = {
            "user": {"real_name": "Test User"}
        }
        mock_client.conversations_info.return_value = {
            "channel": {"name": "test-channel"}
        }
        
        message(test_payload)
        
        mock_db.insert_message.assert_called_once()
        call_args = mock_db.insert_message.call_args[0]
        self.assertEqual(call_args[0], "U123456")  # user_id
        self.assertEqual(call_args[1], "Test User")  # real_name
        self.assertEqual(call_args[2], "C123456")  # channel_id
        self.assertEqual(call_args[3], "test-channel")  # channel_name
        self.assertEqual(call_args[4], "Test message")  # text

    @patch('main.client')
    @patch('main.db')
    def test_reaction_handler(self, mock_db, mock_client):
        """Test reaction event handling"""
        test_payload = {
            "event": {
                "type": "reaction_added",
                "user": "U123456",
                "reaction": "thumbsup",
                "item": {
                    "type": "message",
                    "channel": "C123456",
                    "ts": "1609459200.000000"
                },
                "event_ts": "1609459201.000000"
            }
        }
        
        mock_client.users_info.return_value = {
            "user": {"real_name": "Test User"}
        }
        mock_db.get_message_id.return_value = 1
        mock_db.get_reaction_count.return_value = None
        
        handle_reaction(test_payload)
        
        mock_db.insert_message_reaction.assert_called_once()
        call_args = mock_db.insert_message_reaction.call_args[0]
        self.assertEqual(call_args[0], 1)  # message_id
        self.assertEqual(call_args[1], "U123456")  # user
        self.assertEqual(call_args[2], "Test User")  # real_name
        self.assertEqual(call_args[3], "thumbsup")  # reaction_name

    @patch('main.client')
    @patch('main.db')
    def test_reaction_handler_existing_reaction(self, mock_db, mock_client):
        """Test reaction event handling with existing reaction"""
        test_payload = {
            "event": {
                "type": "reaction_added",
                "user": "U123456",
                "reaction": "thumbsup",
                "item": {
                    "type": "message",
                    "channel": "C123456",
                    "ts": "1609459200.000000"
                },
                "event_ts": "1609459201.000000"
            }
        }
        
        mock_client.users_info.return_value = {
            "user": {"real_name": "Test User"}
        }
        mock_db.get_message_id.return_value = 1
        mock_db.get_reaction_count.return_value = 1
        
        handle_reaction(test_payload)
        
        mock_db.update_reaction_count.assert_called_once_with(1, "thumbsup", 2)

    def test_message_handler_error(self):
        """Test message handler with invalid payload"""
        test_payload = {
            "event": {
                "type": "message",
                "channel": "C123456",  # Missing user field
                "text": "Test message",
                "ts": "1609459200.000000"
            }
        }
        
        # This should not raise an exception
        message(test_payload)

if __name__ == '__main__':
    unittest.main()