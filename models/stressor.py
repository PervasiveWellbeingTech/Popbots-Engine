
from models.core.sqlalchemy_config import * #delete all the above and see if it works
from models.conversation import Conversation
session = get_session()
Base = get_base()


class Stressor(Base):

    __tablename__ = 'stressor'

    id = Column(Integer, primary_key=True)
    stressor_text = Column(String)
    conversation_id = Column(Integer,ForeignKey(Conversation.id))
	
    category0 = Column(String)
    category1 = Column(String)
    category2 = Column(String)
    category3 = Column(String)
    category4 = Column(String)
    category5 = Column(String)
    category6 = Column(String)

    probability0 = Column(Float(6))

    probability1 = Column(Float(6))
    probability2 = Column(Float(6))
    probability3 = Column(Float(6))
    probability4 = Column(Float(6))
    probability5 = Column(Float(6))




import requests
import ast

FLASK_CLASSIFIER_SERVER_URL = "http://commuter.stanford.edu/classifier/stressor/"


def get_pred_api(stressor):
    url = FLASK_CLASSIFIER_SERVER_URL
    headers = {
    'Content-Type': "application/json"
    }
    querystring = {"stressor":stressor}

    payload = ""

    try:
        response = requests.get(url=url, data=payload, headers=headers,params=querystring)

    except Exception as error:
        raise Exception(error)

    return response



    

