# database.py

import psycopg2
from psycopg2 import sql
from schema import (CREATE_TABLE_MESSAGE_REACTION, CREATE_TABLE_MESSAGES,)

class Database:
    def __init__(self, dbname, user, password, host, port):
        self.dbname= dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def _get_connection(self):
        return psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host, port=self.port)

    def create_tables(self):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                for query in [CREATE_TABLE_MESSAGES, CREATE_TABLE_MESSAGE_REACTION]:
                    cur.execute(query)

    def insert_message(self, user_id, user_name, channel_id, channel_name, text, timestamp, parent_message_ts):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                insert_query = """INSERT INTO Messages (userId, userName, channelId, channelName, messageText, timestamp, parentMessageTimestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cur.executemany(insert_query, [(user_id, user_name, channel_id, channel_name, text, timestamp, parent_message_ts)])  # Ensure data is a list of tuples
                conn.commit()

    def insert_message_reaction(self, message_id, user, user_name, reaction_name, reaction_ts, count):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                insert_query = """INSERT INTO MessageReaction (messageId, userId, userName, reactionName, reactionTs, count) VALUES (%s, %s, %s, %s, %s, %s)"""
                cur.executemany(insert_query, [(message_id, user, user_name, reaction_name, reaction_ts, count)])
                conn.commit()

    def update_reaction_count(self, message_ts, reaction_name, new_count):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                update_query = """UPDATE MessageReaction SET count = %s WHERE messageId = %s AND reactionName = %s"""
                cur.execute(update_query, [(new_count, message_ts, reaction_name)])
                conn.commit()

    def get_reaction_count(self, message_ts, reaction_name):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                select_query = """SELECT count FROM MessageReaction WHERE messageId = %s AND reactionName = %s"""
                cur.execute(select_query, (message_ts, reaction_name))
                result = cur.fetchone()
                if result:
                    return result[0]  # Return the count value if found
                else:
                    return None
    
    def get_message_id(self, message_timestamp):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                query = "SELECT messageId FROM Messages WHERE timestamp = %s"
                cur.execute(query, (message_timestamp,))
                result = cur.fetchone()
                if result:
                    return result[0]  # Return the first column (messageId) from the result
                else:
                    return None