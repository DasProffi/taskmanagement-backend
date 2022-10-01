from datetime import datetime
import os
import hashlib
from flask import request
from marshmallow import ValidationError
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, DateTime, exists
from sqlalchemy.orm import relationship

from api.util.database import new_session, Base, engine
from api.util import log
from configs import settings
from configs.endpoint_response import response_false, response_true, response_false_already_exists


class User(Base):
    __tablename__ = 'user'

    name = Column(String(64), nullable=False)
    key = Column(String(128), nullable=False)
    salt = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False, primary_key=True)
    tasks = relationship("Task")
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    last_updated_by = Column(String(256), nullable=False, )

    def __init__(self, name, password, email, created_by="unknown"):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_updated_by = created_by
        self.name = name
        self.email = email
        self.salt = os.urandom(32)
        self.key = hashlib.pbkdf2_hmac(settings.HASHLIB_ALGO, password.encode(settings.HASHLIB_PASSWORD_ENCODING),
                                       self.salt, settings.HASHLIB_ALGO_ITERATIONS, settings.HASHLIB_KEY_LENGTH)

    @staticmethod
    def _log_validation_error(json: dict[str: Any], err: ValidationError):
        errors = err.messages
        valid_data = err.valid_data
        log.logger.debug("Json:" + json.__str__())
        log.logger.info("Errors:" + errors.__str__())
        log.logger.info("Valid Data:" + valid_data.__str__())

    def add_self(self, created_by="") -> Dict[str, Any]:
        session = new_session()
        if not created_by.__eq__(""):
            self.last_updated_by = created_by
        session.add(self)
        session.commit()
        json = self.serialize
        session.close()
        return json

    @property
    def serialize(self, private=False) -> dict[str: Any]:
        if private:
            return {"name": self.name}
        else:
            return {"name": self.name, "email": self.email}

    @staticmethod
    def deserialize(json: Dict[str, Any]) -> Optional["User"]:
        if json is None or "name" not in json or "email" not in json or "password" not in json:
            return None
        try:
            user: User = User(**json)
            return user
        except ValidationError as err:
            User._log_validation_error(json, err)
            return None

    @staticmethod
    def check(email, password):
        if not User.exists(email):
            return False
        session = new_session()
        user = session.query(User).get(email)
        if user is None:
            return False
        hashed = hashlib.pbkdf2_hmac(settings.HASHLIB_ALGO,
                                     password.encode(settings.HASHLIB_PASSWORD_ENCODING),
                                     user.salt, settings.HASHLIB_ALGO_ITERATIONS,
                                     settings.HASHLIB_KEY_LENGTH)
        matching = hashed == user.key
        session.close()
        return matching

    @staticmethod
    def exists(email) -> bool:
        session = new_session()
        is_existing: bool = session.query(exists().where(User.email == email)).scalar() == 1
        session.close()
        return is_existing

    @staticmethod
    def add() -> Dict[str, Any]:
        json = request.get_json(silent=True)
        user: Optional[User] = User.deserialize(json)
        if user is None:
            log.logger.debug("JSON:" + json.__str__())
            return response_false
        response_json = user.add_self("Backend Add")
        return response_true

    @staticmethod
    def get(email):
        return User.read(email)

    @staticmethod
    def create(name, password, email, created_by="Backend Script") -> Dict[str, Any]:
        if User.exists(email):
            return response_false_already_exists
        user = User(name, password, email, created_by)
        return user.add_self(created_by)

    @staticmethod
    def read(email) -> Dict[str, Any]:
        session = new_session()
        if not User.exists(email):
            log.logger.debug("Requested User doesnt exist - email:" + str(email))
            session.close()
            return response_false
        user: Optional[User] = session.query(User).get(email)
        if user is None:
            log.logger.debug("User couldnt be loaded - email:" + str(email))
            session.close()
            return response_false
        json = user.serialize
        session.close()
        return json

    @staticmethod
    def update_user(email) -> Dict[str, Any]:
        session = new_session()
        user_object = session.query(User).where(User.email == email)
        user_json = User.deserialize(request.get_json())
        if user_json is None:
            session.close()
            return response_false
        user_json["last_updated_by"] = "Put Request"
        user_json["updated_at"] = datetime.now().replace(microsecond=0)
        user_object.update(user_json)
        session.commit()
        response = User.read(email)
        session.close()
        return response

    @staticmethod
    def delete_user(email) -> Dict[str, Any]:
        session = new_session()
        # returns false on failure
        if not User.exists(email):
            log.logger.debug("Requested User doesnt exist - email:" + str(email))
            session.close()
            return response_false
        user = session.query(User).get(email)
        if user is None:
            log.logger.debug("Requested User doesnt exist - email:" + str(email))
            session.close()
            return response_false
        session.delete(user)
        session.commit()
        session.close()
        return response_true


Base.metadata.create_all(engine)
