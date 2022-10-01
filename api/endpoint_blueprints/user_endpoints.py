from flask import Blueprint, request, jsonify

from api.auth.auth import requires_auth
from api.models.user import User
from configs.endpoint_response import response_auth_failed, response_false, response_true

user_endpoint_blueprint: Blueprint = Blueprint('user_endpoints', __name__)


@user_endpoint_blueprint.route('/api/register', methods=['Post'])
def signup():
    json = User.add()
    if "success" not in json or not json["success"]:
        return response_false, 400
    return response_true, 201


@user_endpoint_blueprint.route('/api/deregister', methods=['Post'])
@requires_auth
def deregister():
    email = request.authorization.username
    password = request.authorization.password
    if not User.check(email, password):
        r = jsonify(response_auth_failed)
        return r, 401
    json = User.delete_user(email)
    if "success" in json and not json["success"]:
        return json, 400
    return json, 200
