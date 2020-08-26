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
    source_message_index = Column(Integer)
    message_index = Column(Integer)
    bot_content_index = Column(Integer)


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
    

user_content_join =  join(Message,Content,Message.content_id == Content.id)

class MessageContent(Base):
    __table__ = user_content_join
    message_id = Message.id
    content_ids = column_property(Content.id,Message.content_id)
    conversation_id = Message.conversation_id
    tag = Message.tag
    text = Content.text






