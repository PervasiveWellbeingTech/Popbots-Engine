from models.core.sqlalchemy_config import * #delete all the above and see if it works
session = get_session()
Base = get_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category_id = Column(Integer)
    desactivated = Column(Boolean)

class HumanUsers(Base):
    __tablename__ = 'human_users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    subject_id = Column(String)
    language_type_id = Column(Integer)
    language_id = Column(Integer)
    experiment_group = Column(String)
    timezone = Column(String)
        
human_users_join = join(Users,HumanUsers)
class HumanUser(Base):
    __table__ = human_users_join

    user_id = column_property(Users.id, HumanUsers.user_id)
    human_users_id = HumanUsers.id
    name = Users.name


    desactivated = Users.desactivated
    experiment_group = HumanUsers.experiment_group
    subject_id = HumanUsers.subject_id
    language_id= HumanUsers.language_id
    language_type_id = HumanUsers.language_type_id
    timezone = HumanUsers.timezone



