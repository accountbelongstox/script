from pycore.dbmode.baseclass.base.dbbase import DBBase
from pycore.dbmode.baseclass.provider.table_class import TableClass
from pycore.dbmode.baseclass.abs.init_tables import DBInit
from pycore.dbmode.baseclass.provider.common import SqlalchemyBase

import re
import time
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, BigInteger, \
    SmallInteger, LargeBinary, Float, Numeric, Date
from datetime import datetime, date, time as datatime_time

class DBInit(DBBase,DBInit):
    __delete_token = "is_delete"
    __step_per = 1000
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
    __common_table = None

    def __init__(self):
        pass

    def init_database(self,  ):
        self.__common_table = self.get_globl_table_map()
        # self.pprint(self.__common_table)
        # self.create_table()



    def exist_table(self, tabname):
        tablemaps = self.get_tablemaps()
        return tabname in tablemaps

    def exist_field(self, tabname, field_name):
        tablemaps = self.get_tablemaps()
        if self.exist_table(tabname):
            table_class = tablemaps[tabname]
            return hasattr(table_class, field_name)
        return False

    def create_table(self, tabname=None, fields=None):
        if tabname is None or fields is None:
            databases = self.get_tables()
            for database in databases:
                table_name = database.get('tabname')
                fixed_name = database.get('fixed_name')
                if not fixed_name:
                    fixed_name = table_name
                fields = database.get('fields')
                table_class, fieldstypes = self.create_table_class(table_name, fields)
                engine = self.get_globl_engine()
                SqlalchemyBase.metadata.create_all(engine, [table_class.__table__])
        else:
            tablemaps = self.get_tablemaps()
            if isinstance(fields, list):
                fields = fields[0]
            table_class = self.create_table_class(tabname, fields)
            engine = self.get_globl_engine()
            SqlalchemyBase.metadata.create_all(engine, [table_class.__table__])
            tablemaps[tabname] = table_class

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
        return self.__common_table

    def get_tablename(self, tabname):
        for item in self.__databases:
            if item.get('fixed_name') == tabname:
                return item.get('tabname')
        return None

    def get_tablefieldsmaps(self):
        return self.__tablefieldsmaps

    def get_useddbs(self):
        # usedbsection = "use_db"
        # use_dbs = self.com_config.get_section(usedbsection)
        useddbs = ["mysql"]
        # for db_type, str_value in use_dbs.items():
        #     value = self.com_config.config(usedbsection, db_type)
        #     if value == True:
        #         useddbs.append(db_type)
        return useddbs

    def create_table_class(self, table_name, fields):
        class_dict = {
            '__tablename__': table_name,
            '__table_args__': {'extend_existing': True},
            "id": Column(Integer, primary_key=True, nullable=False),
            "time": Column(DateTime, nullable=False),
            self.get_delete_token(): Column(Integer, nullable=False),
            # 'as_dict': self.as_dict,
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
            return self.to_int(value)
        elif field_type == Float:
            return self.to_float(value)
        elif field_type == String:
            return self.to_str(value)
        elif field_type == Text:
            return self.to_str(value)
        elif field_type == LargeBinary:
            return self.to_bytes(value)
        elif field_type == Boolean:
            return self.to_bool(value)
        elif field_type == Date:
            return self.to_date(value)
        elif field_type == DateTime:
            return self.to_datetime(value)
        elif field_type == Numeric:
            return self.to_float(value)
        else:
            # self.com_util.print_warn(f"Unsupported field type: {field_type}")
            return value

    def dict_escape(self, tabname, data):
        tablefieldsmaps = self.get_tablefieldsmaps()
        maps = tablefieldsmaps.get(tabname)
        if "time" not in data:
            data["time"] = self.create_time()
        for key, value in data.items():
            field_type = maps.get(key)
            value = self.convert_to_type(value, field_type)
            data[key] = value
        return data
    def create_time(self, format="%Y-%m-%d %H:%M:%S"):
        t = time.strftime(format, time.localtime())
        return t

    def escape_andsetdate(self, tabname, data):
        if isinstance(data, list):
            data = self.list_escape(tabname, data)
        elif isinstance(data, dict):
            data = self.dict_escape(tabname, data)
        return data
    def to_datetime(self, data):
        if isinstance(data, datetime):
            return data
        elif isinstance(data, date):
            return datetime.combine(data, datatime_time.min)
        elif data in [None, "", "null", False]:
            return datetime.fromtimestamp(100000)
        elif isinstance(data, str):
            dataformat = self.is_timestring(data)
            if dataformat:
                return datetime.strptime(data, dataformat)
            else:
                return datetime.fromtimestamp(100000)
        else:
            self.com_util.print_warn(f"to_datetime")
            self.com_util.print_warn(data)
            return datetime.fromtimestamp(100000)
    def is_timestring(self, time_str, ):
        if type(time_str) != str:
            return None
        time_str = time_str.strip()
        if len(time_str) == 0:
            return None
        first_char = time_str[0]
        if self.is_number(first_char) != True:
            return None
        pattern = re.compile(r'^\s*\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return "%Y-%m-%d %H:%M:%S"
        pattern = re.compile(r'^\s*\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return "%Y-%m-%d %H:%M"
        pattern = re.compile(r'^\s*\d{4}-\d{1,2}-\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return "%Y-%m-%d"
        pattern = re.compile(r'^\s*\d{1,2}:\d{1,2}:\d{1,2}\s*$')
        if re.match(pattern, time_str) != None:
            return "%H:%M:%S"
        return None
    def is_number(self, s):
        if type(s) in [int, float]:
            return True
        if type(s) != str:
            return False
        s = s.strip()
        if s.isdigit():
            return True
        return False
    def to_str(self, data):
        if isinstance(data, str):
            data = data
        elif data in [None, 'Null', 'null', 0, 0.0, False]:
            data = ""
        elif isinstance(data, bytes):
            data = self.byte_to_str(data)
        else:
            data = self.json_tostring(data)
            if not isinstance(data, str):
                data = str(data)
            data = self.convert_to_string(data)
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

dbinit = DBInit()