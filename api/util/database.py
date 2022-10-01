from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, Session, sessionmaker

from configs import settings

engine: Engine = create_engine(settings.SQL_ALCHEMY_DATABASE_URI, echo=settings.SQL_ALCHEMY_DEBUG)
Base = declarative_base()
Base.metadata.bind = engine
Base.metadata.create_all(engine)

session_maker = sessionmaker(bind=engine)


def new_session() -> Session:
    session = session_maker()
    session.expire_on_commit = False
    return session


def reload_database():
    global session_maker
    session_maker = sessionmaker(bind=engine)


def ping_database():
    try:
        new_session().connection().scalar(select([1]))
    except OperationalError:
        reload_database()
