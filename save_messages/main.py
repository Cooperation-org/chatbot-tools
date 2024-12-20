from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask
from slackeventsapi import SlackEventAdapter
from database import Database
from config import DATABASE_CONFIG, HOST_CONFIG
import datetime

# Initialize Flask app
app = Flask(__name__)

SLACK_SIGNING_SECRET = DATABASE_CONFIG.get("slack_signing_secret")
SLACK_TOKEN = DATABASE_CONFIG.get("slack_token")
DB_NAME = DATABASE_CONFIG.get("dbname")
USER = DATABASE_CONFIG.get("user")
PASSWORD = DATABASE_CONFIG.get("password")
HOST = DATABASE_CONFIG.get("host")
PORT = DATABASE_CONFIG.get("port")


# Initialize Slack client
client = WebClient(token=SLACK_TOKEN)

# Initialize SlackEventAdapter
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

# Initialize database
db = Database(dbname=DB_NAME, user=USER,
              password=PASSWORD, host=HOST, port=PORT)

# Ensure database tables are created
try:
    db.create_tables()
    print("DB table successfully created")
except Exception as e:
    print(f"Error creating database tables: {e}")

@slack_events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')

    # Process only messages which have a user field (exclude bot messages)
    if "user" in event and not event.get('is_bot'):
        try:
            user_id = event.get('user')
            text = event.get('text')
            timestamp = change_timestamp_format(event.get('ts'))
            user_info = client.users_info(user=user_id)
            channel_name = get_channel_name(channel_id)
            try:
                parent_message_ts = event.get('thread_ts')
                parent_message_ts =change_timestamp_format(parent_message_ts)
            except:
                parent_message_ts = None

            message_data = (user_id, user_info["user"]["real_name"], channel_id, channel_name, text, timestamp, parent_message_ts)
            try:
                # Insert message
                db.insert_message(user_id, user_info["user"]["real_name"], channel_id, channel_name, text, timestamp, parent_message_ts)
                print(f'Succesfully saved')
            except Exception as e:
                print(f'Could not save. Error: {e}')
        except SlackApiError as e:
            print(f"Error fetching user info: {e}")

@slack_events_adapter.on("reaction_added")
def handle_reaction(payload):
    reaction = payload.get('event', {})
    user = reaction.get("user")
    reaction_name = reaction.get("reaction")
    item = reaction.get("item")
    reaction_ts = change_timestamp_format(reaction.get('event_ts'))
    
    try:
        if item["type"] == "message":
            message_ts = change_timestamp_format(item["ts"])
            # channel = item["channel"]
            user_info = client.users_info(user=user)

            # Fetch the message ID using the message timestamp
            message_id = db.get_message_id(message_ts)
            
            message_reaction_data = (message_id, user, user_info["user"]["real_name"], reaction_name, reaction_ts)
            existing_count = db.get_reaction_count(message_id, reaction_name)
            if existing_count is not None:
                # Increment the count
                new_count = existing_count + 1
                try:
                    db.update_reaction_count(message_id, reaction_name, new_count)
                    print(f'Succesfully updated')
                except Exception as e:
                    print(f'Could not save. Error: {e}')
            else:
                try:
                    db.insert_message_reaction(message_id, user, user_info["user"]["real_name"], reaction_name, reaction_ts, count=1)
                    print(f'Succesfully saved')
                except Exception as e:
                    print(f'Could not save. Error: {e}')
    except SlackApiError as e:
            print(f"Error fetching user info: {e}")

def get_channel_name(channel_id):
    try:
        response = client.conversations_info(channel=channel_id)
        return response["channel"]["name"]
    except SlackApiError as e:
        print(f"Error fetching channel name: {e}")
        return None

def change_timestamp_format(timestamp):
    """Convert timestamp to a datetime object"""
    dt_object = datetime.datetime.fromtimestamp(float(timestamp), datetime.timezone.utc)
    return dt_object

if __name__ == "__main__":
    app.run(host=HOST_CONFIG.get("host"), port=HOST_CONFIG.get("port"), debug=HOST_CONFIG.get("debug"))
