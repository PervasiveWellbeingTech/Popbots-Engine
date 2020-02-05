import re


from user import HumanUser
from message import get_bot_response
from conversation import Conversation,Message,Content

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://popbots:popbotspostgres7@localhost/popbots')
Session = sessionmaker(bind=engine)
session = Session()


def database_push(element):
    session.add(element)
    session.commit()
    return element.id

def conversation_timeout(user_id):
     
    """
    Check if the conversation has timed out.

    Parameter:
        user_id(int) -- unique identifyer

    Return:
        (bool) -- True if the conversation has timed out
    
    TIMEOUT_SECONDS = 3600
    if self.user_history[user_id]:
        last_entry_time = self.user_history[user_id][0]['time']
        return time.time()-last_entry_time >= TIMEOUT_SECONDS
    else:
        return False
    """
next_indexes = [0]
selectors_index = 1 
next_selector_index = 1 # default is always one
conversation_index = 0
conversation_id = 0
def response_engine(user_id,user_message):

    global next_indexes #to be removed
    global selectors_index #to be removed
    global next_selector_index # to be removed 
    global conversation_index
    global conversation_id
    response_dict={'response_list':None,'img':None,'reply_markup':None}

    ############ Special Cases #######################
    if re.match(r'/start', user_message): #restart
        pass
    elif conversation_timeout(user_id): #Time out
        pass 

    elif re.match(r'/switch', user_message): #switch
        pass 
    elif re.match(r'Hi',user_message):

        dt = datetime.now()
        conversation = Conversation(user_id=user_id,start_time=dt)

        conversation_index = 0
        conversation_id = database_push(conversation)
        print("User said hi")
        

    bot_id = 6 ########### for the moment

    stressor = " that "

    
    bot_text,next_indexes,features_index,selectors_index = get_bot_response(bot_id=bot_id,next_indexes=next_indexes,user_response=user_message,selector_index=selectors_index)
    

    print(f"The user id is: {user_id}")
    content_user = Content(text=user_message,user_id=user_id)
    content_id_user  = database_push(content_user)
    message_user = Message(index=conversation_index,receiver_id=bot_id,sender_id=user_id,content_id=content_id_user,conversation_id = conversation_id,stressor=stressor)
    _ = database_push(message_user) 

    content_bot = Content(text=bot_text,user_id=bot_id)
    content_id_bot  = database_push(content_bot)
    message_bot = Message(index=conversation_index,receiver_id=user_id,sender_id=bot_id,content_id=content_id_bot,conversation_id = conversation_id,stressor=stressor)
    _ = database_push(message_bot)

    return bot_text



if __name__ == "__main__":

    bot_response = ""
    while bot_response != "<CONVERSATION_END>":
        user_response = input("My  input: ")
        bot_response = response_engine(user_id=1,user_message=user_response)
        print("Bot reply: " + bot_response)









    