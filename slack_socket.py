#! ../../venv_popbots/bin/ python3


import os
from slack import RTMClient
import ssl
import certifi
import re
import sqlalchemy

from controllers.main import dialog_flow_engine



@RTMClient.run_on(event="message")
def slack_socket(**payload):

    data = payload['data']
    
    web_client = payload['web_client']

    if data.get('upload',None) is None and data.get('text',None) is not None and data.get('bot_id',None) is None:
        
        channel_id = data['channel']
        query = data['text']
        user = data["user"]
        user_id = "".join(str(ord(x)) for x in user)#re.sub("[^0-9]", "",user )
        response  = dialog_flow_engine(int(user_id[0:9]),user_message=query)
        
        command  = response['command']

        if command != "pass":

            """if response['img'] is not None:
                web_client.files_upload(
                    channels=channel_id,
                    file=response['img'],
                    title="Test upload",
                    
                )"""
            reply_markup = response['reply_markup']
            attachments = None
            if reply_markup is not None:

                if reply_markup['type'] == 'inlineButton':

                    buttons = reply_markup['text'].split(",")
                    actions = []
                    for button in buttons:
                        actions.append({
                                "name": f"{button}",
                                "text": f"{button}",
                                "type": "button",
                                "value": f"{button}"
                                })

                    attachments= [{

                                            "text" : "Choose or type an answer",
                                            "fallback" : "You can still type an answer",
                                            "callback_id" : "popbots",
                                            "color" : "#3AA3E3",
                                            "attachment_type" : "default",
                                            "actions" : actions
                                        }
                                    ] 

            emoji_name = response['bot_name'].split(" ")[0].lower()
            for res in response['response_list']:
                try:
                    
                    web_client.chat_postMessage(
                        channel=channel_id,
                        text=res,
                        #icon_url='https://ibb.co/HhVt0cc',
                        icon_emoji  = ":{}:".format(emoji_name),
                        username  = response['bot_name'],
                        as_user = False,
                        attachments = attachments
                        
                    )
                except BaseException as error:
                    print("[ERROR] The message is empty or invalid")
            
        else:
            pass
    else:
        channel_id = data['channel']
        print(data)


if __name__ == "__main__":

    SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    slack_token = SLACK_API_TOKEN
    if slack_token is None:
        print("[ERROR] Slack Token not found")
        raise ValueError
    rtm_client = RTMClient(token=slack_token,ssl=ssl_context)
    rtm_client.start()


""",
#thread_ts=thread_ts

attachments= [

    {

        "text" : "An answer",
        "fallback" : "You can still type an answer",
        "callback_id" : "",
        "color" : "#3AA3E3",
        "attachment_type" : "default",
        "actions" : [
            {
                "name": "game",
                "text": "Thermonuclear War",
                "style": "danger",
                "type": "button",
                "value": "war",
                "confirm": {
                    "title": "Are you sure?",
                    "text": "Wouldn't you prefer a good game of chess?",
                    "ok_text": "Yes",
                    "dismiss_text": "No"
                }
            }
        ]
    }
] 
"""