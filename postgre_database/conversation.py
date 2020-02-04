import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('postgresql+psycopg2://popbots:popbotspostgres7@localhost/popbots')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

from sqlalchemy import Column, Integer, String

class conversations(Base):

    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)


    def __repr__(self):
        return "<Conversation(user_id='%s')>" % (self.user_id)

conversation = conversations(user_id="1")
session.add(conversation)

session.commit()


