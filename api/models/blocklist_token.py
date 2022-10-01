from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from api.util.database import Base, new_session, engine


class BlocklistToken(Base):
    __tablename__ = 'blocklisttoken'

    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False, index=True)
    expiring = Column(DateTime, nullable=False)

    def __init__(self, jti, expiring):
        self.jti = jti
        self.expiring = expiring

    @staticmethod
    def add(token, expiring):
        session = new_session()
        t = BlocklistToken(token,expiring)
        session.add(t)
        session.commit()
        session.close()
        return True

    @staticmethod
    def check_on_blocklist(jti):
        session = new_session()
        on_list = session.query(BlocklistToken.id).filter_by(jti=jti).scalar()
        session.close()
        return on_list is not None

    @staticmethod
    def delete_all_expired():
        session = new_session()
        expired = session.query(BlocklistToken).where(BlocklistToken.expiring < datetime.now(), )
        c = 0
        for item in expired:
            session.delete(item)
            c += 1
        session.close()
        return c


Base.metadata.create_all(engine)
