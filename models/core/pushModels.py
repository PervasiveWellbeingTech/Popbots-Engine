from models.core.sqlalchemy_config import * #delete all the above and see if it works

from models.conversation import NextMessageFinders

from models.user import Users
import traceback
import pandas as pd


session = get_session()
Base = get_base()


class Keyboards(Base):
    __tablename__ = 'keyboards'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Language(Base):
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class LanguageTypes(Base):
    __tablename__ = 'language_types'
    id = Column(Integer, primary_key=True)
    name = Column(String)



class Context(Base):
    __tablename__='context'
    id = Column(Integer,primary_key=True)
    name = Column(String)


class ContextFinders(Base):
    __tablename__='context_finders'
    id = Column(Integer,primary_key=True)
    content_finders_id =  Column(Integer, ForeignKey('content_finders.id', ondelete='CASCADE'))
    context_id = Column(Integer, ForeignKey('context.id'))

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
    

class TriggerFinders(Base):
    __tablename__='trigger_finders'
    id = Column(Integer,primary_key=True)
    content_finders_id =  Column(Integer, ForeignKey('content_finders.id', ondelete='CASCADE'))
    trigger_id = Column(Integer, ForeignKey('triggers.id'))
    outbound = Column(Boolean)


class ContentFinders(Base):
    __tablename__='content_finders'
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey(Users.id))
    message_index = Column(Integer)
    context_Finders = relationship(ContextFinders,cascade='all,delete',passive_deletes=True)
    intentFinders = relationship(IntentFinders,cascade='all,delete',passive_deletes=True)




def push_context_list(session,context_list,content_finder_id):

    try:

        for context_string in context_list:
            context = session.query(Context).filter_by(name=context_string).first()

            if context is None:
                context = Context(name=context_string)
                session.add(context)
                session.commit()

            manytomany = ContextFinders(content_finders_id=content_finder_id,context_id = context.id)
            session.add(manytomany)
        
        session.commit()

    except Exception as error:
        print(error)

def push_intent_list(session,intents,content_finder_id,synonyms_regexes):

    synonyms_regexes['intent'] = synonyms_regexes['intent'].str.lower()

    try:

        for fea in intents:

            
            row = synonyms_regexes.loc[synonyms_regexes['intent'] ==fea,:] 
            if all(list(row.all().isnull().values)):
                raise Exception(f"No synonyms nor regex has been found for intents {fea}")
            else:

             
                if row.regex.values == 'none':
                    regex = None
                else:
                    regex = str(row.regex.values[0]).strip("'")

                if row.synonyms.values == 'none':
                    synonyms = None
                else:
                    synonyms = str(row.synonyms.values).strip("][").strip("'")

                if synonyms is None and regex is None and fea != 'none':
                    raise Exception(f"Synonyms and regex together are none for intent {fea} this is not allowed, the synonym should at least contain (if applies) the name of the intent itself")
                
                intent = session.query(Intents).filter_by(name=fea).first()

                if intent is None:
                    intent = Intents(name=fea,synonyms=synonyms,regex=regex)
                    session.add(intent)
                    session.commit()
                else:
                    intent.synonyms = synonyms
                    intent.regex = regex
                    session.commit()

                manytomany = IntentFinders(content_finders_id=content_finder_id,intent_id = intent.id)
                session.add(manytomany)
        
        session.commit()

    except Exception as error:
        print(error)
        tb = traceback.TracebackException.from_exception(error)
        print(''.join(tb.stack.format()))

def push_trigger_list(session,triggers,content_finder_id):

    try:

        for trig,outbound in triggers:
            trigger = session.query(Trigger).filter_by(name=trig).first()

            if trigger is None:
                trigger = Trigger(name=trig)
                session.add(trigger)
                session.commit()

            manytomany = TriggerFinders(content_finders_id=content_finder_id,trigger_id = trigger.id,outbound=outbound)
            session.add(manytomany)
        
        session.commit()

    except Exception as error:
        print(error)
        tb = traceback.TracebackException.from_exception(error)
        print(''.join(tb.stack.format()))





