CREATE_TABLE_MESSAGES = """
CREATE TABLE IF NOT EXISTS Messages (
    messageId SERIAL PRIMARY KEY,
    userId VARCHAR(100),
    userName VARCHAR(255),
    channelId VARCHAR(100),
    channelName VARCHAR(100),
    messageText TEXT,
    timestamp TIMESTAMP,
    parentMessageTimestamp TIMESTAMP
);
"""

CREATE_TABLE_MESSAGE_REACTION = """
    CREATE TABLE IF NOT EXISTS MessageReaction (
    messageReactionId SERIAL PRIMARY KEY,
    messageId INT,
    userId VARCHAR(100),
    userName VARCHAR(255),
    reactionName VARCHAR(100),
    reactionTs TIMESTAMP,
    count INT DEFAULT 0,
    FOREIGN KEY (messageId) REFERENCES Messages(messageId)
);
"""
