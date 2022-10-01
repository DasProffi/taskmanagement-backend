from flask import Blueprint

from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models.task import Task

task_endpoint_blueprint: Blueprint = Blueprint('task_endpoints', __name__)


@task_endpoint_blueprint.route('/api/task/<int:current_id>', methods=['GET'])
@jwt_required()
def get_task(current_id):
    json = Task.read(current_id, get_jwt_identity())
    if "success" in json and not json["success"]:
        return json, 400
    return json, 200


@task_endpoint_blueprint.route('/api/task', methods=['POST'])
@jwt_required()
def add_task():
    json = Task.add(get_jwt_identity())
    if "success" in json and not json["success"]:
        return json, 400
    return json, 201


@task_endpoint_blueprint.route('/api/task/<int:current_id>', methods=['PUT'])
@jwt_required()
def update_task(current_id):
    json = Task.update_task(current_id, get_jwt_identity())
    if "success" in json and not json["success"]:
        return json, 400
    return json, 200


@task_endpoint_blueprint.route('/api/task/<int:current_id>', methods=['DELETE'])
@jwt_required()
def delete_task(current_id):
    json = Task.delete_task(current_id, get_jwt_identity())
    if "success" in json and not json["success"]:
        return json, 400
    return json, 200


@task_endpoint_blueprint.route('/api/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    response = Task.get_all()
    return response


@task_endpoint_blueprint.route('/api/subtasks/<int:current_id>', methods=['GET'])
@jwt_required()
def get_subtasks(current_id):
    response = Task.get_subtasks(current_id, get_jwt_identity())
    return response


@task_endpoint_blueprint.route('/api/roottasks', methods=['GET'])
@jwt_required()
def get_root_tasks():
    response = Task.get_root_tasks(get_jwt_identity())
    return response
