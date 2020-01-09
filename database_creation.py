#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 22:35:47 2020

@author: hugo
"""

import sqlite3
import database_operations as dbop
import bots_management as bot

connection = sqlite3.connect("database.sqlite3")
cursor = connection.cursor()

create_users_table = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY autoincrement,
    name TEXT NOT NULL,
    subject_id TEXT,
    category_id INTEGER NOT NULL)"""

create_conversations_table = """
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY autoincrement,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id))"""

create_messages_table = """
CREATE TABLE messages (
    id INTEGER PRIMARY KEY autoincrement,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content_id INTEGER NOT NULL,
    conversation_id INTEGER NOT NULL,
    message_index INTEGER NOT NULL,
    stressor BOOLEAN NOT NULL CHECK (stressor IN (0, 1)),
    variant INTEGER NOT NULL,
    FOREIGN KEY (sender_id) REFERENCES users (id),
    FOREIGN KEY (receiver_id) REFERENCES users (id),
    FOREIGN KEY (content_id) REFERENCES contents (id),
    FOREIGN KEY (conversation_id) REFERENCES conversations (id))"""

create_content_finders_table = """
CREATE TABLE content_finders (
    id INTEGER PRIMARY KEY autoincrement,
    message_index INTEGER NOT NULL,
    variant INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content_id INTEGER NOT NULL,
    next_message_index INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (content_id) REFERENCES contents (id))
"""

create_contents_table = """
CREATE TABLE contents (
    id INTEGER PRIMARY KEY autoincrement,
    text TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id))"""

create_message_content_links_table = """
CREATE TABLE message_content_links (
    id INTEGER PRIMARY KEY autoincrement,
    message_id INTEGER NOT NULL,
    content_id INTEGER NOT NULL,
    FOREIGN KEY (message_id) REFERENCES messages (id),
    FOREIGN KEY (content_id) REFERENCES contents (id))"""

cursor.execute(create_users_table)
cursor.execute(create_conversations_table)
cursor.execute(create_messages_table)
cursor.execute(create_content_finders_table)
cursor.execute(create_contents_table)
cursor.execute(create_message_content_links_table)
cursor.close()


# Fixtures
dbop.add("users", ("Bob", "A123", 1), connection)

# First bot with fake messages (just to check some functions)
bot_id = dbop.add("users", ("TestBot", None, 2), connection)

bot_messages = [
    ("Message 1 (variant 1)", 1, 1, 2, bot_id),
    ("Message 2 (variant 1)", 2, 1, 3, bot_id),
    ("Message 3 (variant 1)", 3, 1, 5, bot_id),
    ("Message 5 (variant 1)", 5, 1, 6, bot_id),
    ("Message 2 (variant 2)", 2, 2, 4, bot_id),
    ("Message 4 (variant 1)", 4, 1, 5, bot_id),
    ("Message 5 (variant 1)", 5, 1, 6, bot_id)
]

for content, index, variant, next_index, bot_id in bot_messages:
    bot.add_bot_message(content, index, variant, next_index, bot_id, connection)
    
# Second bot, introduction bot (before the conversation)
bot_id = dbop.add("users", ("IntroBot", None, 2), connection)

bot_messages = [
    ("Hi {}, what is stressing you out ?", 1, 1, 2, bot_id)
]

for content, index, variant, next_index, bot_id in bot_messages:
    bot.add_bot_message(content, index, variant, next_index, bot_id, connection)

# Third bot, standard bot
bot_id = dbop.add("users", ("HungryBot", None, 2), connection)

bot_messages = [
    ("Hello, do you want to eat ?", 1, 1, 2, bot_id),
    ("You should take rice", 2, 1, 3, bot_id),
    ("You should take french fries", 2, 2, 3, bot_id),
    ("No problem, bon appétit!", 3, 1, 4, bot_id)
]

for content, index, variant, next_index, bot_id in bot_messages:
    bot.add_bot_message(content, index, variant, next_index, bot_id, connection)
    
connection.commit()
connection.close()













