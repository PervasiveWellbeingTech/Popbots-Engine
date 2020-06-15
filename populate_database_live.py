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

normal = False 

def push_element(Element,name):

    element = session.query(Element).filter_by(name=name).first()

    if element is None:
        element = Element(name=name)
        session.add(element)
        session.commit()

    return element.id


try:
    user_table = fetch_csv(SPREADSHEET_ID,RANGE_NAME)
    active_bots = [user['name'] for index,user in user_table[(user_table['active'] == '1') & (user_table['updated'] == '1')].iterrows() ]
    print(f'Actives Bot are: {active_bots}')
    features_synonyms_regexes = fetch_csv(SPREADSHEET_ID,'branching_synonyms_regexes')

    for bot in active_bots:

        user = session.query(Users).filter_by(name=bot).first()
        if user is None: # if the user does not exist create it
            user = Users(name=bot,category_id = 2) # create the new user
            session.add(user)
            session.commit()
            print(f'Succesfully added bot {user.name} ')
        elif user:
            #session.query(SelectorFinders).filter_by(index=user.id).delete()
            #session.query(FeatureFinders).filter_by(user_id=user.id).delete()

            session.query(ContentFinders).filter_by(user_id=user.id).delete()
            
            session.query(BotContents).filter_by(user_id=user.id).delete()
            session.query(NextMessageFinders).filter_by(user_id=user.id).delete()

            session.commit()
            print(f'Deleted all contents for bot {user.name}')
        
        bot_scripts = fetch_csv(SPREADSHEET_ID,bot)
        
        for index,script in bot_scripts.iterrows():

            content = Content(text= script.content,user_id = user.id)
            session.add(content)
            session.commit()

            
            language_id = push_element(Language,script.language)
            language_type_id = push_element(LanguageTypes,script.language_type)
            keyboard_id = push_element(Keyboards,script.keyboard)
            
            incoming_branch_option_list = [x.lower() for x in script.incoming_branch_option.split("|")]

            for feature in incoming_branch_option_list:

                new_content = ContentFinderJoin(

                    user_id = user.id,
                    source_message_index = None,
                    message_index = script.msg_index,
                    bot_content_index = script.msg_index,    
                    content_id = content.id,            

                    language_type_id = language_type_id,
                    language_id = language_id,
                    keyboard_id = keyboard_id
                    

                )
            
                session.add(new_content)
                session.commit()


                print(f"Added new content {new_content.content_finders_id}")

                
                branching_option = [x.lower() for x in script.branching_option.split("|")]
                
                selectors = branching_option
                user_input_tag = str(script.user_input_tag).split("|")

                for index,tag in enumerate(user_input_tag):
                    if tag != 'none':
                        selectors +=  [str(tag)]
                features = [x.lower() for x in feature.split("|")]
                ## adding incoming_branch_option and branching_options and next_actions
                push_feature_list(session,features=features,content_finder_id=new_content.content_finders_id,synonyms_regexes=features_synonyms_regexes)
                push_selector_list(session,selectors=selectors,content_finder_id=new_content.content_finders_id)
                push_trigger_list(session,triggers=script.next_action.split("|"),content_finder_id=new_content.content_finders_id)

            for next_index in script.next_indexes.split("|"):
                if next_index != 'none':

                    new_nmf = NextMessageFinders(
                        user_id = user.id,
                        source_message_index = script.msg_index,
                        next_message_index = int(next_index)
                    )
                    session.add(new_nmf)
                    session.commit()
        
        print(f"Added all new contents for bot {user.name}")

      




except (BaseException, psycopg2.DatabaseError) as error:
    print(error)
    tb = traceback.TracebackException.from_exception(error)
    print(''.join(tb.stack.format()))


