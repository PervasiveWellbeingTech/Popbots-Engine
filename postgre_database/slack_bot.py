#! ../../venv_popbots/bin/ python3
SLACK_API_TOKEN = "xoxb-212808347746-949315748167-WjsWGkRygsQGTUQIwEB80L70"

import os
from slack import RTMClient
import ssl
import certifi
import re
import sqlalchemy

from main import dialog_flow_engine

@RTMClient.run_on(event="message")
def say_hello(**payload):

    data = payload['data']
    
    web_client = payload['web_client']
    if data.get('bot_id',False) == False:
        
        channel_id = data['channel']
        query = data['text']
        user = data["user"]
        user_id = "".join(str(ord(x)) for x in user)#re.sub("[^0-9]", "",user )
        response  = dialog_flow_engine(int(user_id[0:9]),user_message=query)

        for res in response['response_list']:
            web_client.chat_postMessage(
                channel=channel_id,
                text=res,
                #thread_ts=thread_ts
            )
        

ssl_context = ssl.create_default_context(cafile=certifi.where())
slack_token = SLACK_API_TOKEN
rtm_client = RTMClient(token=slack_token,ssl=ssl_context)
rtm_client.start()