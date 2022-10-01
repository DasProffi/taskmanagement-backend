from datetime import datetime
from typing import Dict, Any, Optional

from flask import request, jsonify, Response
from marshmallow import ValidationError
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, PrimaryKeyConstraint
from sqlalchemy import exists

from api.schema.task_schema import TaskSchema
from api.util import log
from api.util.database import new_session, Base, engine
from configs.endpoint_response import response_false, response_true
from api.util.enums import ProgressState
from api.util.util import datetime_to_json_timestring, json_timestring_to_datetime

ROOT_TASK_ID = -1



class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    last_updated_by = Column(String(256), nullable=False, )
    email = Column(Integer, ForeignKey("user.email"),
                   nullable=False, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(2048), nullable=False)
    due_date = Column(DateTime, nullable=False)
    time_estimate_sec = Column(Integer, )
    priority = Column(Integer, nullable=False)
    progress_state = Column(Enum(ProgressState), nullable=False)
    root_task_id = Column(Integer, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint(email, id),
        {},
    )

    def __init__(self, name: str, description: str, due_date: datetime, time_estimate_sec: int, priority: int,
                 progress_state: ProgressState, email, created_by: str = "unknown", root_task_id: int = ROOT_TASK_ID):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_updated_by = created_by
        self.name = name
        self.description = description
        self.due_date = due_date
        self.time_estimate_sec = time_estimate_sec
        self.priority = priority
        self.progress_state = progress_state
        self.email = email
        self.root_task_id = root_task_id
        self.id = self.get_next_id()

    def __repr__(self):
        return "<Task(name='%s', email='%s', id='%d')>" % (
                                self.name, self.email, self.id)

    def get_id(self):
        return self.id

    def get_next_id(self):
        session = new_session()
        tasks = session.query(Task.id).where(Task.email == self.email).all()
        max_id = max([*map(lambda x: x.id, tasks)]+[0])
        return max_id+1

    @staticmethod
    def _log_validation_error(json: dict[str: Any], err: ValidationError):
        errors = err.messages
        valid_data = err.valid_data
        log.logger.debug("Json:" + json.__str__())
        log.logger.info("Errors:" + errors.__str__())
        log.logger.info("Valid Data:" + valid_data.__str__())

    @property
    def to_json(self):
        dict_of_task: Dict[str, Any] = {'name': self.name, 'description': self.description,
                                        'due_date': datetime_to_json_timestring(self.due_date),
                                        'id': self.id, 'time_estimate_sec': self.time_estimate_sec,
                                        'priority': self.priority, 'progress_state': self.progress_state.value,
                                        'root_task_id': self.root_task_id}
        return dict_of_task

    @property
    def serialize(self) -> dict[str: Any]:
        return self.to_json

    @staticmethod
    def serialize_tasks(tasks: list["Task"]) -> Response:
        tasks_json = []
        for task in tasks:
            task_as_dict = task.to_json
            tasks_json.append(task_as_dict)
        return jsonify(tasks_json)

    def add_self(self, created_by="") -> Dict[str, Any]:
        session = new_session()
        if not created_by.__eq__(""):
            self.last_updated_by = created_by
        session.add(self)
        session.commit()
        json = self.to_json
        session.close()
        return json

    @staticmethod
    def deserialize_preprocess(json: Dict[str, Any], email) -> Optional[Dict[str, Any]]:
        if "due_date" not in json or "progress_state" not in json:
            return None
        json["email"] = email
        json["due_date"] = json_timestring_to_datetime(json["due_date"])
        json["progress_state"] = ProgressState(int(json["progress_state"]))
        return json

    @staticmethod
    def deserialize(json: Dict[str, Any], email) -> Optional["Task"]:
        json = Task.deserialize_preprocess(json, email)
        if json is None:
            return None
        try:
            task: Task = Task(**json)
            return task
        except ValidationError as err:
            Task._log_validation_error(json, err)
            return None

    # not correct anymore since email not handled
    @staticmethod
    def deserialize_many(json: Dict[str, Any]) -> Optional[list["Task"]]:
        try:
            tasks: list[Task] = TaskSchema(many=True, only=(
                'name', 'description', 'due_date', 'time_estimate_sec',
                'priority', 'progress_state', 'root_task_id')).load(json)
            return tasks
        except ValidationError as err:
            Task._log_validation_error(json, err)
            return None
        finally:
            return None

    @staticmethod
    def exists(task_id, email) -> bool:
        session = new_session()
        is_existing: bool = session.query(exists().where(Task.id == task_id, Task.email == email)).scalar() == 1
        session.close()
        return is_existing

    @staticmethod
    def add(email) -> Dict[str, Any]:
        json = request.get_json(silent=True)
        task: Optional[Task] = Task.deserialize(json, email)
        if task is None:
            log.logger.debug("JSON:" + json.__str__())
            return response_false
        response_json = task.add_self("Backend Add")
        return response_json

    @staticmethod
    def get(task_id: int, email) -> "Task":
        return Task.deserialize(Task.read(task_id, email),email)

    @staticmethod
    def create(name: str, description: str, due_date: DateTime, time_estimate_sec: int, priority: int,
               progress_state: ProgressState, email, created_by: str = "Backend Script") -> Dict[str, Any]:
        task: Task = Task(name, description, due_date, time_estimate_sec, priority, progress_state, email)
        return task.add_self(created_by)

    @staticmethod
    def read(task_id: int, email) -> Dict[str, Any]:
        session = new_session()
        if not Task.exists(task_id,email):
            log.logger.debug("Requested Task doesnt exist - id:" + str(task_id)+ " email: " + email)
            session.close()
            return response_false
        task: Optional[Task] = session.query(Task).get({"email": email, "id": task_id})
        if task is None:
            log.logger.debug("Task couldnt be loaded - id:" + str(task_id)+ " email: " + email)
            session.close()
            return response_false
        json = task.to_json
        session.close()
        return json

    @staticmethod
    def update_task(task_id: int, email) -> Dict[str, Any]:
        session = new_session()
        task_object = session.query(Task).where(Task.id == task_id, Task.email == email)
        task_json = Task.deserialize_preprocess(request.get_json(),email)
        if task_json is None:
            session.close()
            return response_false
        task_json["last_updated_by"] = "Put Request"
        task_json["updated_at"] = datetime.now().replace(microsecond=0)
        task_object.update(task_json)
        session.commit()
        response = Task.read(task_id,email)
        session.close()
        return response

    @staticmethod
    def delete_task(task_id, email) -> Dict[str, Any]:
        session = new_session()
        # returns false on failure
        if not Task.exists(task_id, email):
            log.logger.debug("Requested Task doesnt exist - id:" + str(task_id) + " email: " + email)
            session.close()
            return response_false
        task = session.query(Task).get({"email": email, "id": task_id})
        if task is None:
            log.logger.debug("Requested Task doesnt exist - id:" + str(task_id) + " email: " + email)
            session.close()
            return response_false
        session.delete(task)
        session.commit()
        session.close()
        return response_true

    @staticmethod
    def get_all() -> (list["Task"], int):
        session = new_session()
        tasks = session.query(Task).all()
        response = Task.serialize_tasks(tasks)
        session.close()
        return response

    @staticmethod
    def get_subtasks(task_id, email) -> (list["Task"], int):
        session = new_session()
        tasks: list[Task] = session.query(Task).where(Task.root_task_id == task_id, Task.email == email)
        response = Task.serialize_tasks(tasks)
        session.close()
        return response

    @staticmethod
    def get_root_tasks(email) -> (list["Task"], int):
        session = new_session()
        tasks: list[Task] = session.query(Task).where(Task.root_task_id == ROOT_TASK_ID, Task.email == email)
        response = Task.serialize_tasks(tasks)
        session.close()
        return response

    @staticmethod
    def add_dummy_tasks() -> None:
        session = new_session()
        tasks = [
            Task("Clean", "Clean Room", datetime(2025, 10, 20), 3600, 10, ProgressState.not_started, "dummy-creation"),
            Task("Homework", "Do Homework!", datetime(2022, 12, 24), 7200, 1, ProgressState.is_finished,
                 "dummy-creation"),
            Task("Webinterface", "Program Webinterface", datetime(2022, 4, 4), 7200, 1, ProgressState.in_progress,
                 "dummy-creation"), ]
        for task in tasks:
            task.add_self()
            log.logger.info(task.__str__())
        session.commit()
        session.close()


Base.metadata.create_all(engine)
