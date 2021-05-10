import psycopg2
import traceback
import re

from models.user import Users
from models.core.config import config_string
from models.core.live_google_sheet import fetch_csv
from models.conversation import ContentFinderJoin,Content,BotContents,NextMessageFinders
from models.core.pushModels import push_intent_list,push_context_list,push_trigger_list,Keyboards,Language,LanguageTypes,ContextFinders,IntentFinders,ContentFinders


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(config_string())
Session = sessionmaker(bind=engine)
session = Session()



bot  = input("Name of the bot to delete: ")

user = session.query(Users).filter_by(name=bot).first()
if user is None: # if the user does not exist create it
    print("Bot does not exist")
elif user:

    session.query(ContentFinders).filter_by(user_id=user.id).delete()
    
    #session.query(BotContents).filter_by(user_id=user.id).delete()
    session.query(NextMessageFinders).filter_by(user_id=user.id).delete()

    session.commit()
    print(f'Deleted all contents for bot {user.name}')
    