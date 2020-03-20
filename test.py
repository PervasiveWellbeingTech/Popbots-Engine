
from controllers.message import get_bot_response

if __name__ == "__main__":
    

    bot_text = ""
    bot_id = 1
    next_index = 0
    

    while bot_text != "<CONVERSATION_END>":
        user_response = input("My  input: ")
        bot_text,next_index,triggers = get_bot_response(bot_id=bot_id,next_index=next_index,user_response=user_response,content_index=59)
        print("Bot reply: " + bot_text)
        print(" Next index is "+str(next_index))


