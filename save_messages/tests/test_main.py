# tests/test_main.py

import unittest
from save_messages.main import app
from save_messages.config import DATABASE_CONFIG
import time
import json
import hmac
import hashlib

SLACK_SIGNING_SECRET = DATABASE_CONFIG.get("slack_signing_secret")
# SLACK_TOKEN = DATABASE_CONFIG.get("slack_token")
def generate_slack_signature(secret, timestamp, body):
    """Generate a Slack signature for testing."""
    basestring = f"v0:{timestamp}:{body}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), basestring, hashlib.sha256).hexdigest()
    return f"v0={signature}"

class TestMainApp(unittest.TestCase):
    def setUp(self):
        """Set up the Flask test client."""
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'OK')

    def test_post_message(self):
        """Test posting a message to the /messages endpoint."""
        message_data = {
            "userId": "U12345",
            "userName": "John Doe",
            "channelId": "C12345",
            "channelName": "general",
            "messageText": "Hello, world!",
            "timestamp": str(int(time.time())),
            "parentMessageTimestamp": None
        }
        response = self.app.post('/messages', data=json.dumps(message_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('messageId', response.json)

    def test_post_invalid_message(self):
        """Test posting an invalid message."""
        invalid_message_data = {
            "userId": "U12345",
            # Missing userName, channelId, etc.
        }
        response = self.app.post('/messages', data=json.dumps(invalid_message_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)  # Assuming the endpoint returns 400 for bad requests

    def test_slack_event_handling(self):
        """Test handling a Slack event."""
        slack_event = {
            "type": "event_callback",
            "event": {
                "type": "message",
                "user": "U12345",
                "text": "Hello, world!",
                "ts": str(int(time.time())),
                "channel": "C12345"
            }
        }
        body = json.dumps(slack_event)
        timestamp = str(int(time.time()))
        signature = generate_slack_signature(SLACK_SIGNING_SECRET, timestamp, body)

        headers = {
            "X-Slack-Request-Timestamp": timestamp,
            "X-Slack-Signature": signature,
        }

        response = self.app.post('/slack/events', data=body, content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)  # Assuming successful handling returns 200

    def test_slack_event_invalid(self):
        """Test handling an invalid Slack event."""
        invalid_slack_event = {
            "type": "event_callback",
            # Missing event details
        }
        body = json.dumps(invalid_slack_event)
        timestamp = str(int(time.time()))
        signature = generate_slack_signature(SLACK_SIGNING_SECRET, timestamp, body)

        headers = {
            "X-Slack-Request-Timestamp": timestamp,
            "X-Slack-Signature": signature,
        }

        response = self.app.post('/slack/events', data=body, content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 400)  # Assuming the endpoint returns 400 for bad requests

if __name__ == '__main__':
    unittest.main()