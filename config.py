import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    "dbname": os.getenv("DATABASE"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("HOST", "localhost"),
    "port": os.getenv("PORT", "5432"),
    "slack_token": os.getenv("SLACK_API_TOKEN"),
    "slack_signing_secret": os.getenv("SIGNING_SECRET")
}