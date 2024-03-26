import os.path, threading, re
import time
from datetime import timedelta
from pycore._base import *
import flask
from flask_socketio import SocketIO, emit, send, call
from flask import Flask as FlaskApp, url_for, request as flask_request, render_template, redirect, session, \
    make_response, escape, has_request_context
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import flask_login
from geventwebsocket.handler import WebSocketHandler
import logging
from logging.config import dictConfig
from logging.handlers import SMTPHandler
import flask_wtf
import wtforms
import itsdangerous
# from flask_sqlalchemy import SQLAlchemy
import mimerender
from flask_cors import CORS

# from  geventwebsocket.websocket import WebSocket,WebSocketError
# from  geventwebsocket.handler import WebSocketHandler
# from  gevent.pywsgi import WSGIServer
# import json
mimerender = mimerender.FlaskMimeRender()
from gevent import pywsgi

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


import mimetypes

flask_global = FlaskContainer()
socket_global = SocketContainer()


class FlaskThread(threading.Thread, Base):
    _app = None
    _app_run = False
    # __module = None
    __static_folder = None
    __template_folder = None
    __debug = True
    __loggin_level = "warn"

    def __init__(self, args, target=None, group_queue=None, public_queue=None, thread_id=None, thread_name=None,
                 daemon=False):
        threading.Thread.__init__(self, name=thread_name, daemon=daemon)
        self.__group_queue = group_queue
        self.__public_queue = public_queue
        self.__thread_id = thread_id
        self.task = args.get('task')
        # self.__module = args.get('module')
        setattr(self, "control", args.get('module'))
        self.target = target
        self.args = args
        self.thread_name = thread_name
        self.resultQueue = []
        self.is_alive = True

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        control = getattr(self, 'control')
        self.set_mimetypes()
        self.bind(control, run=False)
        self.initialization()
        self.socketio_init()
        self.flask_run()
        pass

    def set_mimetypes(self):
        mimetypes.add_type('text/css', '.css')
        mimetypes.add_type('application/javascript', '.js')

    def initialization(self):
        global flask_global
        if self.__initialization == True:
            return

        login_manager = flask_login.LoginManager()
        login_manager.init_app(self._app)

        @login_manager.user_loader
        def load_user(user_id):
            print("load_user user_id", user_id)
            return self.com_userinfo.get_user(user_id)

        @login_manager.request_loader
        def request_loader(request):
            pass

        attachments = {
            "login_manager": login_manager,
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
            "escape": escape,
        }
        for name, attach in attachments.items():
            is_attack = getattr(self._app, name, None)
            if is_attack == None:
                setattr(self._app, name, attach)
        # 初始化完毕
        self.__initialization = True

    def socketio_init(self):
        global socket_global
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
            socket_json = self.com_string.to_json_force(args[0])
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
            result = self.find_moduleandexec(socket_global, module, request_method, "socket")
            self.socketio.send(result)

    def flask_run(self):
        if self._app_run == True:
            print(f"flask_router is already running.")
            return
        network_th = self.com_thread.create_thread(thread_type="com", target=self.flask_init)
        network_th.start()

    def configure_flask(self, module, run):
        # self.__module = module
        setattr(self, "control", module)
        main_name = str(module).strip("<")
        split_text = re.compile(r"\s+")
        main_name = re.split(split_text, main_name)[0]
        main_name_split = main_name.split(".")[0:-1]
        main_name = ".".join(main_name_split)
        # Flask设置项: import_name,static_url_path=None,static_folder='static',static_host=None,host_matching=False,subdomain_matching=False,template_folder='templates',
        # instance_path=None,instance_relative_config=False,root_path=None
        static_folder = self.com_config.get_global("flask_static_folder")
        self.__static_folder = static_folder
        template_folder = self.com_config.get_global("flask_template_folder")
        self.__template_folder = template_folder
        self._app = FlaskApp(main_name, static_folder=static_folder, template_folder=template_folder)
        CORS(self._app)
        self.set_loggin()
        # 设置秘钥
        self._app.secret_key = "\xba\x1c0\x85crl#\xfa\xa9[\xa3\xb4\x8c\xe2\xd4@l\xff\x92\x1f\xb6\xbc\xbb"
        # 设置会话的有效时间（秒）
        self._app.permanent_session_lifetime = 60
        # 禁用Flask 缓存
        self._app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
        self._app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=1)
        self._app.config['TRAP_HTTP_EXCEPTIONS'] = False
        self._app.send_file_max_age_default = timedelta(seconds=1)
        self._app.permanent_session_lifetime = timedelta(seconds=1)
        self._app.config['DEBUG'] = True
        if run:
            self.flask_run()
            self._app_run = True

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
        mail_handler = SMTPHandler(
            mailhost=self.com_config.get_config('mail', 'mailhost'),
            fromaddr=self.com_config.get_config('mail', 'fromaddr'),
            toaddrs=self.com_config.get_config('mail', 'toaddrs'),
            subject=self.com_config.get_config('mail', 'subject')
        )
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        if not self._app.debug:
            self._app.logger.addHandler(mail_handler)
        # class RequestFormatter(logging.Formatter):
        #     flask_router = None
        #     def set_flask(self,flask_router):
        #         self.flask_router = flask_router
        #     def format(self, record):
        #         if has_request_context():
        #             record.url = self.flask_router.request.url
        #             record.remote_addr = self.flask_router.request.remote_addr
        #         else:
        #             record.url = None
        #             record.remote_addr = None
        #         return super().format(record)
        # formatter = RequestFormatter(
        #     '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        #     '%(levelname)s in %(module)s: %(message)s'
        # )
        # formatter.set_flask(self._app)
        # self._app.logging.default_handler.setFormatter(formatter)
        # self._app.logging.default_handler.setFormatter(formatter)

    def is_authentications_path(self):
        authenticated = ["index.html", "index", "", "api", "api.html"]
        path_parse = self.com_http.urlparse(flask_request.path)
        path = path_parse.path.strip('/')
        url_start = path.split('/')[0]
        if url_start in authenticated:
            if url_start == 'api':
                key = self.com_flask.get_request(self._app, "key")
                if key != None:
                    allow_execute = self.compare_execution_function_keys(key)
                    if allow_execute == True:
                        # API验证成功的时候不需要验证该URL
                        return False
            return True
        return False

    def bind(self, module, run=True):
        global flask_global
        self.configure_flask(module, run)

        @self._app.before_request
        def before_request():
            self.com_flask.expire_session(self._app)
            authentications_path = self.is_authentications_path()
            if authentications_path == True:
                # 在每个请求之前检查cookie中的签名
                cookie_key = self.com_config.get_cookie_key()
                if cookie_key not in flask_request.cookies:
                    return self.com_user.direct_login(self._app, "fail_not_cookie")
                else:
                    try:
                        token = self.com_flask.get_cookie(self._app)
                        userinfo = token.get('userinfo')
                        user = userinfo.get('username')
                        if userinfo == None or user == None:
                            return self.com_user.direct_login(self._app, "fail_not_cookie_user_user")
                    except itsdangerous.SignatureExpired:
                        return self.com_user.direct_login(self._app, "fail_signature_expired")
                    except itsdangerous.BadSignature:
                        return self.com_user.direct_login(self._app, "fail_bad_signature")
            elif type(authentications_path) == str:
                return authentications_path
            else:
                pass

        @self._app.route('/<path:path>', methods=['GET', 'POST', 'PROPFIND', 'MKCOL'])
        def flask_route(path):
            remote_addr = flask_request.remote_addr
            path_parse = self.com_http.urlparse(path)
            url_path = path_parse.path
            request_method = self.com_flask.get_request(self._app, "method")
            if request_method != None:
                self.set_flask_parameter("path", path)
                module = self.com_flask.get_request(self._app, "module")
                # self.com_util.print_info(f"address {remote_addr} visit api for method:{request_method} of module:{module}.")
                return self.find_moduleandexec(self._app, module, request_method, "flask_router")
            else:
                splitext = os.path.splitext(url_path)
                suffix = splitext[1]
                if suffix in [".html", ".htm", ""]:
                    if suffix == "":
                        url_path = url_path + ".html"
                    route_html = self.get_template_dir(url_path)
                    if self.com_file.isfile(route_html):
                        return render_template(url_path)
                return render_template('404.html')

        @self._app.route('/')
        def index():
            cookie = self.com_flask.get_cookie(self._app)
            print("cookie", cookie)
            remote_addr = flask_request.remote_addr
            self.com_util.print_info(f"address {remote_addr} visit to /.")
            return render_template("index.html")  # manager_data={}

    def find_moduleandexec(self, app, module, request_method, first="flask_router"):
        if not module:
            module = "control"
        if module == 'qt':
            controllers = self.load_module.global_modes['qt']['controller']
            result = [d for d in controllers if getattr(d, request_method) != None]
            if len(result) > 0:
                module = result[-1]
                method_exec = self.get_method(module, request_method)
                parameter_names = self.com_util.get_parameter(method_exec, info=False)
                if (first not in parameter_names):
                    function_not_parameter_modified_not_executed = f"The function {request_method} cannot be executed without being modified by the flask_router parameter."
                    return self.com_util.print_warn(function_not_parameter_modified_not_executed)
                return method_exec(flask=app)
            else:
                return self.com_util.print_result(f"{module} method {request_method} does not exist")

        module = getattr(self, module)
        method_exec = self.get_method(module, request_method)
        if method_exec == None:
            return self.com_util.print_result(f"method {request_method} does not exist")
        # 对于没有修饰flask参数的方法将无法执行
        parameter_names = self.com_util.get_parameter(method_exec, info=False)
        if (first not in parameter_names):
            function_not_parameter_modified_not_executed = f"The function {request_method} cannot be executed without being modified by the flask_router parameter."
            return self.com_util.print_warn(function_not_parameter_modified_not_executed)
        return method_exec(flask=app)

    def get_template_dir(self, filename=None):
        control_dir = self.load_module.get_control_dir()
        if filename == None:
            filename = ""
        template_folder = os.path.join(control_dir, self.__template_folder)
        filename = os.path.join(template_folder, filename)
        return filename

    def set_flask_parameter(self, key, value):
        setattr(self._app, key, value)

    def flask_init(self, args=None):
        port = self.com_config.get_global('flask_port')
        self.com_util.print_info(f'Flask-successfully:\nstartup Flask app server. Listing port is {port}')
        self.com_util.get_parameter(self._app.run)
        self.com_util.get_parameter(pywsgi.WSGIServer)
        # server = pywsgi.WSGIServer(('0.0.0.0', port), self._app)
        # self.socketio.run(self._app,host="0.0.0.0",port=5000)
        # print(f'\n')
        server = pywsgi.WSGIServer(('0.0.0.0', port), self._app, handler_class=WebSocketHandler)
        server.serve_forever()

    def get_method(self, module, key):
        if module == None or key == None:
            return None
        tool = getattr(module, key)
        if tool == None:
            self.com_util.print_info(module)
            self.com_util.print_warn(f"class does not have method {key}")
        else:
            return tool

    def compare_execution_function_keys(self, execute_function_key):
        if execute_function_key == self.com_config.get_global('execute_function_key'):
            return True
        else:
            return False

    def set(self, name, data):
        self.__dict__[name] = data

    def setargs(self, args):
        self.args = args

    def done(self):
        if self.is_alive == False:
            return True
        return False

    def result(self):
        while self.done() == False:
            self.com_util.print_warn(f"waiting for ComThread return.")
        resultQueue = self.resultQueue
        self.resultQueue = []
        return resultQueue
