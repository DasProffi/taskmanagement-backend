from functools import wraps

from flask import request

from api.models.user import User
from configs.endpoint_response import response_auth_failed


def check(email, password):
    return User.check(email, password)


def requires_auth(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        authorization = request.authorization
        print(authorization)
        if not authorization or not check(authorization.username, authorization.password):
            return response_auth_failed, 401
        return f(*args, **kwargs)
    return decorated_func
