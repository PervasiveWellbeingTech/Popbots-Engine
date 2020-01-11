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

default_bot_id = 3
default_bot = dbop.get_by(connection, "users", ("id", default_bot_id))[0]


def is_stressor(message):
    # Some process
    return int(False)


def get_variant(message, index):
    # Some process
    if "french" in message:
        return 2
    elif "hungry" in message:
        return 1
    elif "sport" in message:
        return 2
    return 1


def new_message(user_name, user_id, bot_id, content, conversation_id, index):
    content_id = dbop.add("contents", (content, user_id, None), connection)
    dbop.add("messages", (
                user_id, bot_id, content_id, conversation_id,
                index, is_stressor(content), 0),
             connection)
    print(f"{user_name}: {content}")
    

def new_bot_message(bot_name, bot_id, user_id, content_id, conversation_id, index, variant):
    dbop.add("messages", (
                bot_id, user_id, content_id, conversation_id,
                index, 0, variant),
             connection)
    content = dbop.get_by(connection, "contents", ("id", content_id))[0][1]
    print(f"{bot_name}: {content}")


def new_conversation(user, is_new_user, bot=default_bot):
    print(f"\n##### New conversation #####")
    user_id, user_name, user_subject_id, user_category_id = user
    bot_id, bot_name, bot_subject_id, bot_category_id = bot
    conversation_id = dbop.add("conversations", (user_id,), connection)
    
    # Here, determine who sends the last message.
    # If it is the user, we need to get the bot to send a message
    # (but this is an edge case, which happens when we have an unexpected
    # interruption of the program between the time that the user sent a message
    # and the time that the bot shoudl have sent the reply)
    index = 1

    while True:
        print("Write a message (q to leave):")
        content = input()
        
        if content == "q":
            break
        else:
            new_message(user_name, user_id, bot_id, content, conversation_id, index)
            variant = get_variant(content, index)
            bot_reply = dbop.get_by(connection, "content_finders",
                                    ("message_index", index),
                                    ("variant", variant),
                                    ("user_id", bot_id))
            if bot_reply:
                bot_reply = bot_reply[0]
                _, _, _, _, content_id, next_index, next_bot_id, next_content_type = bot_reply
                
                if bot_id == next_bot_id:
                    new_bot_message(bot_name, bot_id, user_id, content_id, conversation_id, index, variant)
                    index = next_index
                else:
                    index = next_index
                    bot_id, bot_name, bot_subject_id, bot_category_id = dbop.get_by(connection, "users", ("id", next_bot_id))[0]
                    variant = 1
                    bot_reply = dbop.get_by(connection, "content_finders",
                        ("message_index", index),
                        ("variant", variant),
                        ("user_id", bot_id))
                    if bot_reply:
                        bot_reply = bot_reply[0]
                        _, _, _, _, content_id, next_index, next_bot_id, next_content_type = bot_reply
                        
                        new_bot_message(bot_name, bot_id, user_id, content_id, conversation_id, index, variant)
                        index = next_index
            else:
                print("END OF CONVERSATION")
                break
            
user_id = 1
is_new_user = True
user = dbop.get_by(connection, "users", ("id", user_id))[0]

if user:
    user_id, user_name, user_subject_id, user_category_id = user
    print(f"##### {user_name} conversations #####")
    
    while True:
        conversations = dbop.get_by(connection, "conversations", ("user_id", user_id))
        if conversations:
            is_new_user = False
            print()
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
            new_conversation(user, is_new_user)
        else:
            conversation_id = command
            messages = dbop.get_by(connection, "messages", ("conversation_id", conversation_id))
            
            if not messages:
                print("No message in this conversation")
            
            for message in messages:
                # Can be optimized
                sender_id, content_id = message[1], message[3]
                sender_name = dbop.get_by(connection, "users", ("id", sender_id))[0][1]
                message_content = dbop.get_by(connection, "contents", ("id", content_id))[0][1]
                print(f"{sender_name}: {message_content}")
            print()
    
else:
    print("WARNING: Unknown user")

connection.commit()
connection.close()
