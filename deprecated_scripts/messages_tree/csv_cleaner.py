#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 21:44:58 2020

@author: hugo
"""

# Take a CSV to create a new CSV that will be used to display a tree
# Schema: CSV (database-format) -> CSV (tree-format)

SOURCE = "sample_messages.csv"
DESTINATION = "tree_sample_messages.csv"

SEPARATOR = ","

database_csv = []
tree_csv = []

with open(SOURCE) as file:
    database_csv = file.readlines()

header = database_csv.pop(0).rstrip().split(SEPARATOR)
INDEX = {value: index for index, value in enumerate(header)}

new_header = ["name", "parent"]
dico = {}
children = {}

for i, line in enumerate(database_csv):
    line = line.rstrip().split(SEPARATOR)
    database_csv[i] = line
    
    bot_id = line[INDEX["bot_id"]]
    message_index = line[INDEX["message_index"]]
    variant = line[INDEX["variant"]]
    
    key = bot_id + "-" + message_index
    
    if key in dico:
        dico[key][variant] = line
    else:
        dico[key] = {variant: line}

for key, value in dico.items():
    print(key)
    print(value)
    print()
    

for line in database_csv:
    next_bot_id = line[INDEX["next_bot_id"]]
    next_message_index = line[INDEX["next_message_index"]]
    
    bot_id = line[INDEX["bot_id"]]
    message_index = line[INDEX["message_index"]]
    variant = line[INDEX["variant"]]
    
    content = line[INDEX["content"]]
    
    key = bot_id + "-" + message_index
    
    children_key = next_bot_id + "-" + next_message_index
    
    if key == "2-1":
        tree_csv.append(content + "," + "null")
    if children_key in dico:
        for variant, children in dico[children_key].items():
            tree_csv.append(children[INDEX["content"]] + "," + content)
    else:
        print("End of chain", children_key)


#for line in database_csv:
#    new_line = [line[INDEX["content"]]]
#
#    tree_csv.append(SEPARATOR.join(new_line))

with open(DESTINATION, "w") as file:
    file.write(",".join(new_header) + "\n")
    file.write("\n".join(tree_csv))