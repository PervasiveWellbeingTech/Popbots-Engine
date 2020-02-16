import re


from user import HumanUser
from message import get_bot_response
from conversation import Conversation,Message,Content,ContentFinders

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

def response_engine(user_id,user_message):

    #Set custom keyboard (defaults to none)
    reply_markup = {'type':'normal','resize_keyboard':True,'text':""}
    response_dict={'response_list':None,'img':None,'command':None,'reply_markup':reply_markup}
    bot_id = 6

    initialized = False
    
    conversation = session.query(Conversation).filter_by(user_id=user_id,closed = False).order_by(Conversation.start_time.desc()).first()
    if conversation:

        conversation_id = conversation.id
        if (datetime.now() - conversation.start_time).seconds > 3600 : #Time out
            conversation.closed = True
            session.commit()
    else: 
        conversation_id = None
        print(f"Warning the conversation id is none and the message is {user_message}") 

    print(f"This is conversational id {conversation_id}")

    ############        Special Cases        ############

    if re.match(r'/start', user_message): #restart



 
        new_user = HumanUser(user_id=user_id)
        ## TO DO :if(session.query(Message))
        new_user.subject_id = re.findall(' ([0-9]+)', user_message)
        new_user.language_id = 1 # for english
        new_user.language_type_id = 1 # for formal 
        new_user.category_id = 1
        
        new_user.name = "Human"
        session.add(new_user)
        session.commit()

       

        dt = datetime.now()
        conversation = Conversation(user_id=user_id,start_time=dt,closed=False)
        conversation_id = database_push(conversation)

        bot_id = 20 # this is the onboarding bot



    elif re.match(r'/switch', user_message): #switch
        pass
        #conversation.closed = True
        #session.commit() 
        #bot_id = 6 # to do random selection
    elif re.match(r'Hi',user_message) and conversation_id is None :
        print("intered here before ")
        initialized = True
        dt = datetime.now()
        conversation = Conversation(user_id=user_id,start_time=dt,closed=False)
        conversation_id = database_push(conversation)
        bot_id = 20 # for the moment

        

    message = session.query(Message).filter_by(receiver_id=user_id,conversation_id=conversation_id).order_by(Message.id.desc()).first()
    
    if message and not initialized:
        next_index = message.index 
        bot_id = message.sender_id
        if bot_id == 20:
            #bot_id = 6
            pass

    elif initialized:
        print("Entered in the in initized Here")
        bot_id = 20 # this is where it will need to be smart
        next_index = 14
    else: # there is no message
        print("Should not have entered here but did")
        next_index=0
        bot_id = bot_id

    if(next_index !=0):selector_index = session.query(ContentFinders).filter_by(user_id=bot_id,message_index = next_index).first().selectors_index
    else: selector_index = 1
    
    

    stressor = " that "

    
    bot_text,next_index,features_index,selectors_index = get_bot_response(bot_id=bot_id,next_index=next_index,user_response=user_message,selector_index=selector_index)
    
    print(f'Bot text would be: {bot_text}')
    if bot_text == "<SWITCH>":
        response_dict['command'] = "skip"
        next_index = 0
        bot_id = 6
    if bot_text == "":
        next_index = 0
        bot_id = 6
        # not available answer


    print(f"The user id is: {user_id}")
    content_user = Content(text=user_message,user_id=user_id)
    content_id_user  = database_push(content_user)
    message_user = Message(index=None,receiver_id=bot_id,sender_id=user_id,content_id=content_id_user,conversation_id = conversation_id,stressor=stressor,datetime=datetime.now())
    _ = database_push(message_user) 



    content_bot = Content(text=bot_text,user_id=bot_id)
    content_id_bot  = database_push(content_bot)
    message_bot = Message(index=next_index,receiver_id=user_id,sender_id=bot_id,content_id=content_id_bot,conversation_id = conversation_id,stressor=stressor,datetime=datetime.now())
    _ = database_push(message_bot)
    
    if bot_text in set(["<CONVERSATION_END>"]):
        print('Entered in the conversation end')
        conversation.closed = True
        session.commit()
    if bot_text == "<START>":
        response_dict['command'] = "skip"

    
    
    if bot_text == "<CONVERSATION_END>" and bot_id == 20:
        response_dict['command'] = "skip"

    response_dict['response_list'] = bot_text.strip().replace("\\'","'").split("\\n")
    response_dict['reply_markup'] = reply_markup
    

    return response_dict

def dialog_flow_engine(user_id,user_message):

    try:
        command = "skip"
        while command == "skip":

            response_dict  = response_engine(user_id,user_message)
            command  = response_dict['command']
            print("The command is "+str(command))
            
        return response_dict
    except BaseException as error:
        reply_markup = {'type':'normal','resize_keyboard':True,'text':""}
        response_dict={'response_list':['It seems that my bot brain lost itself in the flow...','Sorry for that, say "Hi" to start a new conversation'],'img':None,'command':None,'reply_markup':reply_markup}
        return response_dict
        print('An exception occurred: {}'.format(error))
    

if __name__ == "__main__":

    bot_response = ""
    while bot_response != "<CONVERSATION_END>":
        user_response = input("My  input: ")
        bot_response = dialog_flow_engine(user_id=1,user_message=user_response)
        print("Bot reply: " + str(bot_response['response_list']))

