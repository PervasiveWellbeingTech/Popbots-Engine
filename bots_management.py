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


def add_bot_message(content, index, variant, bot_id, next_index, next_bot_id, next_content_type, connection=connection):
    content_id = dbop.add("contents", (content, bot_id, None), connection)
    dbop.add("content_finders", (index, variant, bot_id, content_id, next_index, next_bot_id, next_content_type), connection)
    print("Message added")


def display_messages(bot_id, index, depth):
    messages = dbop.get_by(connection, "content_finders", ("user_id", bot_id), ("message_index", index))

    for message in messages:
        message_id, message_index, variant, user_id, content_id, next_message_index = message
        content = dbop.get_by(connection, "contents", ("id", content_id))[0][1]
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
            add_bot_message(content, index, variant, bot_id, next_index, bot_id, "text")
        elif command == "t":
            display_messages_tree(bot_id)
        else:
            print("Unknown command")


if __name__ == "__main__":
    print("##### Bots #####")
    
    while True:
        bots = dbop.get_by(connection, "users", ("category_id", BOT_CATEGORY_ID))
        
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
            bots = dbop.get_by(connection, "users", ("id", bot_id))
            if bots:
                manage_bot(bots[0])
    
    connection.commit()
    connection.close()
