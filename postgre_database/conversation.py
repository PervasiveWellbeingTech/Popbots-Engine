import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from user import Users



Base = declarative_base()

from sqlalchemy import Column, Integer, String,DateTime,ForeignKey

class Conversation(Base):

    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    start_time = Column(DateTime)


class Message(Base):
    __tablename__= 'messages'

    id = Column(Integer,primary_key=True)
    index = Column(Integer)
    sender_id = Column(Integer,ForeignKey(Users.id))
    receiver_id = Column(Integer,ForeignKey(Users.id))
    content_id = Column(Integer)
    conversation_id = Column(Integer)
    stressor = Column(String)


class Content(Base):

    __tablename__='contents'

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey(Users.id))
    text = Column(String)

engine = create_engine('postgresql+psycopg2://popbots:popbotspostgres7@localhost/popbots')
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == "__main__":
    a = Content(user_id = 1,text="test")

    session.add(a)
    session.commit()



