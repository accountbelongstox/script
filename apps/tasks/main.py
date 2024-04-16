import os
import os.path
import time

from apps.tasks.flask_router.config import config
from apps.tasks.flask_router.router import Router
from pycore.base.base import Base
from pycore.threads import FlaskThread
from pycore.utils import file

from pycore.dbmode.baseclass.dbcommon import DBCommon
from apps.tasks.provider.mock_data import mock
import json
from apps.tasks.provider.db_mysql import db

from sqlalchemy import Column, Integer, String  # 导入正确的数据类型


class Tasks(Base):
    current_screen_file = None
    default_prompts_dir = ".prompts"

    def __init__(self):
        pass

    def start(self):
        flask = FlaskThread(config=config, router=Router)
        flask.start()
        self.info("正在启动Tasks Flask..")

    def test_sql(self):
        # mysql_instance.get_columns('test')
        # tabname = "test"  # 你的表名
        # fields = {
        #     "id": Integer,
        #     "title": String(255),
        #     "date": String(255),
        #     "description": String(255),
        #     "descriptionText": String(255),
        #     "skills": String(255),
        #     "priority": String(255),
        #     "assignee": String(255),
        #     "path": String(255),
        #     "profit": String(255),
        #     "status": String(255)
        # }  # 你的字段名和类型
        # mysql_instance.create_table(tabname, fields)
        # mysql_instance.save("test",mock.get_mock())
        print(db)
        db.connect()
        db.get_columns('test')


        db.create_table(tabname,fields)


#         for task in mock.get_mock():
#             print("task",task)
#             mysql_instance.save("test",{'id': 1, 'title': 'Meeting with Shaun Park at 4:50pm', 'date': 'Aug, 07 2020', 'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi pulvinar feugiat consequat. Duis lacus nibh, sagittis "id" varius vel, aliquet non augue. Vivamus sem ante, ultrices at ex a, rhoncus ullamcorper tellus. Nunc iaculis eu ligula ac consequat. Orci varius natoque penatibus et magnis dis parturient montes, nascetur r"id"iculus mus. Vestibulum mattis urna neque, eget posuere lorem tempus non. Suspendisse ac turpis dictum, convallis est ut, posuere sem. Etiam imperdiet aliquam risus, eu commodo urna vestibulum at. Suspendisse malesuada lorem eu sodales aliquam.', 'descriptionText': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi pulvinar feugiat consequat. Duis lacus nibh, sagittis "id" varius vel, aliquet non augue. Vivamus sem ante, ultrices at ex a, rhoncus ullamcorper tellus. Nunc iaculis eu ligula ac consequat. Orci varius natoque penatibus et magnis dis parturient montes, nascetur r"id"iculus mus. Vestibulum mattis urna neque, eget posuere lorem tempus non. Suspendisse ac turpis dictum, convallis est ut, posuere sem. Etiam imperdiet aliquam risus, eu commodo urna vestibulum at. Suspendisse malesuada lorem eu sodales aliquam.', 'skills': '["javascript", "python"]', 'priority': 'medium', 'assignee': 'John Smith', 'path': '', 'profit': '￥1', 'status': ''}
# )
#             break












    # def test_mysql_connection(self):
    #     mysql_instance = Mysql()
    #     mysql_instance.connect()
    #     session = mysql_instance.session
    #     assert session is not None, "Database connection failed!"
    #     print("Database connection test passed.")
    #     # mysql_instance.create_table()
    #     #
    #     # for task in mock.get_mock():
    #     #     mysql_instance.create(task)
    #     result_dict = mysql_instance.read()
    #     print(result_dict)



    # Function to insert data into the table
    # def insert_data(self):
    #     # Load mock data from JSON file
    #     mock_data = mock.get_mock()
    #
    #     # Define table name
    #     table_name = "your_table_name"
    #
    #     # Save data to the table
    #     mysql.save(tabname=table_name, data=mock_data)
tasks = Tasks()
