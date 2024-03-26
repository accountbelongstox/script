# import os.path
from flask import request as flask_request, render_template
from pycore._base import Base
from apps.dy_scratch.oper.down import down
from pycore.practicals import flasktool


class Router(Base):
    likeFlaskApp = None

    def __init__(self, likeFlaskApp, config):
        self.likeFlaskApp = likeFlaskApp
        self.config = config

        @likeFlaskApp.route('/', methods=['GET'])
        def index():
            remote_addr = flask_request.remote_addr
            self.success("flask_router:" + remote_addr)
            return f"flask_router run as ok,your IP {remote_addr}"
            # return render_template("index.html")  # manager_data={}

        @likeFlaskApp.route('/video', methods=['GET', 'POST'])
        def post_title():
            title = flasktool.get_request(likeFlaskApp, "title")
            video_title = down.auto_save_click(title)
            return {
                "status": "ok",
                "video_title": video_title,
            }

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
