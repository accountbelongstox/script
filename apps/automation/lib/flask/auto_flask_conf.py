<<<<<<< HEAD
from kernel.utils import file
=======
from pycore.utils import file
>>>>>>> origin/main

FLASK_NAME = "FlaskMain"
DEBUG = True
TESTING = False
SECRET_KEY = '\xba\x1c0\x85crl#\xfa\xa9[\xa3\xb4\x8c\xe2\xd4@l\xff\x92\x1f\xb6\xbc\xbb'  # 请替换为真实的密钥
PORT = 5000
SOCKET_PORT = 8000
<<<<<<< HEAD
STATIC_FOLDER = file.resolve_path('static', "apps/prompt/web")
=======
STATIC_FOLDER = file.resolve_path('static', "applications/prompt/web")
>>>>>>> origin/main
TEMPLATE_FOLDER = file.resolve_path('templates', "out/flask_router")
TEMP_FOLDER = file.resolve_path('tampermonkey', "out/flask_router")
AUTHENTICATIONS_PATHS = [""]

class Config:
    def get_config(self):
        config_dict = {
            'FLASK_NAME': FLASK_NAME,
            'DEBUG': DEBUG,
            'TESTING': TESTING,
            'SECRET_KEY': SECRET_KEY,
            'PORT': PORT,
            'SOCKET_PORT': SOCKET_PORT,
            'STATIC_FOLDER': STATIC_FOLDER,
            'TEMPLATE_FOLDER': TEMPLATE_FOLDER,
            'TEMP_FOLDER': TEMP_FOLDER,
            'AUTHENTICATIONS_PATHS': AUTHENTICATIONS_PATHS,
        }
        return config_dict

config = Config().get_config()
