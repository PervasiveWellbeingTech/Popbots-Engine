#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 21:12:32 2020

@author: hugo
"""

import sqlite3
import database_operations as dbop

BOT_CATEGORY_ID = 2
connection = sqlite3.connect("database.sqlite3")


def new_bot():
    bot_name = input("Bot name: ")
    dbop.add("users", (bot_name, None, 2), connection)
    print(f"{bot_name} added")    


def add_bot_message(content, index, variant, next_index, bot_id):
    content_id = dbop.add("contents", (content, bot_id), connection)
    dbop.add("content_finders", (index, variant, bot_id, content_id, next_index), connection)
    print("Message added")


def display_messages(bot_id, index, depth):
    messages = dbop.get_by_and("user_id", "message_index", "content_finders", bot_id, index, connection)

    for message in messages:
        message_id, message_index, variant, user_id, content_id, next_message_index = message
        content = dbop.get_by("id", "contents", content_id, connection)[0][1]
#        print(f"{2*(depth-1)*' '}|__ {content}")
        print(f"{depth*' |'}__({message_index}-{variant}) {content}")
        print(f"{(depth+1)*' |'}")
        display_messages(user_id, next_message_index, depth + 1)


def display_messages_tree(bot_id):
    display_messages(bot_id, 1, 1)


def manage_bot(bot):
    bot_id, bot_name, _, _ = bot
    print(f"\n##### Manage {bot_name} messages #####")
    
    while True:
        print("\n- To see the messages tree, type t")
        print("- To add a message, type +")
        print("- To quit, type q")
        command = input()
        
        if command == "q":
            break
        elif command == "+":
            content = input("Content: ")
            index = input("Index: ")
            variant = input("Variant: ")
            next_index = input("Next index: ")
            add_bot_message(content, index, variant, next_index, bot_id)
        elif command == "t":
            display_messages_tree(bot_id)
        else:
            print("Unknown command")


print("##### Bots #####")

while True:
    bots = dbop.get_by("category_id", "users", BOT_CATEGORY_ID, connection)
    
    if not bots:
        print("No bot yet")
    
    for bot in bots:
        bot_id, bot_name, _, _ = bot
        print(f"  - n°{bot_id} {bot_name}")
    
    print("\n- To manage a bot, type the bot number")
    print("- To add a bot, type +")
    print("- To quit, type q")
    command = input()
    
    if command == "q":
        break
    elif command == "+":
        new_bot()
    else:
        bot_id = command
        bots = dbop.get_by("id", "users", bot_id, connection)
        if bots:
            manage_bot(bots[0])

connection.commit()
connection.close()
