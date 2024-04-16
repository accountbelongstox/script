import datetime
from sqlalchemy import inspect,Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from abc import ABC, abstractmethod
from sqlalchemy.ext.declarative import declarative_base
SqlalchemyBase = declarative_base()

class DBBase(ABC):
    # @abstractmethod
    # def connect(self):
    #     pass
    # @abstractmethod
    # def main(self):
    #     pass
    #
    # @abstractmethod
    # def save(self):
    #     pass
    #
    # @abstractmethod
    # def read(self):
    #     pass
    #
    # @abstractmethod
    # def update(self):
    #     pass
    # @abstractmethod
    # def delete(self):
    #     pass
    # @abstractmethod
    # def exist_table(self):
    #     pass
    # @abstractmethod
    # def exist_field(self):
    #     pass
    # @abstractmethod
    # def modify_field(self):
    #     pass
    # @abstractmethod
    # def init_database(self):
    #     pass
    # @abstractmethod
    # def create_table(self):
    #     pass
    # @abstractmethod
    # def close(self):
    #     pass
    #
    # @abstractmethod
    # def commit(self):
    #     pass
    #
    # @abstractmethod
    # def count(self):
    #     pass


    def get_tablemaps(self, engine):
        # 使用 SQLAlchemy 的 inspect 方法获取数据库中所有的表名
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        tablemaps = {}
        # 遍历表名，使用 inspect 方法获取表的元数据信息并存储到 tablemaps 中
        for table_name in table_names:
            tablemaps[table_name] = inspector.get_columns(table_name)

        return tablemaps

    def create_table_class(self, tabname, fields):
        # 定义表格类的属性字典
        table_attrs = {'__tablename__': tabname}

        # 根据字段信息构建表格类的属性
        for field_name, field_type in fields.items():
            # 假设第一个字段是主键
            if 'id' in field_name.lower():
                table_attrs[field_name] = Column(Integer, primary_key=True)
            else:
                table_attrs[field_name] = Column(field_type)

        # 使用 type() 动态创建表格类
        table_class = type(tabname.capitalize(), (SqlalchemyBase,), table_attrs)

        return table_class

    def escape_andsetdate(self, tabname, data):
        # 假设需要设置日期的字段名为 'created_at'，可以根据实际情况进行修改
        date_field = 'date'

        # 转义特殊字符（如果需要）
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = self.escape_string(value)

        # 设置日期字段（如果需要）
        if date_field not in data:
            data[date_field] = datetime.datetime.now()

        return data

    def escape_string(self, value):
        # 假设这里只是简单地将单引号转义为两个单引号，可以根据实际需求添加更多转义逻辑
        return value.replace("'", "''")

    def trim_data(self, data):
        # 假设这里只是简单地将数据转换为字符串并修剪长度，可以根据实际需求修改
        max_length = 100
        data_str = str(data)
        if len(data_str) > max_length:
            return data_str[:max_length] + '...'
        else:
            return data_str