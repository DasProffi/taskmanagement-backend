from os.path import exists

from flask.logging import default_handler
from flask import Flask
from flask_cors import CORS

from api.models.blocklist_token import BlocklistToken
from api.util import log
from configs import settings
from api.endpoint_blueprints.user_endpoints import user_endpoint_blueprint
from api.endpoint_blueprints.task_endpoints import task_endpoint_blueprint
from api.endpoint_blueprints.auth_endpoints import auth_endpoint_blueprint

from flask_jwt_extended import JWTManager

app: Flask = Flask(__name__)
appCors: CORS = CORS(app, supports_credentials=True)
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_token_invalid(_, jwt_payload: dict):
    jti = jwt_payload["jti"]
    return BlocklistToken.check_on_blocklist(jti)


def configure_app():
    app.logger.removeHandler(default_handler)
    log.configure(app.logger)
    app.logger.info('configuring app...')
    app.register_blueprint(task_endpoint_blueprint)
    app.register_blueprint(auth_endpoint_blueprint)
    app.register_blueprint(user_endpoint_blueprint)
    app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME

    # Configure application to store JWTs in cookies
    app.config['JWT_TOKEN_LOCATION'] = settings.JWT_TOKEN_LOCATION

    # Only allow JWT cookies to be sent over https
    app.config['JWT_COOKIE_SECURE'] = True
    app.config["JWT_COOKIE_SAMESITE"] = "None"

    # Set the cookie paths
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
    app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

    # Enable csrf double submit protection
    app.config['JWT_COOKIE_CSRF_PROTECT'] = settings.JWT_COOKIE_CSRF_PROTECT
    # Setting Secret Key
    if exists(settings.JWT_SECRET_KEY_FILE_PATH):
        app.config['JWT_SECRET_KEY'] = open(settings.JWT_SECRET_KEY_FILE_PATH).read()
    else:
        app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
    app.config["JWT_CSRF_IN_COOKIES"] = True
    app.config['JWT_CSRF_METHODS'] = settings.JWT_CSRF_METHODS
    app.config['JWT_COOKIE_SECURE'] = settings.JWT_COOKIE_SECURE
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.JWT_ACCESS_TOKEN_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = settings.JWT_REFRESH_TOKEN_EXPIRES

    #app.config["JWT_HEADER_TYPE"] = settings.JWT_HEADER_TYPE


def init_app():
    app.logger.info('initializing app...')


def main():
    configure_app()
    init_app()
    app.logger.info('starting app...')
    if settings.FLASK_SSL_USED:
        app.run(debug=settings.FLASK_DEBUG, threaded=settings.FLASK_THREADED,
                ssl_context=(settings.FLASK_SSL_CERT, settings.FLASK_SSL_KEY))
    else:
        app.run(debug=settings.FLASK_DEBUG, threaded=settings.FLASK_THREADED)


if __name__ == '__main__':
    main()
