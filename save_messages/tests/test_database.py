# tests/test_database.py

import unittest
from save_messages.database import Database
from save_messages.config import DATABASE_CONFIG
import psycopg2

DB_NAME = DATABASE_CONFIG.get("dbname")
USER = DATABASE_CONFIG.get("user")
PASSWORD = DATABASE_CONFIG.get("password")
HOST = DATABASE_CONFIG.get("host")
PORT = DATABASE_CONFIG.get("port")

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up the database connection and create test tables."""
        self.db = Database(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT)
        self.db.create_tables()  # Ensure tables are created before each test

    def tearDown(self):
        """Clean up by dropping the test tables after each test."""
        with self.db._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS MessageReaction;")
                cur.execute("DROP TABLE IF EXISTS Messages;")

    def test_connection(self):
        """Test that a connection to the database can be established."""
        connection = self.db._get_connection()
        self.assertIsNotNone(connection)
        connection.close()

    def test_create_tables(self):
        """Test that the tables are created in the database."""
        with self.db._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT to_regclass('public.Messages');")
                messages_table = cur.fetchone()[0]
                cur.execute("SELECT to_regclass('public.MessageReaction');")
                reactions_table = cur.fetchone()[0]
                self.assertIsNotNone(messages_table, "Messages table was not created.")
                self.assertIsNotNone(reactions_table, "MessageReaction table was not created.")

    def test_insert_message(self):
        """Test that a message can be inserted into the Messages table."""
        message_data = {
            'userId': 'U12345',
            'userName': 'John Doe',
            'channelId': 'C12345',
            'channelName': 'general',
            'messageText': 'Hello, world!',
            'timestamp': '2024-12-19 04:20:33',
            'parentMessageTimestamp': None
        }
        with self.db._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Messages (userId, userName, channelId, channelName, messageText, timestamp, parentMessageTimestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (message_data['userId'], message_data['userName'], message_data['channelId'],
                      message_data['channelName'], message_data['messageText'],
                      message_data['timestamp'], message_data['parentMessageTimestamp']))
                conn.commit()

                # Verify that the message was inserted
                cur.execute("SELECT * FROM Messages WHERE userId = %s;", (message_data['userId'],))
                result = cur.fetchone()
                self.assertIsNotNone(result)
                self.assertEqual(result[1], message_data['userId'])
                self.assertEqual(result[2], message_data['userName'])
                self.assertEqual(result[3], message_data['channelId'])
                self.assertEqual(result[4], message_data['channelName'])
                self.assertEqual(result[5], message_data['messageText'])

    def test_retrieve_message(self):
        """Test that a message can be retrieved from the Messages table."""
        message_data = {
            'userId': 'U12345',
            'userName': 'John Doe',
            'channelId': 'C12345',
            'channelName': 'general',
            'messageText': 'Hello, world!',
            'timestamp': '2024-12-19 04:20:33',
            'parentMessageTimestamp': None
        }
        # Insert a message first
        self.test_insert_message()

        with self.db._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM Messages WHERE userId = %s;", (message_data['userId'],))
                result = cur.fetchone()
                self.assertIsNotNone(result)
                self.assertEqual(result[1], message_data['userId'])
                self.assertEqual(result[2], message_data['userName'])
                self.assertEqual(result[3], message_data['channelId'])
                self.assertEqual(result[4], message_data['channelName'])
                self.assertEqual(result[5], message_data['messageText'])

if __name__ == '__main__':
    unittest.main()