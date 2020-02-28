from live_google_sheet import fetch_csv
from bot_management import add_bot_content
from conversation import ContentFinderJoin,Content,BotContents,ContentFinders,NextMessageFinders
from user import Users
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://popbots:popbotspostgres7@localhost/popbots')
Session = sessionmaker(bind=engine)
session = Session()

SPREADSHEET_ID = "1mlegVF0CFDVVRgrfe08J53j6eNfHRThQitIuUEA5pwU"
RANGE_NAME = "Users"



try:
    user_table = fetch_csv(SPREADSHEET_ID,RANGE_NAME)
    active_bots = [user['name'] for index,user in user_table[(user_table['active'] == '1') & (user_table['updated'] == '1')].iterrows() ]
    print(f'Actives Bot are: {active_bots}')
    for bot in active_bots:

        user = session.query(Users).filter_by(name=bot).first()
        if user is None: # if the user does not exist create it
            user = Users(name=bot,category_id = 2) # create the new user
            session.add(user)
            session.commit()
            print(f'Succesfully added bot {user.name} ')
        elif user:
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

            new_content = ContentFinderJoin(

                user_id = user.id,
                source_message_index = None,
                message_index = script.msg_index,
                bot_content_index = script.msg_index,    
                features_index = script.features_finder_index,
                selectors_index = script.next_selectors,
                
                
                content_id = content.id,
                language_type_id = script.language_type_id,
                language_id = script.language_id,
                keyboard_id = script.keyboard_id )
            
            session.add(new_content)
            session.commit()
        
        print(f'Added new contents for bot {user.name}')

        bot_nmf = fetch_csv(SPREADSHEET_ID,"nmf_"+bot.split(" ")[0].lower())

        for index,nmf in bot_nmf.iterrows():

            new_nmf = NextMessageFinders(
                user_id = user.id,
                source_message_index = nmf['msg_index'],
                next_message_index = nmf['next_msg_index']
            )
            session.add(new_nmf)
            session.commit()
            print(f"Committed {nmf}")
        print(f'Added nmf contents for bot {user.name}')




except (BaseException, psycopg2.DatabaseError) as error:
    print(error)
