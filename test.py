#! ../popbots_venv/bin/python3

from controllers.main import *
from controllers.message import get_bot_response,stressor_pass
from models.database_operations import connection_wrapper,select_from_join
from models.user import HumanUser,Users
from models.conversation import MessageContent
from models.core.sqlalchemy_config import get_session,get_base,ThreadSessionRequest
session = ThreadSessionRequest().s




if __name__ == "__main__":
    #print(feature_selector_split("yes i am ready","no?else"))
    
    #list = ["~something","!random"]

    #print(get_bot_ids(session,1,"Greeting Module"))
    
    #bool_trigger = [True if "~" in x else False for x in list ]
    #rint(not all(bool_trigger))

    #stressor1 = session.query(MessageContent).filter_by(conversation_id = 38,tag = 'stressor1').first()

    #print([stressor1.text])
    print(stressor_pass())
