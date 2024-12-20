import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "slack_token": os.getenv("SLACK_API_TOKEN"),
    "slack_signing_secret": os.getenv("SIGNING_SECRET")
}

HOST_CONFIG = {
    "host": os.getenv("HOST", "localhost"),
    "port": os.getenv("HOST_PORT", "5000"),
    "debug": os.getenv("DEBUG", False)
}