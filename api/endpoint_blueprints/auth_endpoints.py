from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token,get_jwt_identity

from api.auth.auth import requires_auth, check
from api.models.blocklist_token import BlocklistToken
from configs import settings
from configs.endpoint_response import response_auth_failed, response_auth_succeeded

auth_endpoint_blueprint: Blueprint = Blueprint('auth_endpoints', __name__)


# sets the jwt
@auth_endpoint_blueprint.route('/token/auth', methods=['POST'])
@cross_origin(expose_headers=[settings.JWT_ACCESS_TOKEN_NAME, settings.JWT_REFRESH_TOKEN_NAME])
@requires_auth
def login():
    email = request.authorization.username
    password = request.authorization.password
    if not check(email, password):
        return response_auth_failed

    # Create the tokens we will be sending back to the user
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    resp = jsonify({"login": True, settings.JWT_ACCESS_TOKEN_NAME: access_token,
                    settings.JWT_REFRESH_TOKEN_NAME: refresh_token})
    resp.headers.add(settings.JWT_ACCESS_TOKEN_NAME, access_token)
    resp.headers.add(settings.JWT_REFRESH_TOKEN_NAME, refresh_token)
    return resp, 200


# Same thing as login here, except we are only setting a new cookie
# for the access token.
@auth_endpoint_blueprint.route('/token/refresh', methods=['POST'])
@cross_origin(expose_headers=settings.JWT_ACCESS_TOKEN_NAME)
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()

    access_token = create_access_token(identity=current_user)

    resp = jsonify(response_auth_succeeded)
    resp.headers.add(settings.JWT_ACCESS_TOKEN_NAME, access_token)
    return resp, 200


# Because the JWTs are stored in an httponly cookie now, we cannot
# log the user out by simply deleting the cookie in the frontend.
# We need the backend to send us a response to delete the cookies
# in order to logout. unset_jwt_cookies is a helper function to
# do just that.
@auth_endpoint_blueprint.route('/token/remove', methods=['POST'])
@jwt_required()
def logout():
    access_token = request.headers.get("Authorization")[7:]
    refresh_token = request.json.get(settings.JWT_REFRESH_TOKEN_NAME)
    if not access_token or not refresh_token:
        r = response_auth_failed.copy()
        r.update({"Reason": "Please Provide the Accesstoken in the Header and Refresh Token in the Body"})
        resp = jsonify(r)
        return resp, 401
    BlocklistToken.add(access_token, datetime.now() + 2*settings.JWT_ACCESS_TOKEN_EXPIRES)
    BlocklistToken.add(refresh_token, datetime.now() + 2*settings.JWT_REFRESH_TOKEN_EXPIRES)
    resp = jsonify(response_auth_succeeded)
    return resp, 200


@auth_endpoint_blueprint.route('/token/test', methods=['POST'])
@jwt_required(refresh=True)
def test():
    resp = jsonify(response_auth_succeeded)
    return resp, 200
