from models.core.sqlalchemy_config import * #delete all the above and see if it works
from models.user import Users
session = get_session()
Base = get_base()


class Conversation(Base):

    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    datetime = Column(DateTime)
    stressor = Column(String)
    closed = Column(Boolean)
    timeout_threshold = Column(Integer)
    
class Selectors(Base):
    __tablename__='selectors'
    id = Column(Integer,primary_key=True)
    name = Column(String)


class SelectorFinders(Base):
    __tablename__='selector_finders'
    id = Column(Integer,primary_key=True)
    content_finders_id =  Column(Integer, ForeignKey('content_finders.id', ondelete='CASCADE'))
    selector_id = Column(Integer, ForeignKey('selectors.id'))

class Intents(Base):
    __tablename__='intents'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    synonyms = Column(String)
    regex=Column(String)

class IntentFinders(Base):
    __tablename__='intent_finders'
    id = Column(Integer,primary_key=True)
    content_finders_id =  Column(Integer, ForeignKey('content_finders.id', ondelete='CASCADE'))
    intent_id = Column(Integer, ForeignKey('intents.id'))

class Trigger(Base):
    __tablename__='triggers'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    outbound = Column(Boolean)

class TriggerFinders(Base):
    __tablename__='trigger_finders'
    id = Column(Integer,primary_key=True)
    content_finders_id =  Column(Integer, ForeignKey('content_finders.id', ondelete='CASCADE'))
    trigger_id = Column(Integer, ForeignKey('triggers.id'))




class Content(Base):

    __tablename__='contents'

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey(Users.id))
    text = Column(String)
class Message(Base):
    __tablename__= 'messages'

    id = Column(Integer,primary_key=True)
    index = Column(Integer)
    sender_id = Column(Integer,ForeignKey(Users.id))
    receiver_id = Column(Integer,ForeignKey(Users.id))
    content_id = Column(Integer,ForeignKey(Content.id))
    conversation_id = Column(Integer)
    datetime = Column(DateTime)
    tag = Column(String)

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
    message_index = Column(Integer)
    selectorFinders = relationship(SelectorFinders,cascade='all,delete',passive_deletes=True)
    intentFinders = relationship(IntentFinders,cascade='all,delete',passive_deletes=True)




class BotContents(Base):
    __tablename__ = 'bot_contents'
    
    id = Column(Integer,primary_key=True)
    content_id = Column(Integer,ForeignKey(Content.id))
    language_type_id = Column(Integer)
    language_id = Column(Integer)
    keyboard_id = Column(Integer)
    content_finders_id = Column(Integer,ForeignKey(ContentFinders.id))
   


bot_contents_join = join(ContentFinders,BotContents,ContentFinders.id == BotContents.content_finders_id)
# join(BotContents,Content,BotContents.content_id == Content.id).

class ContentFinderJoin(Base):
    __table__ = bot_contents_join
    
    message_index = ContentFinders.message_index

    user_id = ContentFinders.user_id
    #content finders
    content_finders_id = column_property(ContentFinders.id,BotContents.content_finders_id)
    bot_content_id = BotContents.id

    
    #Bot contents
    content_id = BotContents.content_id

    language_type_id = BotContents.language_type_id
    language_id = BotContents.language_id
    keyboard_id = BotContents.keyboard_id

    #content
    

user_content_join =  join(Message,Content,Message.content_id == Content.id)

class MessageContent(Base):
    __table__ = user_content_join
    message_id = Message.id
    content_ids = column_property(Content.id,Message.content_id)
    conversation_id = Message.conversation_id
    tag = Message.tag
    text = Content.text






