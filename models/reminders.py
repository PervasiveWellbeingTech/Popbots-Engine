
import os
from models.core.sqlalchemy_config import * #delete all the above and see if it works
from models.conversation import Conversation, Content
from models.user import Users
session = get_session()
Base = get_base()


class Reminders(Base):

    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey(Users.id))
    content_id = Column(Integer, ForeignKey(Content.id))
    creation_date = Column(DateTime(timezone=True))
    reminder_time = Column(DateTime(timezone=True))
    reminder_type = Column(String)
    executed = Column(Boolean)
    expired = Column(Boolean)
	
