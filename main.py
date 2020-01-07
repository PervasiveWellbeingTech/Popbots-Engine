#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 20:27:40 2020

@author: hugo
"""

import sqlite3
import database_operations as dbop

connection = sqlite3.connect("database.sqlite3")

#dbop.add("users", ("HungryBot", None, 2), connection)
#dbop.add("conversations", (1,), connection)
#dbop.add("messages", (1, 4, ), connection)

default_bot_id = 4
default_bot = dbop.get_by("id", "users", default_bot_id, connection)[0]


def is_stressor(message):
    # Some process
    return int(False)


def get_variant(message):
    # Some process
    return 0


def new_conversation(user, bot=default_bot):
    print(f"\n##### New conversation #####")
    user_id, user_name, user_subject_id, user_category_id = user
    bot_id, bot_name, bot_subject_id, bot_category_id = bot
    conversation_id = dbop.add("conversations", (user_id,), connection)

    while True:
        print("Write a message (q to leave):")
        content = input()
        
        if content == "q":
            break
        else:
            content_id = dbop.add("contents", (content, user_id), connection)
            dbop.add("messages", (
                        user_id, bot_id, content_id, conversation_id,
                        0, is_stressor(content), get_variant(content)
                        ),
                     connection)
            print(f"{user_name}: {content}")


user_id = 1
user = dbop.get_by("id", "users", user_id, connection)[0]

if user:
    user_id, user_name, user_subject_id, user_category_id = user
    print(f"##### {user_name} conversations #####")
    
    while True:
        conversations = dbop.get_by("user_id", "conversations", user_id, connection)
        if conversations:
            for conversation in conversations:
                print(f"  - conv. n°{conversation[0]}")
        else:
            print("No conversation yet")
        print("\n- To see a conversation, type the conversation number")
        print("- To add a conversation, type +")
        print("- To quit, type q")
        command = input()
        
        if command == "q":
            break
        elif command == "+":
            new_conversation(user)
        else:
            conversation_id = command
            messages = dbop.get_by("conversation_id", "messages", conversation_id, connection)
            
            if not messages:
                print("No message in this conversation")
            
            for message in messages:
                # Can be optimized
                sender_id, content_id = message[1], message[3]
                sender_name = dbop.get_by("id", "users", sender_id, connection)[0][1]
                message_content = dbop.get_by("id", "contents", content_id, connection)[0][1]
                print(f"{sender_name}: {message_content}")
            print()
    
else:
    print("WARNING: Unknown user")

connection.commit()
connection.close()
