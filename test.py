#! ../popbots_venv/bin/python3

#from controllers.message import get_bot_response
#from models.database_operations import connection_wrapper,select_from_join
from models.user import HumanUser,Users

from models.core.sqlalchemy_config import get_session,get_base,ThreadSessionRequest
thread_session = ThreadSessionRequest()

#user = thread_session.s.query(Users).filter_by(id=1231).delete()

#print(user)

"""
from controllers.main import dialog_flow_engine
from controllers.message import get_bot_response

  
if __name__ == "__main__":
    
    bot_text = ""
    bot_id = 1
    next_index = 0


    while bot_text != "<CONVERSATION_END>":
        user_response = input("My  input: ")
        bot_text,next_index,keyboards,triggers = get_bot_response(bot_id=bot_id,next_index=next_index,user_response=user_response,content_index=59)
        print("Bot reply: " + bot_text)
        print(" Next index is "+str(next_index))
    
 

    bot_response = ""
    while bot_response != "<CONVERSATION_END>":
        user_response = input("My  input: ")
        bot_response = dialog_flow_engine(user_id=1234567,user_message=user_response)
        print("Bot reply: " + str(bot_response['response_list']))
    """



