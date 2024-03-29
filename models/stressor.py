import os
from models.core.sqlalchemy_config import * #delete all the above and see if it works
from models.conversation import Conversation
session = get_session()
Base = get_base()


class Stressor(Base):

    __tablename__ = 'stressor'

    id = Column(Integer, primary_key=True)
    stressor_text = Column(String)
    stress_level = Column(String)
    conversation_id = Column(Integer,ForeignKey(Conversation.id))
	
    category0 = Column(String)
    category1 = Column(String)
    category2 = Column(String)
    category3 = Column(String)
    category4 = Column(String)
    category5 = Column(String)
    category6 = Column(String)
    covid_category = Column(String)

    probability0 = Column(Float(6))

    probability1 = Column(Float(6))
    probability2 = Column(Float(6))
    probability3 = Column(Float(6))
    probability4 = Column(Float(6))
    probability5 = Column(Float(6))
    covid_probability = Column(Float(6))


import requests
import ast

CLASSIFIER_IP_ADDRESS = os.environ['CLASSIFIER_IP_ADDRESS']
FLASK_CLASSIFIER_SERVER_URL = f"http://{CLASSIFIER_IP_ADDRESS}/classifier/"


def get_pred_api(stressor,url):
    headers = {
    'Content-Type': "application/json"
    }
    querystring = {"stressor":stressor}

    payload = ""

    try:
        response = requests.get(url=url, data=payload, headers=headers,params=querystring)

    except Exception as error:
        raise Exception(error)

    return response.json()


def populated_stressor(stressor,stress_level,conv_id):

    result = get_pred_api(stressor,FLASK_CLASSIFIER_SERVER_URL+"stressor")
    covid_results = get_pred_api(stressor,FLASK_CLASSIFIER_SERVER_URL+"covid")

    stressor = Stressor( # added as a dummy for now

        conversation_id = conv_id,
        stressor_text = stressor,
        stress_level = stress_level,
        category0 = result['raw']['category0'],
        category1 = result['raw']['category1'],
        category2 = result['raw']['category2'],
        category3 = result['raw']['category3'],
        category4 = result['raw']['category4'],
        category5 = result['raw']['category5'],
        category6 = "Other",
        covid_category = covid_results['category'],
        
        covid_probability = round(float(covid_results['probability']),4),
        probability0 = round(result['raw']['probability0'],4),
        probability1 = round(result['raw']['probability1'],4),
        probability2 = round(result['raw']['probability2'],4),
        probability3 = round(result['raw']['probability3'],4),
        probability4 = round(result['raw']['probability4'],4),
        probability5 = round(result['raw']['probability5'],4)
    )

    return stressor
    

