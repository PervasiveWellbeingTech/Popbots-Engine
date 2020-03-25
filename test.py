
from controllers.message import get_bot_response
from models.database_operations import connection_wrapper,select_from_join




    
"""
bot_text = ""
bot_id = 1
next_index = 0


while bot_text != "<CONVERSATION_END>":
    user_response = input("My  input: ")
    bot_text,next_index,triggers = get_bot_response(bot_id=bot_id,next_index=next_index,user_response=user_response,content_index=59)
    print("Bot reply: " + bot_text)
    print(" Next index is "+str(next_index))

if __name__ == "__main__":
    print(connection_wrapper(select_from_join,True,"content_finders","ALL content_finders.id,contents.text,keyboards.name",
            (("bot_contents","content_finders.bot_content_index","bot_contents.index"),("contents","bot_contents.content_id","contents.id"),("keyboards","bot_contents.keyboard_id","keyboards.id")),
            (("content_finders.user_id",4),("contents.user_id",4),("bot_content_index",4))))

"""


