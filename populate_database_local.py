import psycopg2
import traceback
import re

from models.user import Users
from models.core.config import config_string
from models.conversation import ContentFinderJoin,Content,BotContents,NextMessageFinders
from models.core.pushModels import push_intent_list,push_context_list,push_trigger_list,Keyboards,Language,LanguageTypes,ContextFinders,IntentFinders,ContentFinders
from controllers.rasa_nlu import train_rasa_model, check_existence

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pandas import read_excel


engine = create_engine(config_string())
Session = sessionmaker(bind=engine)
session = Session()

RANGE_NAME = "Users"
SPREADSHEET_NAME = './bot_sample_data/bot_script_excel.xlsx'
normal = False 

def push_element(Element,name):

    element = session.query(Element).filter_by(name=name).first()

    if element is None:
        element = Element(name=name)
        session.add(element)
        session.commit()

    return element.id

def rasa_process(context_list,intents_synonyms_regexes):

    for context in context_list:
        if "@" not in context:
            intents = context.split("/")
            match_list = []

            intent_synonym_list = [] #in the (intent, intent_synonym ) format
            for intent in intents:
                print(f"Intent {intent} processed")
                intent = intent.replace("^","")
                row = intents_synonyms_regexes.loc[intents_synonyms_regexes['intent'] ==intent,:] 
                print(row.synonyms)
                intent_synonym_list.append((intent,row.synonyms.tolist()[0].split("|")))
                if row.interpreter_type.tolist()[0] == 'rasa':
                    match_list.append(True)
                else:
                    match_list.append(False)
            
            if all(match_list): #this means that all intents are rasa-compatible
                model_name = context.replace("/","_")

                if not check_existence(intents):
                    train_rasa_model(model_name,tuple(intent_synonym_list))

def fetch_csv(spreadsheet_name,tab_name):
    return read_excel(spreadsheet_name, sheet_name=tab_name,dtype=str)


try:
    user_table = fetch_csv(SPREADSHEET_NAME,RANGE_NAME)
    print(user_table.head(10))
    active_bots = [user['name'] for index,user in user_table[(user_table['active'] == '1') & (user_table['updated'] == '1')].iterrows() ]
    #must_delete_bots = [user['name'] for index,user in user_table[(user_table['delete'] == '1') & (user_table['updated'] == '1')].iterrows() ]

    print(f'Actives Bot are: {active_bots}')
    intents_synonyms_regexes = fetch_csv(SPREADSHEET_NAME,'branching_synonyms_regexes')

    for bot in active_bots:

        user = session.query(Users).filter_by(name=bot).first()
        if user is None: # if the user does not exist create it
            user = Users(name=bot,category_id = 2,desactivated = False) # create the new user
            session.add(user)
            session.commit()
            print(f'Succesfully added bot {user.name} ')
        elif user:
            #session.query(SelectorFinders).filter_by(index=user.id).delete()
            #session.query(IntentFinders).filter_by(user_id=user.id).delete()

            session.query(ContentFinders).filter_by(user_id=user.id).delete()
            
            #session.query(BotContents).filter_by(user_id=user.id).delete()
            session.query(NextMessageFinders).filter_by(user_id=user.id).delete()

            session.commit()
            print(f'Deleted all contents for bot {user.name}')
        
        bot_scripts = fetch_csv(SPREADSHEET_NAME,bot)
        
        for index,script in bot_scripts.iterrows():

            content = Content(text= script.content,user_id = user.id)
            session.add(content)
            session.commit()

            for next_index in script.next_indexes.split("|"):
                if next_index != 'none':

                    new_nmf = NextMessageFinders(
                        user_id = user.id,
                        source_message_index = script.msg_index,
                        next_message_index = int(next_index)
                    )
                    session.add(new_nmf)
                    session.commit()

            
            language_id = push_element(Language,script.language)
            language_type_id = push_element(LanguageTypes,script.language_type)
            keyboard_id = push_element(Keyboards,script.keyboard)
            
            intents_list = [x.lower() for x in script.intents.split("|")]

            for intent in intents_list:
                
                
                

                content_finders = ContentFinders(
                    user_id = user.id,
                    message_index = script.msg_index
                )
                session.add(content_finders)
                session.commit()
            


                new_bot_content = BotContents(

                    content_finders_id = content_finders.id,
                    content_id = content.id,            

                    language_type_id = language_type_id,
                    language_id = language_id,
                    keyboard_id = keyboard_id
                    

                )
            
                session.add(new_bot_content)
                session.commit()


                print(f"Added new content at index {content_finders.message_index}")

                
                context_list = [x.lower() for x in script.context.split("|")]
                
                
                triggers = [(trigger,False) for trigger in script.next_action.split("|")] 
                
                user_input_tag = str(script.user_input_tag).split("|")

                for index,tag in enumerate(user_input_tag):
                    if tag != 'none':
                        triggers +=  [(str(tag),True)]


                intents = [x.lower() for x in intent.split("|")]
                ## adding intent and context and next_actions

                intents_synonyms_regexes['intent'] = intents_synonyms_regexes['intent'].str.lower()
                
                rasa_process(context_list,intents_synonyms_regexes)


                push_intent_list(session,intents=intents,content_finder_id=content_finders.id,synonyms_regexes=intents_synonyms_regexes)
                push_context_list(session,context_list=context_list,content_finder_id=content_finders.id)
                push_trigger_list(session,triggers=triggers,content_finder_id=content_finders.id)

            
        
        print(f"Added all new contents for bot {user.name}")


except (BaseException, psycopg2.DatabaseError) as error:
    print(error)
    tb = traceback.TracebackException.from_exception(error)
    print(''.join(tb.stack.format()))








