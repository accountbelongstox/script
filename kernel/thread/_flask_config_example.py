import os
from pycore.utils import file


class Config:
    FLASK_NAME = "FlaskMain"
    DEBUG = False
    TESTING = False
    SECRET_KEY = '\xba\x1c0\x85crl#\xfa\xa9[\xa3\xb4\x8c\xe2\xd4@l\xff\x92\x1f\xb6\xbc\xbb'  # 请替换为真实的密钥
    PORT = 5000
    SOCKET_PORT = 8000
    STATIC_FOLDER = file.resolve_path('static', "apps/prompt/web")
    TEMPLATE_FOLDER = file.resolve_path('templates', "out/flask_router")
    TEMP_FOLDER = file.resolve_path('tampermonkey', "out/flask_router")
    AUTHENTICATIONS_PATHS = [""]


config = Config()
