from models.core.sqlalchemy_config import * #delete all the above and see if it works
from models.user import Users
from utils import log

session = get_session()
Base = get_base()

def get_user_id_from_name(name):

    bot = session.query(Users).filter_by(name=name).first()
    
    if bot is None:
        log('FATAL ERROR',f'{name} is not in the database')
        raise Exception
    else:
        log('DEBUG',f"Bot id is {bot.id}")
        return bot.id # this is the onboarding bot, serve multiple purposes