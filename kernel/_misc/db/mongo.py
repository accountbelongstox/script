# import html
from pycore.base.base import *
from pycore.db_baseclass.dbbase import *
from mongoengine import (Document, StringField, IntField, LongField, FloatField, DecimalField, BooleanField,
                         DateTimeField, DateField, BinaryField, FileField)
# import time
# import json
# import os
import re
# import pymongo
# from pymongo import ASCENDING, DESCENDING, MongoClient
from mongoengine.queryset.visitor import Q
from mongoengine.errors import NotUniqueError
from mongoengine import connect
from pymongo.errors import DuplicateKeyError


class Mongo(Base, DBBase):
    __tablemaps = {}
    __tablefieldsmaps = {}
    session = None
    __type_map = {
        "INT": IntField,
        "INTEGER": IntField,
        "TINYINT": IntField,
        "SMALLINT": IntField,
        "MEDIUMINT": IntField,
        "BIGINT": LongField,
        "UNSIGNED BIG INT": LongField,
        "BIG INT": LongField,
        "INT2": IntField,
        "INT8": LongField,
        "CHARACTER": StringField,
        "VARCHAR": StringField,
        "CHAR": StringField,
        "VARYING CHARACTER": StringField,
        "NCHAR": StringField,
        "NATIVE CHARACTER": StringField,
        "NVARCHAR": StringField,
        "TEXT": StringField,
        "FILE": FileField,
        "CLOB": StringField,
        "BLOB": BinaryField,
        "REAL": FloatField,
        "DOUBLE": FloatField,
        "DOUBLE PRECISION": FloatField,
        "FLOAT": FloatField,
        "NUMERIC": DecimalField,
        "DECIMAL": DecimalField,
        "BOOLEAN": BooleanField,
        "DATE": DateField,
        "DATETIME": DateTimeField
    }
    tablemaps = {}

    def __init__(self, args):
        pass

    def main(self, args):
        self.init_database()
        pass

    def init_database(self, ):
        self.get_tablemaps()

        # self.tables = self.com_dbbase.get_tables()
        # for table in self.tables:
        #     tabname = table.get('tabname')
        #     fields = table.get('fields')
        #     if not self.exist_table(tabname):
        #         self.create_table(tabname, fields)

    def get_tables(self):
        return self.__tablemaps.keys()

    def get_fields(self,tabname):
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        return table_class

    def get_tablemaps(self):
        if len(self.__tablemaps.keys()) > 0:
            return self.__tablemaps
        databases = self.com_dbbase.get_tables()
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

    def create_table_class(self, table_name, fields=None, all_unique=True):
        class_dict = {
            'meta': {'collection': table_name},
            'id': IntField(primary_key=True, required=True),  # primary_key=False,
            'time': DateTimeField(required=False),
            self.com_dbbase.get_delete_token(): IntField(required=False),
        }
        fieldstypes = {
            "id": self.__type_map["INT"],
            "time": self.__type_map["DATETIME"],
            self.com_dbbase.get_delete_token(): self.__type_map["INT"],
        }
        field_elements_pattern = re.compile(r'\((.*?)\)')
        if not fields:
            databases = self.com_dbbase.get_tables()
            for database in databases:
                query_table_name = database.get('tabname')
                if table_name == query_table_name:
                    fields = database.get('fields')
                    break
        for field_name, field_types in fields.items():
            field_elements = field_types.split()
            match = field_elements_pattern.search(field_elements[0])
            varchar_len = None
            if match:
                varchar_len = match.group(1)
                field_elements[0] = field_elements[0].replace(f'({varchar_len})', '')
            field_elements = self.com_dbbase.listformat_fields(field_elements)
            field_type = field_elements.pop(0)
            fieldstypes[field_name] = self.__type_map[field_type]
            class_dict[field_name] = self.get_ormfield(field_type, field_elements, varchar_len, all_unique=all_unique)
        table_class = type(table_name, (Document,), class_dict)
        return table_class, fieldstypes

    def get_ormfield(self, field_type, field_elements, varchar_len, all_unique=True):
        if all_unique == True:
            unique = True if "UNIQUE" in field_elements else False
            required = True if "NOT NULL" in field_elements else False
        else:
            unique = False
            required = False
        field_kwargs = {"unique": unique, "required": required}
        if varchar_len is not None:
            varchar_len = int(varchar_len)
            field_kwargs["max_length"] = varchar_len
        field_class = self.__type_map[field_type]
        return field_class(**field_kwargs)

    def exist_table(self, tabname):
        self.connect()
        collection_names = self.__con__.list_collection_names()
        return tabname in collection_names

    def exist_field(self, tabname, field_name):
        self.connect()
        if self.exist_table(tabname):
            collection = self.__con__[tabname]
            doc = collection.find_one({field_name: {"$exists": True}})
            return doc is not None
        else:
            return False

    def modify_field(self, tabname, fields):
        self.connect()
        collection = self.__con__[tabname]
        collection.update_many({}, {"$set": fields})

    def create_table(self, tabname, fields):
        self.connect()
        if not self.exist_table(tabname):
            self.__con__.create_collection(tabname)

    def commit(self):
        pass

    def close(self):
        self.__con__.close()

    def deduplication(self, tabname, keys):
        table_class, fieldstypes = self.create_table_class(tabname, all_unique=False)
        collection = table_class._get_collection()
        for key in keys:
            duplicates = (
                collection.aggregate(
                    [
                        {"$group": {"_id": f"${key}", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}},
                        {"$match": {"count": {"$gt": 1}}},
                    ]
                )
            )
            # 保留最后一个值
            for duplicate in duplicates:
                ids = [str(id_) for id_ in duplicate["ids"][1:]]  # 保留最后一个值
                for id in ids:
                    table_class.objects(Q(pk=id)).delete()

    def get_unique_fields(self, table_class):
        fields = table_class._fields
        unique_fields = []
        for field_name, field in fields.items():
            if field.unique:
                unique_fields.append(field_name)
        return unique_fields

    def increment_idfordata(self, data, table_class, tabname):
        # 添加ID自增值
        id_field = getattr(table_class, 'id', None)
        if id_field:
            if 'id' not in data:
                result = table_class.objects().order_by('-id')
                first_item = result.first()
                if first_item:
                    max_id = first_item.id
                else:
                    max_id = 0
                if self.com_string.is_number(max_id):
                    if not isinstance(max_id, int):
                        max_id = int(max_id)
                    max_id += 1
                else:
                    max_id = 1
                data['id'] = max_id
        return data

    def increment_ids(self, data, table_class, tabname):
        if isinstance(data, list):
            for i in range(len(data)):
                item = data[i]
                data[i] = self.increment_idfordata(item, table_class, tabname)
        else:
            data = self.increment_idfordata(data, table_class, tabname)
        return data

    def list_escape(self, tabname, data):
        for index in range(len(data)):
            value = data[index]
            data[index] = self.dict_escape(tabname, value)
        return data

    def convert_to_type(self, value, field_type):
        if field_type == IntField:
            return self.com_string.to_int(value)
        elif field_type == FloatField:
            return self.com_string.to_float(value)
        elif field_type == StringField:
            return self.com_string.to_str(value)
        elif field_type == StringField:
            return self.com_string.to_str(value)
        elif field_type == BinaryField:
            return self.com_string.to_bytes(value)
        elif field_type == BooleanField:
            return self.com_string.to_bool(value)
        elif field_type == DateField:
            return self.com_string.to_date(value)
        elif field_type == DateTimeField:
            return self.com_string.to_datetime(value)
        elif field_type == DecimalField:
            return self.com_string.to_float(value)
        else:
            # self.com_util.print_warn(f"Unsupported field type: {field_type}")
            return value

    def get_tablefieldsmaps(self):
        return self.__tablefieldsmaps

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

    def save(self, tabname=None, data=None, result_id=True):
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        if not table_class:
            self.com_util.print_warn("save tabname must be provided")
            return
        if not data:
            self.com_util.print_warn("save data must be provided")
            return
        self.connect()
        data = self.increment_ids(data, table_class, tabname)
        data = self.escape_andsetdate(tabname, data)
        saved_ids = []

        if isinstance(data, dict):
            data = [data]
        # documents_list = [table_class(**item) for item in data]
        # # 一次性插入文档对象列表
        # table_class.objects.insert(documents_list,load_bulk=False)

        for item in data:
            sid = self.save_item(table_class, item)
            if sid != None:
                saved_ids.append(sid)
        if result_id:
            return saved_ids
        else:
            self.com_util.print_warn("save Invalid data type for 'data' parameter. Expected list or dict.")
            return None

    def save_item(self, table_class, data):
        try:
            # 创建记录实例，但不存储FileField字段
            record_data = {k: v for k, v in data.items() if not isinstance(getattr(table_class, k, None), FileField)}
            record = table_class(**record_data)

            # 单独处理FileField字段
            for k, v in data.items():
                if isinstance(getattr(table_class, k, None), FileField):
                    # 编码字符串为字节流
                    byte_data = v.encode('utf-8') if isinstance(v, str) else v
                    getattr(record, k).put(byte_data, content_type='text/plain')

            record.save()
            return record.id
        except Exception as e:
            e = str(e)
            if e.find("unique") == -1:
                self.com_util.print_warn(f"MongoDB save error: {e}")
            return None

    def filter_query(self, conditions=None):
        query = Q()
        nulls = ["", "null", "None", None]
        if conditions:
            for key, value in conditions.items():
                if isinstance(value, list):
                    query &= Q(**{f"{key}__in": value})
                elif isinstance(value, int):
                    query &= Q(**{key: value})
                elif value in nulls:
                    query &= Q(**{f"{key}__in": nulls})
                elif isinstance(value, str):
                    if value.startswith("!="):
                        query &= Q(**{f"{key}__ne": value[2:]})
                    elif value.startswith("%") and value.endswith("%"):
                        query &= Q(**{f"{key}__contains": value[1:-1]})
                    elif value.startswith("%"):
                        query &= Q(**{f"{key}__startswith": value[1:]})
                    elif value.endswith("%"):
                        query &= Q(**{f"{key}__endswith": value[:-1]})
                    elif value.startswith(">="):
                        query &= Q(**{f"{key}__gte": value[2:]})
                    elif value.startswith("<="):
                        query &= Q(**{f"{key}__lte": value[2:]})
                    elif value.startswith(">"):
                        query &= Q(**{f"{key}__gt": value[1:]})
                    elif value.startswith("<"):
                        query &= Q(**{f"{key}__lt": value[1:]})
                    else:
                        query &= Q(**{key: value})
                else:
                    query &= Q(**{key: value})
        return query

    def read(self, tablename, conditions=None, limit=(0, 1000), select=None, sort=None, result_object=True,
             bug=False,
             print_sql=False,
             read_delete=False,
             ):
        self.connect()
        if read_delete == False:
            if conditions == None:
                conditions = {
                    "is_delete": "!=1"
                }
            else:
                conditions["is_delete"] = "!=1"
        tablemaps = self.get_tablemaps()
        limit = self.com_dbbase.gen_limit_sql(limit)
        table_class = tablemaps.get(tablename)
        query = self.filter_query(conditions)
        records = table_class.objects(query)
        if select and select != "*":
            select = tuple(select.split(','))
            records = records.only(*select)
        if sort:
            records = records.order_by(*sort)
        offset = limit[1]
        query_len = limit[0]
        records = records.skip(offset).limit(query_len)
        records = records.as_pymongo()
        record_list = []
        for item in records:
            item_list = []
            item = dict(item.items())
            qid = item.get('_id')
            item["id"] = qid
            for key, val in item.items():
                if isinstance(getattr(table_class, key, None), FileField):
                    record = table_class.objects.get(id=qid)
                    file_content = getattr(record, key).read().decode('utf-8')
                    val = file_content
                    item[key] = file_content
                item_list.append(val)
            if not result_object:
                record_list.append(item_list)
            else:
                record_list.append(item)
        if print_sql:
            self.com_util.print_info(records.to_json())
        records = record_list
        if isinstance(records, list):
            records = [item[0] if (isinstance(item, list) and len(item) == 1) else item for item in records]
        return records

    def get_id(self, tabname, conditions):
        self.connect()
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        query = self.filter_query(conditions)
        document = table_class.objects(query).order_by('-id').first()
        if document:
            return document.id
        return None

    def count(self, tabname=None, conditions=None, print_sql=False):
        self.connect()
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        query = self.filter_query(conditions)
        count = table_class.objects(query).count()
        return count

    def delete(self, tabname=None, conditions=None, physical=False):
        data = {
            self.com_dbbase.get_delete_token(): 1
        }
        if not physical:
            return self.update(tabname=tabname, data=data, conditions=conditions)
        else:
            return self.delete_physical(tabname=tabname, conditions=conditions)

    def delete_physical(self, tabname, conditions, not_execute=False):
        self.connect()
        if not conditions:
            self.com_util.print_warn(f"{tabname} delete must need conditions")
            return 0
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        query = self.filter_query(conditions)
        docs = list(table_class.objects(query))
        table_class.objects(query).delete()
        ids = [doc.id for doc in docs]
        if len(ids) == 0:
            return 0
        return ids[:-1]

    def update(self, tabname=None, data=None, conditions=None, not_execute=False, print_sql=False):
        self.connect()
        if not conditions:
            self.com_util.print_warn(f"{tabname} delete must need conditions")
            return 0
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        query = self.filter_query(conditions)
        data = self.dict_escape(tabname, data)
        updated_documents = list(table_class.objects(query))

        for key, value in data.items():
            if isinstance(value, str):
                if value.startswith("-") or value.startswith('+'):
                    value = value[1:]
                    if self.com_string.is_number(value):
                        value = self.com_string.number(value)
                        if value.startswith("+"):
                            table_class.objects(query).update_one(inc__counter=value)
                        elif value.startswith('-'):
                            table_class.objects(query).update_one(dec__counter=value)
                        del data[key]

        if len(data.keys()) > 0:
            table_class.objects(query).update(**data)
        updated_ids = [doc.id for doc in updated_documents]
        if len(updated_ids) == 0:
            return 0
        elif len(updated_ids) == 1:
            return updated_ids[0]
        else:
            return updated_ids

    def connect(self):
        if self.session is not None:
            return self.session
        username = self.com_config.get_global('mongo_user')
        password = self.com_config.get_global('mongo_password')
        host = self.com_config.get_global('mongo_host')
        port = self.com_config.get_global('mongo_port')
        db_name = self.com_config.get_global('mongo_database')
        if username and password:
            self.session = connect(db=db_name, host=host, port=int(port), username=username, password=password)
        else:
            self.session = connect(db=db_name, host=host, port=int(port))

        return self.session
