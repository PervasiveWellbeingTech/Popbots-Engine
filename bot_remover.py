import psycopg2
import traceback
import re

from models.user import Users
from models.core.config import config_string
from models.core.live_google_sheet import fetch_csv
from models.conversation import ContentFinderJoin,Content,BotContents,NextMessageFinders
from models.core.pushModels import push_feature_list,push_selector_list,push_trigger_list,Keyboards,Language,LanguageTypes,SelectorFinders,FeatureFinders,ContentFinders


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(config_string())
Session = sessionmaker(bind=engine)
session = Session()

SPREADSHEET_ID = "1xRTnHL9jpNsNbfC8qNEbrSIqDT0JCdkQmAE9xSKWsEg"
RANGE_NAME = "Users"

input("Name of the bot to delete":"")