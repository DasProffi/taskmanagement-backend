## Server
from datetime import timedelta

FLASK_SERVER_NAME = '127.0.0.1:5000'
FLASK_DEBUG = False  # change before deployment
FLASK_THREADED = True
FLASK_SSL_USED = False
FLASK_SSL_KEY = "key.pem"
FLASK_SSL_CERT = "cert.pem"

## SQL-Alchemy
SQL_ALCHEMY_DATABASE_URI = 'sqlite:///test.db'
SQL_ALCHEMY_DEBUG = False

## Hashlib
HASHLIB_PASSWORD_ENCODING = 'utf-8'
HASHLIB_ALGO = 'sha256'
HASHLIB_ALGO_ITERATIONS = 100000
HASHLIB_KEY_LENGTH = 128

# API_KEY_DURATION = 3 # in Days

## JWT_TOKEN
JWT_TOKEN_LOCATION = ["headers"]  # headers,cookies,query_string,json
JWT_HEADER_TYPE = ["Bearer"]
JWT_ACCESS_TOKEN_NAME = "access_token"
JWT_REFRESH_TOKEN_NAME = "refresh_token"
JWT_ACCESS_COOKIE_PATH = '/api/'
JWT_REFRESH_COOKIE_PATH = '/token/refresh'
JWT_COOKIE_CSRF_PROTECT = False
JWT_SECRET_KEY = 'Please change me, if used'  # Only used if JWT_SECRET_KEY_FILE_PATH doesn't exist
JWT_SECRET_KEY_FILE_PATH = 'jwtkey.txt'
JWT_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE', 'GET']
JWT_COOKIE_SECURE = True
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=365)
