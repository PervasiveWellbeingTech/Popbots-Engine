import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, MetaData, join, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,column_property
from sqlalchemy.ext.declarative import declarative_base



from config import config_string

Base = declarative_base()
from user import Users
from sqlalchemy import Column, Integer,Boolean, String,DateTime,ForeignKey

class Conversation(Base):

    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    start_time = Column(DateTime)
    closed = Column(Boolean)
    
#last_selector = Column(Integer)



class Message(Base):
    __tablename__= 'messages'

    id = Column(Integer,primary_key=True)
    index = Column(Integer)
    sender_id = Column(Integer,ForeignKey(Users.id))
    receiver_id = Column(Integer,ForeignKey(Users.id))
    content_id = Column(Integer)
    conversation_id = Column(Integer)
    stressor = Column(String)
    datetime = Column(DateTime)


class Content(Base):

    __tablename__='contents'

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey(Users.id))
    text = Column(String)

class NextMessageFinders(Base):
    __tablename__=  'next_message_finders'
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey(Users.id))
    source_message_index = Column(Integer)
    next_message_index = Column(Integer)

class ContentFinders(Base):
    __tablename__='content_finders'
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey(Users.id))
    source_message_index = Column(Integer)
    message_index = Column(Integer)
    bot_content_index = Column(Integer)
    #features_index = Column(Integer)
    #selectors_index = Column(Integer)

class BotContents(Base):
    __tablename__ = 'bot_contents'
    
    id = Column(Integer,primary_key=True)
    index = Column(Integer)
    content_id = Column(Integer,ForeignKey(Content.id))
    language_type_id = Column(Integer)
    language_id = Column(Integer)
    keyboard_id = Column(Integer)
    user_id = Column(Integer,ForeignKey(Users.id))
   


bot_contents_join = join(ContentFinders,BotContents,ContentFinders.bot_content_index == BotContents.index)
# join(BotContents,Content,BotContents.content_id == Content.id).

class ContentFinderJoin(Base):
    __table__ = bot_contents_join
    
    #content finders
    content_finders_id = column_property(ContentFinders.id)
    bot_content_id = column_property(BotContents.id)

    
    user_id = column_property(ContentFinders.user_id,BotContents.user_id)
    source_message_index = ContentFinders.source_message_index
    message_index = ContentFinders.message_index
    bot_content_index = column_property(ContentFinders.bot_content_index,BotContents.index)    
    #features_index = ContentFinders.features_index
    #selectors_index = ContentFinders.selectors_index
    
    #Bot contents
    content_id = BotContents.content_id
    
    language_type_id = BotContents.language_type_id
    language_id = BotContents.language_id
    keyboard_id = BotContents.keyboard_id

    #content
    



if __name__ == "__main__":
    engine = create_engine(config_string())
    Session = sessionmaker(bind=engine)
    session = Session()

    a  = Content(text="something",user_id = 50)
    session.add(a)
    session.commit()

    print(a.id)

    """
    b = ContentFinderJoin(

        user_id = 50,
        source_message_index = None,
        message_index = 0,
        bot_content_index = 0,    
        features_index = 1,
        selectors_index = 1,
        
        #Bot contents
        content_id = a.id,
        language_type_id = 1,
        language_id = 1,
        keyboard_id = 1 )
    session.add(b)
    session.commit()
    print(b)
    """



