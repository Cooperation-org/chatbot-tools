# Chatbot Message Management

## Overview
This project is a chatbot message management system that integrates with Slack. It allows users to store and manage messages and reactions in a PostgreSQL database. The application is built using Flask and utilizes the Slack SDK for handling events from Slack.

The aim of the project is to store chats and communication on WhatstCookin slack channel to provide a mentor to developer on projects going on and information on WhatsCookin.

## Project Structure
chatbot-tools/ 
    └── save-messages/ 
        ├── config.py 
        ├── database.py 
        ├── main.py 
        ├── requirements.txt 
        ├── schema.py 
        └── wsgi.py


## Installation

### Prerequisites
- Python 3.7 or higher
- PostgreSQL database
- Slack account with API access

### Setup
1. Clone the repository:
```bash
git clone https://github.com/Cooperation-org/chatbot-tools.git
cd chatbot-tools
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install the required packages:
```bash
pip install -r save-messages/requirements.txt
```

4. Create a .env file in the save-messages directory with the following content:

```env
DATABASE=<your_database_name>
DB_USER=<your_database_user>
DB_PASSWORD=<your_database_password>
HOST=localhost
PORT=5432
SLACK_API_TOKEN=<your_slack_api_token>
SIGNING_SECRET=<your_slack_signing_secret>
```

### Usage
1. Start the application:
```bash
python save-messages/main.py
```

2. The application will run on `http://localhost:5000`

3. Configure your Slack app to send events to the endpoint provided by your Flask application.

### API Endpoints

- Message Handling: The application listens for messages and reactions from Slack and stores them in the database.

### Configuration
- The application uses a .env file to store sensitive information such as database credentials and Slack API tokens
- The database is created and populated with tables using the [database.py](save-messages/database.py) script
- The application uses a Flask development server to run on http://localhost:5000
- Database connection details and Slack API credentials must be provided in the .env file.

For further complaints, enquires or contact
`ping Orjiene Kenechukwu or spiderman on slack`