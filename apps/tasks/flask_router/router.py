# import os.path
from flask import request as flask_request, render_template
from pycore.base.base import Base
from pycore.practicals_linux import flasktool
# from apps.tasks.provider.data_src import data_src
# from apps.tasks.oper.data_save import data_save
from datetime import datetime
from apps.tasks.provider.mock_data import mock
class Router(Base):
    likeFlaskApp = None
    current_id = None
    current_title = None

    def __init__(self, likeFlaskApp, config):
        self.likeFlaskApp = likeFlaskApp
        self.config = config

        @likeFlaskApp.route('/', methods=['GET'])
        def index():
            remote_addr = flask_request.remote_addr
            self.success("flask_router:" + remote_addr)
            return f"flask_router run as ok,your IP {remote_addr}"
            # return render_template("index.html")  # manager_data={}

        # @likeFlaskApp.route('/put_company', methods=['GET', 'POST'])
        # def put_company():
        #     title = flasktool.get_request(likeFlaskApp, "title")
        #     data_save.append_data(f"{title}\n")
        #     return {
        #         "status": "ok",
        #         "video_title": title,
        #     }

        @likeFlaskApp.route('/get_data', methods=['GET', 'POST'])
        def provider():
            # title = data_src.get_item()
            return mock.get_mock()

        # @likeFlaskApp.route('/get_key', methods=['GET', 'POST'])
        # def get_key():
        #     if self.current_title != None:
        #         self.warn(f"等待分析抓取 id: {self.id_value}", )
        #         self.warn(f"\t 公司: {self.compo_value}", )
        #         self.warn(f"\t 职位: {self.position_value}", )
        #         timestamp = int(datetime.timestamp(datetime.now())) * 1000
        #         difftime = timestamp - self.timestamp
        #         self.info(f"已耗时 {difftime }")
        #         if difftime > 20000:
        #             self.values[2] = self.values[2] + " 招聘"
        #         if difftime > 60000:
        #             title = f"{self.current_title},{self.url_value}"
        #             self.success(f"获取信息:", )
        #             self.success(f"\tid:{self.id_value}", )
        #             self.success(f"\t职位:{self.position_value}", )
        #             self.success(f"\t源网址官方:{self.url_value}", )
        #             self.current_title = None
        #             data_save.append_result(f"{title}\n")
        #         return {
        #             "status": False,
        #             "src": ",".join(self.values),
        #             "timestamp": self.timestamp,
        #             "diff_time": difftime
        #         }
        #     title = data_src.get_search()
        #     try:
        #         values = title.split(',')
        #         self.values = values
        #         self.id_value = values[0]
        #         self.url_value = values[1]
        #         self.position_value = values[2]
        #         self.compo_value = values[3]
        #         self.current_title = title
        #         self.timestamp = int(datetime.timestamp(datetime.now())) * 1000
        #         self.info(f"开始分析抓取源网址 id: {self.id_value}", )
        #         self.info(f"\t 职位: {self.position_value}", )
        #         self.info(f"\t 公司 {self.compo_value}", )
        #         return {
        #             "status": True,
        #             "src": title,
        #             "timestamp": self.timestamp
        #         }
        #     except Exception as e:
        #         return {
        #             "status": False,
        #             "message": f"An unexpected error occurred: {str(e)}",
        #             "timestamp": self.timestamp
        #         }

        # @likeFlaskApp.route('/put_result', methods=['GET', 'POST'])
        # def put_result():
        #     oriurl = flasktool.get_request(likeFlaskApp, "oriurl")
        #     if oriurl and self.current_title:
        #         title = f"{self.current_title},{oriurl}"
        #         self.success(f"成功:", )
        #         self.success(f"\tid:{self.id_value}", )
        #         self.success(f"\t职位:{self.position_value}", )
        #         self.success(f"\t源网址为:{oriurl}", )
        #         self.current_title = None
        #         data_save.append_result(f"{title}\n")
        #     else:
        #         self.warn(f"本次分析结果无效", )
        #         self.warn(f"\toriurl:{oriurl}", )
        #         self.warn(f"\tcurrent_title:{self.current_title}", )
        #     return {
        #         "status": "ok",
        #     }
