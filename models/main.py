import re
import random
from datetime import datetime

from models.user import HumanUser,Users
from models.utils import get_user_id_from_name
from models.core.config import config_string
from models.conversation import Conversation,Message,Content,ContentFinders,MessageContent
from models.stressor import Stressor,populated_stressor
from models.core.sqlalchemy_config import get_session,get_base,ThreadSessionRequest

from utils import log,timed


def database_push(session,element):
    session.add(element)
    session.commit()
    return element.id

@timed
def push_message(session,text,user_id,datetime,answering_time,index,receiver_id,sender_id,conversation_id,tag):
    content_user = Content(text=text,user_id=user_id)
    content_id_user  = database_push(session,content_user)
    message_user = Message(index=index,receiver_id=receiver_id,sender_id=sender_id,content_id=content_id_user,conversation_id = conversation_id,datetime=datetime,answering_time=answering_time,tag=tag)
    _ = database_push(session,message_user) 


def delconv(session,user_id):
    conversation = session.query(Conversation).filter_by(user_id=user_id,closed = False).order_by(Conversation.datetime.desc()).first()
    if conversation:
        conversation.closed = True
        session.commit()


@timed
def create_human_user(session,user_id,user_message):
    """
        Create user object, binds subject id to it (to be completed), set the language, language_type, initializes the user_name

    """
    user = HumanUser(user_id=user_id)
    subject_id = re.findall(r'\d+', user_message)
    if subject_id:
        user.subject_id = subject_id[0]
    else:
        user.subject_id = "0000"
    user.language_id = 1 # for english
    user.language_type_id = 1 # for formal 
    user.category_id = 1
    user.desactivated = False
    possible_group = ["Group","Moderator"]
    user.experiment_group = possible_group[random.randint(0,1)]
    
    user.name = "Human" # this is the default
    session.add(user)
    session.commit()

    return user


@timed
def create_conversation(session,user_id):
    dt = datetime.now()
    conversation = Conversation(user_id=user_id,datetime=dt,closed=False)
    _ = database_push(session,conversation)

    return conversation

def push_stressor(session,conv_id):
    print(conv_id)
    stressor1 = session.query(MessageContent).filter_by(conversation_id = conv_id,tag = 'stressor1').first()
    stressor2 = session.query(MessageContent).filter_by(conversation_id = conv_id,tag = 'stressor2').first()
    stressor3 = session.query(MessageContent).filter_by(conversation_id = conv_id,tag = 'stressor3').first()

    stress_level = session.query(MessageContent).filter_by(conversation_id = conv_id,tag = 'stress_level').first().text

    print(stressor1)
    stressor_list = [stressor1,stressor2,stressor3]
    print(stressor_list)
    stressor_text = '. '.join(x.text for x in stressor_list if x)

    stressor = populated_stressor(stressor_text,stress_level,conv_id = conv_id)

    session.add(stressor)
    session.commit()

    log('INFO',f'Stressor: {stressor_text} sucessfully added to conversation id {conv_id}')
