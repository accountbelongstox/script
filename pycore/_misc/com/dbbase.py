from pycore._base import *
from pycore.db_baseclass.table_class import TableClass
# import time
# import json
# import os
# import pickle
# import operator
# import copy
# import sqlite3
# from lxml import etree
from datetime import datetime, date
import re
import threading
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, DECIMAL, BigInteger, \
    SmallInteger, LargeBinary, Float, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base

# import sqlalchemy.types as types
# from sqlalchemy.orm import sessionmaker

SqlalchemyBase = declarative_base()

threadingLock = threading.Lock()


class Dbbase(Base):
    __delete_token = "is_delete"
    __step_per = 1000  # 默认每次读取1000个单词
    __limit_start = 0
    __limit_end = 0
    __dbconfig = None
    __basetables = None
    __databases = None
    __tablemaps = {}
    __tablefieldsmaps = {}
    __type_map = {
        "INT": Integer,
        "INTEGER": Integer,
        "TINYINT": Integer,
        "SMALLINT": Integer,
        "MEDIUMINT": Integer,
        "BIGINT": BigInteger,
        "UNSIGNED BIG INT": BigInteger,
        "BIG INT": BigInteger,
        "INT2": SmallInteger,
        "INT8": BigInteger,
        "CHARACTER": String,
        "VARCHAR": String,
        "CHAR": String,
        "VARYING CHARACTER": String,
        "NCHAR": String,
        "NATIVE CHARACTER": String,
        "NVARCHAR": String,
        "TEXT": Text,
        "FILE": Text,
        "CLOB": Text,
        "BLOB": LargeBinary,
        "REAL": Float,
        "DOUBLE": Float,
        "DOUBLE PRECISION": Float,
        "FLOAT": Float,
        "NUMERIC": Numeric,
        "DECIMAL": Numeric,
        "BOOLEAN": Boolean,
        "DATE": Date,
        "DATETIME": DateTime
    }
    __common_table = [
        {
            "tabname": "sundries_default_table",
            "fixed_name": "sundries_default_table",
            "fields": {
                "text": "TEXT",
                "origin_type": "TEXT",
                "read": "REAL",
            }
        },
        {
            "tabname": "translation_dictionary",
            "fixed_name": "translation_dictionary",
            "fields": {
                "word": "VARCHAR(100) UNIQUE",
                "language": "TEXT",
                "translate_bing": "TEXT",
                "last_time": "DATETIME",
                "read": "INTEGER",
                "read_time": "DATETIME",
                "word_sort": "VARCHAR(100)",
                "phonetic_us": "VARCHAR(50)",
                "phonetic_us_sort": "VARCHAR(50)",
                "phonetic_us_length": "INTEGER",
                "phonetic_uk": "VARCHAR(50)",
                "phonetic_uk_sort": "VARCHAR(50)",
                "phonetic_uk_length": "INTEGER",
                "word_length": "INTEGER",
            }
        },
        {
            "tabname": "translation_group",
            "fixed_name": "translation_group",
            "fields": {
                "group_n": "VARCHAR(200) UNIQUE",
                "uid": "INTEGER",
                "group_type": "VARCHAR(100)",
                "language": "TEXT",
                "count": "INTEGER",
                "link_words": "TEXT",
                "word_frequency": "TEXT",
                "include_words": "TEXT",
                "include_words_count": "INTEGER",
                "invalid_words": "TEXT",
                "invalid_words_count": "INTEGER",
                "valid_words": "TEXT",
                "valid_words_count": "INTEGER",
                "last_time": "DATETIME",
                "word_read": "INTEGER",
                "origin_text": "FILE",
                "sentence": "TEXT",
            }
        },
        {
            "tabname": "translation_voices",
            "fixed_name": "translation_voices",
            "fields": {
                "group_id": "INTEGER",
                "sentence": "TEXT",
                "voice": "TEXT",
                "md5": "CHAR(32) UNIQUE",
                "link_words": "TEXT",
                "last_time": "DATETIME",
                "read": "INTEGER",
            }
        },
        {
            "tabname": "translation_notebook",
            "fixed_name": "translation_notebook",
            "fields": {
                "group_id": "INTEGER",
                "user_id": "INTEGER",
                "word_id": "INTEGER",
                "reference_url": "TEXT",
                "last_time": "DATETIME",
                "read": "INTEGER",
            }
        },
        {
            "tabname": "user",
            "fixed_name": "user",
            "fields": {
                "user": "VARCHAR(100) UNIQUE",
                "pwd": "VARCHAR(32)",
                "role": "INTEGER",
                "trans_count": "INTEGER",
                "last_login": "TEXT",
                "last_time": "DATETIME",
                "register_time": "DATETIME",
                "register_ip": "VARCHAR(32)",
                "read": "INTEGER",
            }
        },
        {
            "tabname": "user_gtu_map",
            "fixed_name": "user_gtu_map",
            "fields": {
                "userid": "INTEGER",
                "group_id": "INTEGER",
                "group_map": "TEXT",
            }
        },
        {
            "tabname": "user_gtu_haveread",
            "fixed_name": "user_gtu_haveread",
            "fields": {
                "userid": "INTEGER",
                "read_ids": "TEXT",
                "read_time_day": "DATETIME",
                "read_time": "DATETIME",
            }
        },
        {
            "tabname": "user_gtu_readcount",
            "fixed_name": "user_gtu_readcount",
            "fields": {
                "userid": "INTEGER",
                "read_map": "TEXT",
            }
        },
        {
            "tabname": "translation_dictionarymap",
            "fixed_name": "translation_dictionarymap",
            "fields": {
                "wordids": "TEXT",
                "words": "TEXT",
                "count": "INTEGER",
                "words_count": "INTEGER",
                "ids_count": "INTEGER",
            }
        },
    ]

    def __init__(self, args):
        pass

    def main(self, args):
        pass

    def init_database(self, ):
        self.get_tablemaps()

    def transport_database(self, from_db, to_db, step=10000):
        from_db = self.get_dbmodefromname(from_db)
        to_db = self.get_dbmodefromname(to_db)
        from_dbname = self.get_dbnamefrommode(from_db)
        to_dbname = self.get_dbnamefrommode(to_db)
        tables = from_db.get_tables()
        self.com_util.print_info(f'transport_database from {from_dbname} to {to_dbname}')
        for table in tables:
            self.com_util.print_info(f'starting duplicated from {table}')
            self.transport(from_db, to_db, table, step=step)

    def transport(self, from_db, to_db, tabname, step=10000):
        from_db = self.get_dbmodefromname(from_db)
        to_db = self.get_dbmodefromname(to_db)
        from_dbname = self.get_dbnamefrommode(from_db)
        to_dbname = self.get_dbnamefrommode(to_db)
        origin_len = from_db.count(tabname)
        if origin_len == 0:
            return False

        target_len = 0
        if to_db.exist_table(tabname) == True:
            target_len = to_db.count(tabname)

        self.com_util.print_info(f'{tabname} {origin_len},target-count{target_len} data wait copying ')
        # 每次复制数据
        limit = self.init_limit(step)
        limit_start = limit[0]
        # columns = from_db.get_columns(tabname)
        while limit_start < (origin_len - 1):
            limit = self.get_limitincrement()
            limit_step = limit[0]
            limit_start = limit[1]
            limit_end = limit_start + limit_step
            self.com_util.print_info(f'\treading {tabname}:{limit_start}-{limit_end} from {from_dbname} to {to_dbname}')
            origin_data = from_db.read(tabname, limit=limit)

            if to_db.exist_table(tabname) == False:
                fields = from_db.get_fields()
                to_db.create_table(tabname, fields)
                print(fields)
                exit()

            self.com_util.print_info(
                f'\ttranslating of {tabname}({len(origin_data)} item by data)')
            # to_db.save(tabname, origin_data)
            self.com_util.print_info(
                f'\tSuccessfully! {tabname}')
            self.com_util.print_info(
                f'------------------------------------------------------------------------------------')

    def get_tablemaps(self):
        if len(self.__tablemaps.keys()) > 0:
            return self.__tablemaps
        use_dbs = self.get_useddbs()
        if len(use_dbs) > 0:
            databases = self.get_tables()
            for database in databases:
                table_name = database.get('tabname')
                fixed_name = database.get('fixed_name')
                if not fixed_name:
                    fixed_name = table_name
                fields = database.get('fields')
                table_class, fieldstypes = self.create_table_class(table_name, fields)
                self.__tablemaps[fixed_name] = table_class
                self.__tablefieldsmaps[fixed_name] = fieldstypes
        return self.__tablemaps

    def get_tables(self):
        if self.__databases != None:
            return self.__databases
        control_databases = self.get_controldatabasies()
        self.__databases = control_databases + self.__common_table
        return self.__databases

    def get_tablename(self, tabname):
        for item in self.__databases:
            if item.get('fixed_name') == tabname:
                return item.get('tabname')
        return None

    def get_tablefieldsmaps(self):
        return self.__tablefieldsmaps

    def get_useddbs(self):
        usedbsection = "use_db"
        use_dbs = self.com_config.get_section(usedbsection)
        useddbs = []
        for db_type, str_value in use_dbs.items():
            value = self.com_config.config(usedbsection, db_type)
            if value == True:
                useddbs.append(db_type)
        return useddbs

    def create_table_class(self, table_name, fields):
        # global SqlalchemyBase
        class_dict = {
            '__tablename__': table_name,
            '__table_args__': {'extend_existing': True},
            "id": Column(Integer, primary_key=True, nullable=False),
            "time": Column(DateTime, nullable=False),
            self.get_delete_token(): Column(Integer, nullable=False),
            # 'as_dict': self.as_dict,  # 添加as_dict方法
        }
        fieldstypes = {
            "id": self.__type_map["INT"],
            "time": self.__type_map["DATETIME"],
        }
        field_elements_pattern = re.compile(r'\((.*?)\)')
        for field_name, field_types in fields.items():
            field_elements = field_types.split()
            match = field_elements_pattern.search(field_elements[0])
            varchar_len = None
            if match:
                varchar_len = match.group(1)
                field_elements[0] = field_elements[0].replace(f'({varchar_len})', '')
            field_elements = self.listformat_fields(field_elements)
            field_type = field_elements.pop(0)
            fieldstypes[field_name] = self.__type_map[field_type]
            class_dict[field_name] = self.get_ormfield(field_type, field_elements, varchar_len)
        table_class = type(table_name, (TableClass,), class_dict)
        return table_class, fieldstypes

    def get_ormfield(self, field_type, field_elements, varchar_len):
        unique = True if "UNIQUE" in field_elements else False
        nullable = True if "NOT NULL" in field_elements else False
        if varchar_len != None:
            varchar_len = int(varchar_len)
            return Column(self.__type_map[field_type](varchar_len), unique=unique, nullable=nullable)
        else:
            return Column(self.__type_map[field_type], unique=unique, nullable=nullable)

    def listformat_fields(self, fields):
        new_words = []
        i = 0
        while i < len(fields):
            if fields[i] == 'NOT' and i + 1 < len(fields):
                new_words.append(' '.join(fields[i:i + 2]))
                i += 2
            else:
                new_words.append(fields[i])
                i += 1
        return new_words

    def get_controldatabasies(self):
        control_config = self.load_module.get_control_config()
        control_databases = control_config.get('database')
        if control_databases == None:
            control_databases = []
        if type(control_databases) != list:
            control_databases = [control_databases]
        prefix = self.load_module.get_control_name()
        for a_dict in control_databases:
            a_dict['tabname'] = prefix + a_dict['tabname']
        return control_databases

    def get_dbmodefromname(self, dbmodule):
        if type(dbmodule) == str:
            dbmodule = self.get_db(dbmodule)
        return dbmodule

    def get_dbnamefrommode(self, dbmodule):
        if type(dbmodule) != str:
            dbmodule = dbmodule.__class__.__name__
        return dbmodule

    def set_limitsetp(self, step):
        self.__step_per = step

    def init_limit(self, step=None):
        if step != None:
            self.set_limitsetp(step)
        self.__limit_start = 0
        self.__limit_end = self.__step_per
        self.__limit = (self.__step_per, self.__limit_start)
        return self.__limit

    def get_limitincrement(self):
        self.__limit_end = self.__limit_start + self.__step_per
        self.__limit = (self.__step_per, self.__limit_start)
        self.__limit_start = self.__limit_start + self.__step_per
        return self.__limit

    def list_escape(self, tabname, data):
        for index in range(len(data)):
            value = data[index]
            data[index] = self.dict_escape(tabname, value)
        return data

    def convert_to_type(self, value, field_type):
        if field_type == Integer:
            return self.com_string.to_int(value)
        elif field_type == Float:
            return self.com_string.to_float(value)
        elif field_type == String:
            return self.com_string.to_str(value)
        elif field_type == Text:
            return self.com_string.to_str(value)
        elif field_type == LargeBinary:
            return self.com_string.to_bytes(value)
        elif field_type == Boolean:
            return self.com_string.to_bool(value)
        elif field_type == Date:
            return self.com_string.to_date(value)
        elif field_type == DateTime:
            return self.com_string.to_datetime(value)
        elif field_type == Numeric:
            return self.com_string.to_float(value)
        else:
            # self.com_util.print_warn(f"Unsupported field type: {field_type}")
            return value

    def dict_escape(self, tabname, data):
        tablefieldsmaps = self.get_tablefieldsmaps()
        maps = tablefieldsmaps.get(tabname)
        if "time" not in data:
            data["time"] = self.com_string.create_time()
        for key, value in data.items():
            field_type = maps.get(key)
            value = self.convert_to_type(value, field_type)
            data[key] = value
        return data

    def escape_andsetdate(self, tabname, data):
        if isinstance(data, list):
            data = self.list_escape(tabname, data)
        elif isinstance(data, dict):
            data = self.dict_escape(tabname, data)
        return data

    def trim_data(self, data):
        if isinstance(data, list):
            data = data[0]
        new_dict = {}
        for k, v in data.items():
            if isinstance(v, str) and len(v) > 10:
                new_dict[k] = v[:10]
            else:
                new_dict[k] = v
        return new_dict

    def check_like(self, s):
        s = s.strip()
        if s.startswith('%') and s.endswith('%'):
            return 'both'
        elif s.startswith('%'):
            return 'beginning'
        elif s.endswith('%'):
            return 'end'
        else:
            return 'none'

    def get_column_type(self):
        column_types = [
            "INT", "INTEGER", "TINYINT", "SMALLINT", "MEDIUMINT", "BIGINT", "UNSIGNED", "BIG", "INT", "INT2", "INT8",
            "INTEGER", "CHARACTER", "VARCHAR", "CHAR", "VARYING", "CHARACTER", "NCHAR", "NATIVE",
            "CHARACTER", "NVARCHAR", "TEXT", "CLOB", "TEXT", "BLOB", "no", "datatype", "specified", "NONE",
            "REAL", "DOUBLE", "DOUBLE", "PRECISION", "FLOAT", "REAL", "NUMERIC", "DECIMAL", "BOOLEAN", "DATE",
            "DATETIME", "NUMERIC"
        ]
        return column_types

    def get_delete_token(self):
        return self.__delete_token

    def get_dbconfig(self):
        if self.__dbconfig == None:
            config = self.load_module.get_control_config()
            dbconfigs = config.get('database')
            for dbconfig in dbconfigs:
                dbconfig["tabname"] = self.load_module.get_control_name() + "_" + dbconfig["tabname"]
            self.__dbconfig = dbconfigs
        return self.__dbconfig

    def gen_limit_sql(self, limit, default_limit_length=1000):
        if not limit:
            return (None, 0)
        if isinstance(limit, str):
            limit = limit.split(',')
            limit_start = int(limit[0])
            offset = int(self.com_util.get_list_value(limit, 1, 0))
        elif isinstance(limit, int):
            limit_start = limit
            offset = 0
        elif isinstance(limit, (tuple, list)):
            limit_start = int(limit[0])
            offset = int(self.com_util.get_list_value(limit, 1, 0))
            if limit_start == 0 and offset > 0:
                offset, limit_start = limit_start, offset
        else:
            limit_start = default_limit_length
            offset = 0
        return (limit_start, offset)
