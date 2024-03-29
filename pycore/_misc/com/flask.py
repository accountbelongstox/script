import os

from pycore.base.base import Base
from flask_wtf import FlaskForm
from datetime import datetime, timedelta
import os
# from wtforms import StringField, SubmitField
# from wtforms.validators import DataRequired
from itsdangerous import  BadSignature, SignatureExpired,Serializer
# from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired
vtr_session = {}
# import user_agent
from user_agent import generate_user_agent, generate_navigator

class Flask(Base,FlaskForm):
    cookie_expires = 365 # day are all end.
    __session_expires = 60*60*24*30
    def __init__(self,args):
        pass

    def set_cookie(self,flask,user_info,rend_html=None,rend_str='Success logged.'):
        serializer = Serializer(flask.config['SECRET_KEY'])
        token = serializer.dumps(user_info)#.decode('utf-8')
        if rend_html != None:
            rend_html = flask.render_template(rend_html)
            resp = flask.make_response(rend_html)
        else:
            resp = flask.make_response(rend_str)

        cookie_key = self.com_config.get_cookie_key()
        expires = datetime.now()
        expires = expires + timedelta(days=self.cookie_expires)
        resp.set_cookie(cookie_key, token,expires=expires)
        return resp

    def get_cookie(self,flask,key=None):
        cookie_key = self.com_config.get_cookie_key()
        token = flask.flask_request.cookies.get(cookie_key)
        if not token:
            return None
        # 创建一个序列化器，用于解密token
        serializer = Serializer(flask.config['SECRET_KEY'])
        try:
            user_info = serializer.loads(token)#.encode('utf-8'))
            if key != None:
                user_info = user_info[user_info]
            return user_info
        except:
            # 如果解密失败，则表示token不正确或已过期，返回提示信息
            # self.com_util.pring_warn('Invalid or expired token. Please log in again.')
            return None

    def get_session(self, flask):
        return flask.session
    def qual_browser(self,flask):
        session = flask.session
        request = flask.request
        session['user_agent'] = request.headers.get('User-Agent')
        session['ip'] = request.remote_addr
        return flask.session

    def is_session(self,flask):
        session_file = self.get_vtrsessionfile(flask)
        session_dir = self.com_config.get_public(f'session/')
        session_include = self.com_file.dir_include(session_dir,session_file)
        return session_include

    def expire_session(self,flask):
        session_dir = self.com_config.get_public(f'session/')
        datestamp = self.com_util.create_timestamp()
        for file_name in os.listdir(session_dir):
            session_datestamp = self.get_sessiontime(flask)
            if session_datestamp == None:
                continue
            diff_timestamp = datestamp - session_datestamp
            if diff_timestamp > self.__session_expires:
                file_path = os.path.join(session_dir, file_name)
                os.remove(file_path)

    def get_sessiontime(self,flask):
        session_findfile = self.find_sessionfile(flask)
        if session_findfile == None:
            return session_findfile
        name_without_extension = session_findfile.rsplit(".", 1)[0]  # 去除后缀的文件名部分
        name_parts = name_without_extension.split("_")  # 划分文件名部分
        last_part = name_parts[-1]  # 获取最后一项
        return int(last_part)

    def set_session(self, flask,content=None):
        session_findfile = self.find_sessionfile(flask)
        if session_findfile == None:
            datestamp = self.com_util.create_timestamp()
            session_findfile = self.get_vtrsessionfilehead(flask,datestamp)
        origin_session = self.get_session(flask)
        if len(origin_session) > 0:
            origin_session = self.com_string.to_json(origin_session)
        else:
            origin_session = {}
        if content != None:
            content = self.com_string.to_json(content)
        else:
            content = {}
        for key,value in content.items():
            origin_session[key] = value

        origin_session = self.com_string.json_tostring(origin_session)
        self.com_file.save(session_findfile,origin_session,overwrite=True)

    def get_session(self, flask,):
        session_findfile = self.find_sessionfile(flask)
        if session_findfile == None:
            return {}
        else:
            origin_session = self.com_file.read(session_findfile)
            if len(origin_session) > 0:
                origin_session = self.com_string.to_json(origin_session)
            else:
                origin_session = {}
            return origin_session

    def find_sessionfile(self,flask):
        session_file = self.get_vtrsessionfile(flask)
        session_dir = self.com_config.get_public(f'session/')
        session_findfile = self.com_file.dir_find(session_dir,session_file)
        if session_findfile != None:
            session_findfile = os.path.join(session_dir,session_findfile)
        return session_findfile

    def get_vtrsessionfile(self,flask):
        request = flask.request
        ip = request.remote_addr
        ip_md5 = self.com_string.md5(ip)
        user_agent = request.headers.get('User-Agent')
        user_agent_md5 = self.com_string.md5(user_agent)
        return f'{ip_md5}_{user_agent_md5}'

    def get_vtrsessionfilehead(self,flask,timestamp=""):
        session_file = self.get_vtrsessionfile(flask)
        session_filedir = self.com_config.get_public(f'session/{session_file}_{timestamp}.session')
        return session_filedir

    def get(self,flask=None,key=None,default=None):
        if not flask:
            return default
        if flask.flask_request.is_json:
            data = flask.flask_request.get_json()
            val = data.get(key)
        else:
            val = flask.flask_request.args.get(key)
            if val == None:
                val = flask.flask_request.form.get(key)
        if val ==None:
            val = default
        val = self.com_string.to_value(val)
        return val

    def response(self,flask,data=None):
        if flask == None:
            return data
        else:
            return self.com_util.print_result(data=data)