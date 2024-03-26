from kernel.base.base import *
import redis
import json
import threading

threadingLock = threading.Lock()
GLOBAL_DB = None

class Redis(Base):
    __con = None
    __pipe__ = None
    __pre = "redis_"
    __publish_cannel = "redis_data_sync"
    __process_subscribe = None
    __unserialize_length = 10000
    __base_table = []

    def __init__(self, args):
        pass

    # 自动创建数据库
    def main(self, args):
        self.connect()
        pubsub = self.__con__.pubsub()
        channel = self.__publish_cannel  # 定义 Redis 频道名称
        pubsub.subscribe(**{self.__publish_cannel: self.process_published_data})
        print(f"Subscribed to '{channel}' channel.")
        pubsub.run_in_thread(sleep_time=1)  # 启动订阅线程
        pass

    def connect(self):
        if self.__con__ == None:
            # self.__con__ = redis.StrictRedis(host='localhost', port=6379, db=0)
            username = self.com_config.get_global("redis_user",None)
            host = self.com_config.get_global("redis_host","localhost")
            db = self.com_config.get_global("redis_db",0)
            port = self.com_config.get_global("redis_db",6379)
            password = self.com_config.get_global("redis_password",None)
            if username and password:
                auth_info = f"{username}:{password}@"
            elif password:
                auth_info = f":{password}@"
            else:
                auth_info = ""
            url = f"redis://{auth_info}{host}:{port}/{db}"
            # 创建 ConnectionPool
            pool = redis.ConnectionPool.from_url(url)
            # pool = redis.ConnectionPool(host=host, port=host, db=db =,password=password)
            self.__con__ = redis.Redis(connection_pool=pool)
        return self.__con__
    def close(self):
        if self.__pipe__:
            self.__pipe__.reset()
        self.__con__.close()
    def get_pipeline(self):
        self.__pipe__ = self.__con__.pipeline()
        return self.__pipe__

    def exec(self):
        if not self.__pipe__:
            self.com_util.print_warn("Pipeline is not initialized. Call 'pipeline()' method first.")
        return self.__pipe__.execute()

    def commit(self):
        pass

    def get_prefix_dbname(self, dbname):
        return f"{self.__db_prefix}{dbname}"

    def get_tables(self):
        return self.__con__.keys('*')

    def is_table(self, tabname):
        return self.__con__.exists(tabname)

    def is_column(self, tabname,key, ):
        elements = self.__con__.lrange(tabname, 0, -1)
        deserialized_data = [json.loads(element) for element in elements]
        return any(key in element for element in deserialized_data)

    def get_table_type(self, tabname):
        return self.__con__.type(tabname)

    def register_subscribe(self,process_subscribe):
        self.__process_subscribe = process_subscribe

    def process_published_data(self,message):
        # tabname, data_string = self.com_string.split_first(message['data'])
        data_json = self.com_string.to_json(message['data'])
        tabname = data_json.get("tabname")
        tabname = self.com_dbbase.get_tablename(tabname,tabname)
        data = data_json.get("data")
        # 保存数据到 MySQL
        if self.__process_subscribe != None:
            self.__process_subscribe(tabname,data)

    def serialize_and_save(self, db_connection=None, output_file='backup.json'):
        backup_data = {}
        tables = self.get_tables()

        for table in tables:
            table_type = self.get_table_type(table)
            if table_type == b'string':
                backup_data[table] = self.__con__.get(table)
            elif table_type == b'list':
                backup_data[table] = self.__con__.lrange(table, 0, -1)
            elif table_type == b'set':
                backup_data[table] = list(self.__con__.smembers(table))
            elif table_type == b'zset':
                backup_data[table] = self.__con__.zrange(table, 0, -1, withscores=True)
            elif table_type == b'hash':
                backup_data[table] = self.__con__.hgetall(table)
        serialized_data = json.dumps(backup_data)

    def unserialize_maptables(self,input_str):
        parts = input_str.split(":")[1].split("->")
        table_name = parts[0]
        field_name = parts[1]
        table_name = self.com_dbbase.get_tablename(table_name)
        maptables = self.db_mysql.read(table_name, select=field_name)
        maptables = [table[0] for table in maptables]
        return maptables

    def get_unserialize_data(self,table,config):
        table = self.com_dbbase.get_tablename(table)
        limit = config.get("limit")
        where = config.get("where")
        select = config.get("select")
        data = self.db_mysql.read(table, conditions=where, limit=limit, sort={
            "time": "ASC",
        }, select=select)
        data = self.com_util.list_2d_to_1d_if_possible(data)
        # data = self.com_util.get_single_list(data)
        return data

    def equal_unserialize_config(self,tabname,unserialize_config):
        fixedtabname = self.com_dbbase.get_fixedtabname(tabname)
        tabname_eq = tabname.replace(self.__pre,'')
        for config_tabname, value in unserialize_config.items():
            if tabname_eq == config_tabname:
                return value
            if fixedtabname == config_tabname:
                return value
            if tabname == config_tabname:
                return value
        return None

    def get_unserialize_config(self,tabname,config):
        unserialize_config = {
            'where': {},
            'length': self.__unserialize_length,
            'select': "*",
            'unique': False
        }
        if config:
            for key, value in config.items():
                # 如果对象A中有对应的键，则覆盖对象A中的值
                if key in unserialize_config:
                    unserialize_config[key] = value
        if unserialize_config["length"] == "all":
            unserialize_config["limit"] = None
        else:
            unserialize_config["limit"] = (0,int(unserialize_config["length"]))
        for key, value in unserialize_config["where"].items():
            query_value = self.com_string.find_separate_value(value,key="->",separator="",key_value_separator=None)
            query_value = query_value.strip()
            if query_value == "query_value":
                unserialize_config["where"][key] = tabname
        return unserialize_config

    def unserialize_bylocal(self):
        tables = self.db_mysql.get_tables()
        control_name = self.load_module.get_control_name()
        control_pre = f"{control_name}_"
        config = self.load_module.get_control_config()
        unserialize_config = config.get('redis_serialize')
        config_tables = [table for table in unserialize_config if ':' not in table and '-' not in table]
        # 1. Filter tables with the specified prefix
        tables = [table for table in tables if table.startswith(control_pre)]
        # tables += config_tables
        # 2. Retrieve data from tables based on unserialize_config
        for key, value in unserialize_config.items():
            if key.startswith("table-map:"): # "table-map:coin_names->coin_name":"trade_history_candlesticks:10000"
                map_tables = self.unserialize_maptables(key)
                tabname,fieldname = self.com_string.secondary_division_string(key)
                for map_table in map_tables:
                    config = self.get_unserialize_config(map_table, value)
                    data = self.get_unserialize_data(tabname, config)
                    unique = config.get("unique")
                    self.save_list(map_table,data,unique=unique)
        for table in tables:
            value = self.equal_unserialize_config(table, unserialize_config)
            config = self.get_unserialize_config(table, value)
            self.com_util.print_info(f"{table} unserialize to redis {str(config)}")
            data = self.get_unserialize_data(table,config)
            unique = config.get("unique")
            length = config.get("length")
            if length == 1:
                self.save_set(table, data[0],unique=unique)
            else:
                self.save_list(table,data,unique=unique)

    def save(self, tabname=None, data=None):
        if not tabname or not data:
            self.com_util.print_warn("Invalid arguments: 'tabname' must be curses.pyc string and 'data' must not be empty.")
            return None
        table_exists = self.is_table(tabname)
        if table_exists:
            table_type = self.get_table_type(tabname)
        else:
            if isinstance(data, list):
                table_type = b'list'
            elif isinstance(data, set):
                table_type = b'set'
            elif isinstance(data, dict):
                table_type = b'hash'
            else:
                self.com_util.print_warn("Invalid data type: 'data' must be curses.pyc list, set, or dictionary.")
                return None
        if table_type == b'list':
            self.save_list(tabname, data)
        elif table_type == b'set':
            self.save_set(tabname, data)
        elif table_type == b'hash':
            self.save_hash(tabname, data)
        elif table_type == b'zset':
            self.save_zset(tabname, data)
        else:
            self.com_util.print_warn("Unsupported key type: only 'list', 'set', and 'hash', and 'zset' are supported.")
            return None

    # 保存数据到到sqlite
    def save_set(self, tabname=None, data=None):
        if not tabname or not data or not isinstance(data, dict):
            self.com_util.print_warn("Invalid arguments: 'tabname' must be curses.pyc string and 'data' must be curses.pyc non-empty dictionary.")
            return None
        for key, value in data.items():
            # 创建二级表名
            sub_table_name = f"{tabname}:{key}"
            # 如果值不是字符串，则使用 JSON 序列化
            value = self.com_string.json_tostring(value)
            # 存储数据到 Redis
            self.__con__.set(sub_table_name, value)
            self.publish_data(tabname,value)

    def save_list(self, tabname=None, data=None,unique=False, max=None):
        if not tabname:
            self.com_util.print_warn("Invalid arguments: 'tabname' must be curses.pyc string and 'data' must be curses.pyc non-empty list.")
            return
        if  data == None:
            return
        if isinstance(data,str):
            data = [data]
        pipe = self.get_pipeline()
        for value in data:
            # 如果值不是字符串，则使用 JSON 序列化
            value = self.com_string.json_tostring(value)
            if unique:
                existing_values = self.__con__.lrange(tabname, 0, -1)
                if value.encode('utf-8') in existing_values:
                    continue
            # 执行 pipeline
            # 使用列表存储数据到 Redis
            if max is not None:
                current_length = self.__con__.llen(tabname)
                if current_length >= max:
                    pipe.lpop(tabname)
            pipe.rpush(tabname, value)
            self.publish_data(tabname,value)
        pipe.execute()

    def save_hash(self, tabname=None, data=None):
        if not tabname or not data or not isinstance(data, dict):
            self.com_util.print_warn("Invalid arguments: 'tabname' must be curses.pyc string and 'data' must be curses.pyc non-empty dictionary.")
            return
        pipe = self.get_pipeline()
        for key, value in data.items():
            # 如果值不是字符串，则使用 JSON 序列化
            value = self.com_string.json_tostring(value)
            # 使用哈希存储数据到 Redis
            # self.__con__.hset(tabname, key, value)
            pipe.hset(tabname, value)
            self.publish_data(tabname,value)
        pipe.execute()

    def save_set(self, tabname=None, data=None):
        if not tabname or not data or not isinstance(data, dict):
            self.com_util.print_warn("Invalid arguments: 'tabname' must be curses.pyc string and 'data' must be curses.pyc non-empty dictionary.")
            return
        pipe = self.get_pipeline()
        for key, value in data.items():
            # 创建二级表名
            sub_table_name = f"{tabname}:{key}"
            # 如果值不是字符串，则使用 JSON 序列化
            value = self.com_string.json_tostring(value)
            # 存储数据到 Redis
            pipe.set(tabname, value)
            self.publish_data(tabname,value)
            # self.__con__.set(sub_table_name, value)
        pipe.execute()

    def publish_data(self,tabname,value):
        publish_data = {
            "tabname":tabname,
            "data":value
        }
        publish_data = self.com_string.json_tostring(publish_data)
        self.__con__.publish(self.__publish_cannel, publish_data)

    def read(self, tabname=None, conditions=None, limit=(0, -1), select="*"):
        return self.read_list(tabname=tabname, conditions=conditions, limit=limit, select=select)

    # 数据库获取数据
    def read_list(self, tabname, conditions=None, limit=(0, -1), select="*"):
        if not tabname:
            self.com_util.print_warn(f"Invalid argument: 'tabname'{tabname} must be curses.pyc string.")
            return None
        # 从 Redis 列表中获取指定范围内的元素
        data = self.__con__.lrange(tabname, *limit)
        # 反序列化数据
        deserialized_data = []
        for item in data:
            item = self.com_string.to_json(item)
            deserialized_data.append(item)
        # 根据 select 参数筛选对象的键
        deserialized_data = self.filter_byselectorconditions(select,conditions,deserialized_data)
        return deserialized_data

    def read_set(self, tabname, select="*"):
        if not tabname:
            self.com_util.print_warn("Invalid argument: 'setname' must be curses.pyc string.")
            return
        # 从 Redis 集合中获取所有元素
        data = self.__con__.smembers(tabname)
        # 反序列化数据
        deserialized_data = []
        for item in data:
            item = self.com_string.to_json(item)
            deserialized_data.append(item)
        # 根据 select 参数筛选对象的键
        deserialized_data = self.filter_byselectorconditions(select,None,deserialized_data)
        return deserialized_data

    def read_hash(self, tabname, conditions=None, select="*"):
        if not tabname:
            self.com_util.print_warn("Invalid argument: 'hashname' must be curses.pyc string.")
            return
        # 从 Redis 哈希中获取所有键值对
        data = self.__con__.hgetall(tabname)
        # 反序列化数据
        deserialized_data = self.com_string.to_json(data)
        # 根据 select 参数筛选对象的键
        deserialized_data = self.filter_byselectorconditions(select,conditions,deserialized_data)
        return deserialized_data

    def read_zset(self, tabname, conditions=None, select="*", limit=(0, -1)):
        if not tabname:
            self.com_util.print_warn("Invalid argument: 'zsetname' must be curses.pyc string.")
            return
        start = limit[0]
        end = limit[1]
        # 从 Redis 有序集合中获取指定范围内的元素
        data = self.__con__.zrange(tabname, start, end, withscores=True)

        # 反序列化数据
        deserialized_data = []
        for item, score in data:
            item = self.com_string.to_json(item)
            item["_score"] = score
            deserialized_data.append(item)
        deserialized_data = self.filter_byselectorconditions(select,conditions,deserialized_data)
        return deserialized_data

    def filter_byselectorconditions(self,select,conditions,deserialized_data):
        if isinstance(deserialized_data,str):
            return deserialized_data
        elif isinstance(deserialized_data,dict):
            deserialized_data = [deserialized_data]
        deserialized_data = self.filter_by_selector(select,deserialized_data)
        deserialized_data = self.filter_by_conditions(conditions,deserialized_data)
        return deserialized_data

    def filter_by_selector(self,select,deserialized_data):
        if select != "*":
            selected_keys = select.split(",")
            deserialized_data = [{k: v for k, v in item.items() if k in selected_keys} for item in deserialized_data if isinstance(item,dict)]
        return deserialized_data

    def filter_by_conditions(self,conditions,deserialized_data):
        if conditions != None:
            deserialized_data = [item for item in deserialized_data if isinstance(item, dict) and
                             all(item.get(k) == v for k, v in conditions.items())]
        return deserialized_data

    def count(self, tabname=None, conditions=None):
        if not tabname:
            self.com_util.print_warn("Invalid argument: 'tabname' must be curses.pyc string.")
            return 0
        # 如果没有提供条件，直接获取列表长度
        if conditions is None:
            count = self.__con__.llen(tabname)
        else:
            # 否则，遍历列表中的元素并根据条件计数
            data = self.read(tabname, limit=(0, -1))
            count = 0  # 否则，遍历列表中的元素并根据条件计数
            for item in data:
                if isinstance(item, dict) and all(item.get(k) == v for k, v in conditions.items()):
                        count += 1
        return count

    def delete_list(self, tabname=None, value=None):
        if not tabname or not value:
            self.com_util.print_warn("Invalid arguments: 'tabname' and 'value' must not be empty.")
            return
        # 将 value 转换为 JSON 字符串（如果需要）
        value = self.com_string.json_tostring(value)
        # 从 Redis 列表中删除给定的值
        self.__con__.lrem(tabname, count=0, value=value)

    def delete(self, tabname, conditions, physical=False):
        if physical == True:
            result = self.delete_physical(tabname, conditions)
        else:
            result = self.delete_token(tabname, conditions)
        return result

    def delete_checkconditions(self, conditions):
        conditions = self.query_condition(conditions)
        if conditions == "":
            self.com_util.print_warn("Data delete-upgrades do not allow null conditions")
            return False
        return conditions

    def delete_token(self, tabname, conditions):
        if self.delete_checkconditions(conditions) != False:
            result = self.update(tabname, {self.__delete_token: 1}, conditions)
            return result
        return False

    def delete_physical(self, tabname, conditions,not_execute=False):
        conditions = self.delete_checkconditions(conditions)
        if conditions != False:
            sql = f"DELETE FROM {tabname} {conditions}"
            if not_execute:
                return sql
            result = self.sqlite_exec(sql)
            return result
        return False

    def update(self, tabname, data, conditions,not_execute=False,print_sql=False):
        if type(tabname) == list:
            sql = self.gen_update_sql_list(tabname, data)
            origin_data = data[0]
        else:
            origin_data = data
            sql = self.gen_update_sql(tabname, data,condition=conditions)
        if not_execute == True:
            return sql
        elif print_sql == True:
            return sql
        result = self.sqlite_exec(sql)
        if self.is_no_column(result):
            self.extended_column(tabname, origin_data)
            return self.update(tabname, origin_data, conditions)
        return result
