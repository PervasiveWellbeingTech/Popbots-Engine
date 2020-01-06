#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 22:35:47 2020

@author: hugo
"""

import sqlite3

connection = sqlite3.connect("database.sqlite3")
cursor = connection.cursor()

create_users_table = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY autoincrement,
    name TEXT NOT NULL,
    subject_id INTEGER,
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
