# import os.path
from flask import request as flask_request, render_template
import pprint
from apps.task.task import task
# import itsdangerous
from kernel.base.base import Base
from kernel.practicals import flasktool

class Router(Base):
    likeFlaskApp = None

    def __init__(self, likeFlaskApp, config):
        self.likeFlaskApp = likeFlaskApp
        self.config = config

        # likeFlaskApp = {
        #     "login_manager": self._login_manager,
        #     "itsdangerous": itsdangerous,
        #     "wtforms": wtforms,
        #     "flask_wtf": flask_wtf,
        #     "url_for": url_for,
        #     "render_template": render_template,
        #     "flask_request": flask_request,
        #     "request": flask_request,
        #     "mimerender": mimerender,
        #     "redirect": redirect,
        #     "flask_login": flask_login,
        #     "session": session,
        #     "make_response": make_response,
        # }

        @likeFlaskApp.route('/', methods=['GET'])
        def index():
            remote_addr = flask_request.remote_addr
            self.success("flask_router:" + remote_addr)
            return f"flask_router run as ok,your IP {remote_addr}"
            # return render_template("index.html")  # manager_data={}

        @likeFlaskApp.route('/chat', methods=['GET', 'POST'])
        def post_chat():
            # remote_addr = likeFlaskApp.request.remote_addr
            # self.info(f"GET request from IP: {remote_addr}")
            texts = flasktool.get_request(likeFlaskApp, "texts")
            id = flasktool.get_request(likeFlaskApp, "id")
            done = flasktool.get_request(likeFlaskApp, "done")
            if done in [True, 'true']:
                missing_keys = []
                text_index = [key for key in texts.keys() if key.startswith("text_")]
                text_index = [int(key.split("_")[1]) for key in text_index]
                text_max = max(text_index, default=0)
                for i in range(text_max + 1):
                    key = f"text_{i}"
                    if key not in texts:
                        missing_keys.append(key)
                if missing_keys:
                    self.error("The following keys are missing:")
                    for key in missing_keys:
                        self.error(key)
                message = f"Because the completed submission has received the ,ID:{id}."
                self.success(message)
                task.set_complete_task(texts)
                return message
            else:
                message = f"Task live chat has been received.id:{id}"
                self.success(message)
                self.info(texts)
                return message

        @likeFlaskApp.before_request
        def before_request():
            # auth_urls = self._config.AUTHENTICATIONS_PATHS
            # cookies = flask_request.cookies
            # self.direct_login(self._app, "fail_not_cookie")
            pass

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

    def get_method(self, module, key):
        if module == None or key == None:
            return None
        tool = getattr(module, key)
        if tool == None:
            self.com_util.print_info(module)
            self.com_util.print_warn(f"class does not have method {key}")
        else:
            return tool
