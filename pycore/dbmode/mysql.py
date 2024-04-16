
from pycore.dbmode.baseclass.dbcommon import DBCommon
from sqlalchemy import create_engine,Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
import json
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# class YourModel(Base):
#     __tablename__ = 'test_sql'
#
#     id = Column(Integer, primary_key=True)
#     title = Column(String(255))
#     date = Column(String(255))
#     description = Column(String(255))
#     dateption = Column(String(255))  # 添加dateption字段
#     descriptionText = Column(String(255))
#     skills = Column(String(255))  # 如果是列表形式的数据，你可能需要使用JSON字段或者创建关联表
#     priority = Column(String(255))
#     assignee = Column(String(255))
#     path = Column(String(255))
#     profit = Column(String(255))
#     status = Column(String(255))

class Mysql(DBCommon):
    session = None
    config = {}
    tables = {}
    def __init__(self,config,tables):
        self.config = config
        self.tables = tables
        pass

    def main(self, args):
        self.init_database()

    def connect(self):
        if self.session != None:
            return self.session
        username = self.config.get('mysql_user')
        password = self.config.get('mysql_password')
        host = self.config.get('mysql_host')
        port = self.config.get('mysql_port')
        db_name = self.config.get('mysql_database')
        if username and password:
            engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}')
        else:
            engine = create_engine(f'mysql+pymysql://{host}:{port}/{db_name}')
        print("engine",engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        self.session = session
        self.engine = engine
        super().__init__(session, engine)



    # def create_table(self):
    #     Base.metadata.create_all(self.engine)
    # def create(self, data):
    #     new_entry = YourModel(**data)
    #     self.session.add(new_entry)
    #     self.session.commit()

    # def read(self):
    #     data_list = self.session.query(YourModel).all()
    #     data_dict = {data.id: {
    #         'title': data.title,
    #         'date': data.date,
    #         'description': data.description,
    #         'dateption': data.dateption,
    #         'descriptionText': data.descriptionText,
    #         'skills': data.skills,
    #         'priority': data.priority,
    #         'assignee': data.assignee,
    #         'path': data.path,
    #         'profit': data.profit,
    #         'status': data.status
    #     } for data in data_list}
    #     return data_dict
    # def read(self):
    #     data_objects = self.session.query(YourModel).all()
    #     data_list = [data.__dict__ for data in data_objects]
    #     # 移除'_sa_instance_state'键，它是 SQLAlchemy 内部属性，不需要序列化
    #     for data in data_list:
    #         data.pop('_sa_instance_state', None)
    #     return json.dumps(data_list)
    #
    # def update(self, id_, data):
    #     entry = self.session.query(YourModel).filter_by(id=id_).first()
    #     for key, value in data.items():
    #         setattr(entry, key, value)
    #     self.session.commit()
    #
    # def delete(self, id_):
    #     entry = self.session.query(YourModel).filter_by(id=id_).first()
    #     self.session.delete(entry)
    #     self.session.commit()