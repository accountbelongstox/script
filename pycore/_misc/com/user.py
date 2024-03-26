# import json
# import re

from pycore.base.base import Base
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange
# from itsdangerous import BadSignature, SignatureExpired, Serializer

# from flask_jwt import TimedJSONWebSignatureSerializer

# from flask_jwt import JWT, jwt_required, current_identity
# from werkzeug.security import safe_str_cmp
# 配置 Flask-JWT
# app.config['SECRET_KEY'] = 'super-secret-key'
# app.config['JWT_AUTH_URL_RULE'] = '/auth'  # 自定义认证 URL
# app.config['JWT_EXPIRATION_DELTA'] = 3600  # 设置 token 过期时间，单位为秒

# Flask-JWT 验证回调
# def authenticate(username, password):
#     user = find_user_by_username(username)
#     if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
#         return user
#
# # Flask-JWT 身份回调
# def identity(payload):
#     user_id = payload['identity']
#     return find_user_by_id(user_id)
#
# jwt = JWT(app, authenticate, identity)
#
# # 保护的路由
# @app.route('/protected', methods=['GET'])
# @jwt_required()
# def protected():
#     return jsonify({'message': 'This is curses.pyc protected route.', 'current_user': current_identity.username})
#

# import json

class User(Base, FlaskForm):
    login_validate = None
    __is_init_deliver_sql = True

    def __init__(self, args=None):
        pass

    def main(self, args):
        pass

    def register_user(self, flask):
        user = flask.flask_request.form.get('user')
        pwd = flask.flask_request.form.get('pwd')
        register_time = self.com_util.create_time()
        register_ip = flask.flask_request.remote_addr
        if None in [user, pwd]:
            result = f"register-fail:ip:{register_ip} / user:{user} / pwd:{pwd},because: not user or pwd."
            self.com_util.print_warn(result)
            return flask.redirect("/register?info=fail_not_user_or_pwd")
        account_info = {
            "user": user,
            "pwd": pwd,
            "role": 0,
            "trans_count": 0,
            "read": 0,
            "is_delete": 0,
            "register_time": register_time,
            "register_ip": register_ip,
            "time": register_time,
        }
        self.com_util.print_info(account_info)
        result_id = self.com_db.save("user", account_info, result_id=True)
        self.is_init_deliver_sql(result_id)
        if result_id == 0:
            result_id = f"register-fail:ip:{register_ip} / user:{user} / pwd:***, result:{result_id}."
            self.com_util.print_warn(result_id)
            return flask.redirect(f"/register?info=fail_user_exists&account={user}")
        # result = self.com_util.print_info(result)
        # self.copy_dictionarytouser(flask_router, result_id)
        return flask.redirect(f"/login?info=success&account={user}")

    def get_users(self, user, password):
        result = self.com_db.read("user", {
            "user": user,
            "password": password,
        }, )
        return result

    def is_login_from_cookie(self, flask, username):
        if username in flask.flask_request.cookies:
            username = flask.flask_request.cookies.get('username')
            return True
        else:
            return False

    def get_current_user(self, flask):
        return self.com_userinfo.get_current_user(flask)

    def get_current_id(self, flask):
        return self.com_userinfo.get_current_id(flask)

    def login(self, flask):
        user = self.com_flask.get_request(flask,"user")
        pwd = self.com_flask.get_request(flask,"pwd")
        json = self.com_flask.get_request(flask,"json")
        if None in [user, pwd]:
            result = f"login-fail: not user or pwd. user:{user}"
            self.com_util.print_warn(result)
            if json == True:
                return self.com_util.print_result(data=result)
            else:
                return flask.redirect("/login?info=fail_not_user_or_pwd")

        user_info = self.com_userinfo.query_user(user, pwd)
        if user_info.id == None:
            result = f"login-fail: user or pwd error. user:{user}"
            self.com_util.print_warn(result)
            if json == True:
                return self.com_util.print_result(data=result)
            else:
                return flask.redirect("/login?info=fail_user_or_pwd_error")
        session_info = {
            "userid": user_info.id,
            "username": user_info.username
        }
        flask.session["userinfo"] = session_info
        flask.session.modified = True
        # user = flask_router.login_manager.user_loader(user_info)
        # self.com_dictionary.get_dictionary_map_ids(user)
        # if user:
        # flask_router.flask_login.login_user(user)
        self.com_util.print_info(f"user : {user_info.username} login successfully, user-id:{user_info.id}", )
        response = self.login_successanddirectory(flask, session_info, 'index.html')
        self.com_flask.set_session(flask,session_info)
        if json == True:
            result = self.com_util.print_result(data=session_info)
            return result
        return response

    def get_userinfobysession(self, flask):
        session = self.com_flask.get_session(flask)
        result = self.com_util.print_result(data=session)
        return result

    def login_successanddirectory(self, flask, userinfo, direct_url="/"):
        response = self.com_flask.set_cookie(flask, {
            "userinfo": userinfo
        }, rend_str=f"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
            <html>
            <script>alert('登陆成功,请等待网页自动跳转.');window.location.href='{direct_url}';</script>
            <title>登陆成功(如没有自动跳转,请手动点击)</title>
            <body>
            <h1>登陆成功(如没有自动跳转,请手动点击)</h1>
            <p>
            <a style="align-content: center; font-size: 14px;" href="{direct_url}">请手动点击跳转</a>
            </body>
            </html>
            """)
        return response

    # @login_required
    def success(self, flask, ):
        return "Welcome %s!" % flask.session["user"]

    def direct_login(self, flask, info="fail_login_expire"):
        return flask.redirect(f"/login?info={info}")

    # @login_required
    def logout(self, flask, ):
        flask.logout_user()
        response = flask.make_response('Successfully logged out')
        self.com_flask.set_cookie(flask, 'token', '')  # , secure=True, httponly=True),secure=True, httponly=True)
        return response

    def is_login_from_session(self, flask, username):
        # 检查用户是否已登录
        if username in flask.session:
            username = flask.session["username"]
            # 更新会话的最后访问时间
            flask.session.modified = True
            return True
        else:
            return False

    def is_init_deliver_sql(self,id):
        if id == 1 and self.__is_init_deliver_sql != False:
            self.__is_init_deliver_sql = True
            return True
        else:
            self.__is_init_deliver_sql = False
            return  False

    def get_singleid(self, user):
        try:
            userid = user.id if user.id else None
        except:
            userid = user
        if userid == None: userid = user
        return userid

    def add_groupmaptouser(self, userid, user_gtu_map_table):
        groups_mapstr = self.com_dictionary.get_groups_mapstr()
        result = self.com_db.update(user_gtu_map_table, {"group_map": groups_mapstr}, {"userid": userid})
        return result

    def is_usergroup_map(self, user_gtu_map):
        if len(user_gtu_map) == 0:
            return False
        user_gtu_map = user_gtu_map[0]
        group_map = user_gtu_map[3]
        if group_map in [None, '']:
            return False
        return True

class LoginForm(FlaskForm):
    user = StringField('user', validators=[DataRequired()])
    pwd = StringField('pwd', validators=[DataRequired()])
