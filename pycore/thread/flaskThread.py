import os.path, threading, re
from datetime import timedelta
import flask
from flask_socketio import SocketIO, emit, send, call
from flask import Flask as FlaskApp, url_for, request as flask_request, render_template, redirect, session, \
    make_response, has_request_context
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import flask_login
from geventwebsocket.handler import WebSocketHandler
# import logging
from logging.config import dictConfig
import flask_wtf
import wtforms
import mimerender
from flask_cors import CORS
# from  geventwebsocket.websocket import WebSocket,WebSocketError
# from  gevent.pywsgi import WSGIServer
mimerender = mimerender.FlaskMimeRender()
from gevent import pywsgi
import mimetypes
import itsdangerous
# from flask_jwt import JWT, jwt_required, current_identity
# from werkzeug.security import safe_str_cmp
# from livereload import Server
user_socket_dict = {}

class FlaskContainer():
    pass

class SocketContainer():
    def set_data(self, value):
        self.__dict__['data'] = value

    def get(self, key):
        return self.__dict__[key]

    pass

flask_global = FlaskContainer()
socket_global = SocketContainer()

class FlaskThread(threading.Thread):
    _app = None
    _app_run = False
    # __module = None
    __static_folder = None
    __template_folder = None
    __debug = True
    __loggin_level = "warn"
    __initialization = False

    def __init__(self, config, router=None,socket_router=None, callbacks=None, task_queue=None, public_queue=None):
        threading.Thread.__init__(self)
        self._task_queue = task_queue
        self._public_queue = public_queue
        self._router = router
        self._socket_router = socket_router
        self._config = config
        self.resultQueue = []
        self.is_alive = True

    def run(self):
        mimetypes.add_type('text/css', '.css')
        mimetypes.add_type('application/javascript', '.js')
        # mimetypes.add_type('application/json', '.json')
        self.init_flask()
        login_manager = self.packagingAPP()
        self.base_router(login_manager)
        self.set_loggin()
        self.socketio_init()
        self.startAsMain()

    def packagingAPP(self):
        if not self.__initialization:
            self._login_manager = flask_login.LoginManager()
            self._login_manager.init_app(self._app)
            attachments = {
                "login_manager": self._login_manager,
                "itsdangerous": itsdangerous,
                "wtforms": wtforms,
                "flask_wtf": flask_wtf,
                "url_for": url_for,
                "render_template": render_template,
                "flask_request": flask_request,
                "request": flask_request,
                "mimerender": mimerender,
                "redirect": redirect,
                "flask_login": flask_login,
                "session": session,
                "make_response": make_response,
            }
            for name, attach in attachments.items():
                is_attack = getattr(self._app, name, None)
                if is_attack == None:
                    setattr(self._app, name, attach)
            self.__initialization = True
        return self._login_manager

    def socketio_init(self):
        engineio_logger = False
        attachments = {
            "emit": emit,
            "send": send,
            "call": call,
        }
        for name, attach in attachments.items():
            is_attack = getattr(socket_global, name, None)
            if is_attack == None:
                setattr(socket_global, name, attach)
        self.socketio = SocketIO(self._app, cors_allowed_origins="*", async_mode='gevent',
                                 engineio_logger=engineio_logger, engineio_async_mode='gevent')

        @self.socketio.on('message')
        def on_message(*args):
            print(f"Client {flask_request.sid} connected.")
            namespace = flask_request.namespace
            print(f"Received message in namespace {namespace}")
            socket_json = self.to_json_force(args[0])
            module = socket_json.get('module')
            request_method = socket_json.get('method')
            result = {
                "module": module,
                "method": request_method,
            }
            if request_method == None:
                result["code"] = "-1"
                result[
                    "message"] = """Parameter Error,Example: {"module":"module_name","method":"method_name","data":{},}"""
                self.socketio.send(result)
                return
            data = socket_json.get('data')
            socket_global.set_data(data)
            if self._socket_router:
                result = self._socket_router.main(socket_global, module, request_method, "socket")
                self.socketio.send(result)
            else:
                print("socket")
                print(result)
            self.socketio.send(result)

    def to_json_force(self, json_str):
        json_str = self.to_json(json_str)
        if type(json_str) != dict:
            json_str = {}
        return json_str

    def startAsMain(self,):
        port = self._config["PORT"]
        print(f'Flask-successfully:\nstartup Flask app server. Listing port is {port}')
        # debian12 = pywsgi.WSGIServer(('0.0.0.0', port), self._app)
        # self.socketio.run(self._app,host="0.0.0.0",port=5000)
        server = pywsgi.WSGIServer(('0.0.0.0', port), self._app, handler_class=WebSocketHandler)
        server.serve_forever()

    def startAsThread(self,ComThread):
        if self._app_run == True:
            print(f"flask is already running.")
            return
        com_th = ComThread(target=self.startAsMain)
        com_th.start()

    def init_flask(self, ):
        main_name = self._config["FLASK_NAME"]
        # Flask设置项: static_url_path=None,static_folder='static',static_host=None,host_matching=False,subdomain_matching=False,template_folder='templates',
        STATIC_FOLDER = self._config["STATIC_FOLDER"]
        TEMPLATE_FOLDER = self._config["TEMPLATE_FOLDER"]
        SECRET_KEY = self._config["SECRET_KEY"]
        self._app = FlaskApp(main_name, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
        CORS(self._app)
        self._app.secret_key = SECRET_KEY
        self._app.permanent_session_lifetime = 60
        self._app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
        self._app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=1)
        self._app.config['TRAP_HTTP_EXCEPTIONS'] = False
        self._app.send_file_max_age_default = timedelta(seconds=1)
        self._app.permanent_session_lifetime = timedelta(seconds=1)
        self._app.config['DEBUG'] = self._config["DEBUG"]

    def set_loggin(self):
        if self.__debug == True:
            self._app.logger.removeHandler(flask.logging.default_handler)
            dictConfig({
                'version': 1,
                # 'formatters': {'default': {
                #     'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                # }},
                # 'handlers': {'wsgi': {
                #     'class': 'logging.StreamHandler',
                #     'stream': 'ext://flask_router.logging.wsgi_errors_stream',
                #     'formatter': 'default'
                # }},
                'root': {
                    'level': self.__loggin_level.upper(),
                    # 'handlers': ['wsgi']
                }
            })

    def base_router(self,login_manager):
        @login_manager.request_loader
        def request_loader(request):
            pass

        if self._router:

            self._router(self._app,self._config)

    def set(self, name, data):
        self.__dict__[name] = data

    def setargs(self, args):
        self.args = args

    def done(self):
        if self.is_alive == False:
            return True
        return False
