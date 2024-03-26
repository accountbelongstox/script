from pycore._base import *
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()


# class Userinfo(Base,UserMixin,db.Model):
class Userinfo(Base,UserMixin):
    __user_table = 'user'
    def __init__(self,args=None,id=None,username=None,phone=None,pwd=None,role=None,trans_count=None,last_login=None,last_time=None,register_ip=None,read=None,time=None):
        self.id = id
        self.username = username
        self.phone = phone
        self.pwd = pwd
        self.role = role
        self.trans_count = trans_count
        self.last_login = last_login
        self.last_time = last_time
        self.register_ip = register_ip
        self.read = read
        self.time = time
        pass
    @property
    def is_authenticated(self):
        if self.id != None:
            return True
        return False

    @property
    def is_active(self):
        if self.id != None:
            return True
        return False

    @property
    def is_anonymous(self):
        if self.id == None:
            return True
        return False

    # @property
    def get_id(self):
        return str(self.id)

    def get_current_user(self,flask):
        cookie_key = self.com_config.get_cookie_key()
        if cookie_key not in flask.flask_request.cookies:
            return None
        cookie = self.com_flask.get_cookie(flask)
        userinfo = cookie.get('userinfo')
        user = userinfo.get('username')
        if userinfo == None or user == None:
            return None
        else:
            return user
    def get_current_id(self,flask):
        cookie_key = self.com_config.get_cookie_key()
        if cookie_key not in flask.flask_request.cookies:
            return None
        cookie = self.com_flask.get_cookie(flask)
        userinfo = cookie.get('userinfo')
        user = userinfo.get('userid')
        if userinfo == None or user == None:
            return None
        else:
            return user

    def get_user(self, userid):
        condition = {
            "user": userid
        }
        user_info = self.com_db.read(self.__user_table, condition,print_sql=True)
        return self.set_user(user_info)

    def query_user(self, username,pwd):
        user_query =  {
            "user": str(username),
            "pwd": str(pwd),
        }
        user_info = self.com_db.read(self.__user_table,user_query,result_object=True)
        print('user_info',user_info)
        return self.set_user(user_info)

    def set_user(self,users):
        if len(users) > 0:
            user_info = users[0]
            id = user_info.get('id')
            username = user_info.get('user')
            phone = user_info.get('user')
            pwd = user_info.get('pwd')
            role = user_info.get('role')
            trans_count = user_info.get('trans_count')
            last_login = user_info.get('time')
            last_time = user_info.get('register_time')
            register_ip = user_info.get('register_ip')
            read = user_info.get('read')
            time = user_info.get('time')
            return Userinfo(id=id, username=username, phone=phone, pwd=pwd, role=role, trans_count=trans_count, last_login=last_login,
                     last_time=last_time, register_ip=register_ip, read=read, time=time)
        return self

