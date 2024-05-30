from pycore.dbmode.baseclass.abs.dbcommon import DBCommon
from pycore.dbmode.baseclass.base.dbbase import DBBase
from pycore.dbmode.baseclass.init_database import dbinit
from pycore.dbmode.baseclass.operate_table import operate_table
from pycore.dbmode.baseclass.provider.common import SqlalchemyBase
from pycore.utils_linux import arr
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
from sqlalchemy import asc, desc, inspect
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, literal
# from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, DECIMAL, BigInteger, \
#     SmallInteger, LargeBinary, Float, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.sql.expression import in_, like
from apps.tasks.provider.mock_data import mock

class DBCommon(DBBase,DBCommon):
    def __init__(self, session, engine,tables):
        self.session = session
        self.tablemaps = {}

    def main(self):
        pass

    def init_database(self):
        self.connect()
        dbinit.init_database()
        # self.save("test2",{'test':'李虎'})
        # for data in mock.get_mock():
        #     self.save("duijie",data)

        # self.read("duijie")

        # self.update(tabname="test2", data={"test": "尺寸"}, conditions={"id": 3})
        # self.delete_physical("test2",conditions={"id": 3})
        # t=self.count("test2",{"test":"你好"})
        # print(t)
        # SqlalchemyBase.metadata.create_all(self.engine)


    def commit(self):
        session = self.get_session()
        session.commit()

    def close(self):
        session = self.get_session()
        session.close()

    def get_session(self):
        if not self.session:
            self.connect()
            self.session = self.get_globl_session()
        return self.session

    def get_tablemaps(self):
        if not self.tablemaps:
            self.tablemaps = dbinit.get_tablemaps()
        return self.tablemaps

    def save(self, tabname=None, data=None, result_id=True):
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        if not table_class:
            self.warn("save tabname must be provided")
            return
        if not data:
            self.warn("save data must be provided")
            return
        session = self.get_session()
        if isinstance(data, list):
            for index in range(len(data)):
                item = data[index]
                if isinstance(item, dict):
                    _id = item.get("_id")
                    if None != _id:
                        if None == item.get("id"):
                            item['id'] = _id
                        del item['_id']
                        data[index] = item
        try:
            if isinstance(data, list):
                try:
                    session.bulk_insert_mappings(table_class, data)
                except IntegrityError as e:
                    session.rollback()
                    for item in data:
                        try:
                            stmt = insert(table_class).prefix_with("OR IGNORE").values(item)
                            session.execute(stmt)
                        except Exception as e_inner:
                            self.warn(self.com_dbbase.trim_data(item))
                            self.warn(e_inner)
                            session.rollback()
            elif isinstance(data, dict):
                stmt = insert(table_class).values(data)
                session.execute(stmt)
                # record = table_class(**data)
                # session.add(record)
                # new_id = getattr(record, record.__mapper__.primary_key[0].name)
                # session.commit()
            else:
                self.warn("save Invalid data type for 'data' parameter. Expected list or dict.")
                return
            session.commit()
        except Exception as e:
            self.warn(dbinit.trim_data(data))
            self.warn("db_save Exception")
            self.warn(e)
            session.rollback()
        finally:
            session.close()

    def extract_dict_values(self, d):
        # 此处_asdict 由数据基类db_baseclass/table_class 中提供
        d = d._asdict()
        return d

    def query_sqlchameylisttojson(self, lst):
        for i in range(len(lst)):
            record = lst[i]
            record = self.extract_dict_values(record)
            lst[i] = record
        lst = arr.list_tojson(lst)
        return lst

    def filter_query(self, query_obj, table_class, conditions=None):
        if not conditions:
            return query_obj
        condition_clauses = []
        null_char = [None, 'null', '']
        for key, value in conditions.items():
            if isinstance(value, str):
                value = value.strip().replace("'", "")
            field_obj = getattr(table_class, key)
            if isinstance(value, list):
                condition_clauses.append(field_obj.in_(value))
            elif isinstance(value, str):
                check_like = self.check_like(value)
                if check_like == 'both':
                    condition_clauses.append(field_obj.like(value))
                elif check_like == 'beginning':
                    value = value.strip('%')
                    condition_clauses.append(field_obj.startswith(value))
                elif check_like == 'end':
                    value = value.strip('%')
                    condition_clauses.append(field_obj.endswith(value))
                elif value.startswith('<'):
                    condition_clauses.append(field_obj < literal(value[1:]))
                elif value.startswith('>'):
                    condition_clauses.append(field_obj > literal(value[1:]))
                elif value.startswith('>'):
                    condition_clauses.append(field_obj > literal(value[1:]))
                elif value.startswith('!='):
                    condition_clauses.append(field_obj != literal(value[2:]))
                elif value in null_char:
                    condition_clauses.append(field_obj.in_(null_char))
                else:
                    condition_clauses.append(field_obj == value)
            else:
                condition_clauses.append(field_obj == value)
        query_obj = query_obj.filter(and_(*condition_clauses))
        return query_obj

    def read(self, tablename, conditions=None, limit=(0, 1000), select=None, sort=None, result_object=True,
             print_sql=False, read_delete=False):
        session = self.get_session()
        tablemaps = self.get_tablemaps()
        table_class = tablemaps[tablename]
        query_obj = session.query(table_class)

        if read_delete == False:
            if conditions == None:
                conditions = {
                    "is_delete": "!=1"
                }
            else:
                conditions["is_delete"] = "!=1"
        # Select specific columns
        if select and select != "*":
            columns = [getattr(table_class, col_name.strip()) for col_name in select.split(',')]
            query_obj = query_obj.with_entities(*columns)
        # Apply conditions
        query_obj = self.filter_query(query_obj, table_class, conditions=conditions)
        # Apply limit
        limit = self.gen_limit_sql(limit)
        offset = limit[1]
        query_len = limit[0]
        # return records
        # else:
        # print('not limit')
        # Apply sorting
        if sort:
            for field, order in sort.items():
                if order.upper() == 'ASC':
                    query_obj = query_obj.order_by(asc(getattr(table_class, field)))
                elif order.upper() == 'DESC':
                    query_obj = query_obj.order_by(desc(getattr(table_class, field)))
                else:
                    self.warn(f"Unsupported sort order: {order}")
        if limit:
            # print('offset', offset, 'query_len', query_len)
            query_obj = query_obj.offset(offset).limit(query_len)
        if print_sql:
            print(str(query_obj.statement.compile()))
        records = query_obj.all()
        if result_object:
            records = self.query_sqlchameylisttojson(records)
        session.close()

        if isinstance(records, list):
            records = [item[0] if (isinstance(item, list) and len(item) == 1) else item for item in records]
        print(records)
        return records

    def delete(self, tabname=None, conditions=None, physical=False):
        data = {
            dbinit.get_delete_token(): 1
        }
        if not physical:
            return self.update(tabname=tabname, data=data, conditions=conditions)
        else:
            return self.delete_physical(tabname=tabname, conditions=conditions)

    def get_id(self, tabname, conditions):
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        session = self.get_session()
        if table_class:
            try:
                query = session.query(table_class)
                query = self.filter_query(query, table_class, conditions=conditions)
                result = query.first()
                return result.id if result and hasattr(result, 'id') else 0
            finally:
                session.close()
        else:
            self.warn(f"No table_class found for tabname: {tabname}")
            return 0

    def count(self, tabname=None, conditions=None, select="*", print_sql=False):
        tablemaps = self.get_tablemaps()
        session = self.get_session()
        table_class = tablemaps.get(tabname)
        print("table_class", table_class)
        if table_class:
            try:
                query = session.query(table_class)
                query = self.filter_query(query, table_class, conditions=conditions)
                if print_sql:
                    print(str(query))
                return query.count()
            finally:
                session.close()
        else:
            self.warn(f"No table_class found for tabname: {tabname}")
            return 0

    def delete_physical(self, tabname, conditions=None, not_execute=False):
        if not conditions:
            self.warn(f"{tabname} delete must need conditions")
            return 0
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        session = self.get_session()
        try:
            query = session.query(table_class)
            query = self.filter_query(query, table_class, conditions=conditions)
            if not_execute:
                print(str(query))
                return 0
            else:
                affected_rows = query.delete(synchronize_session=False)
                session.commit()
                return affected_rows
        finally:
            session.close()

    def update(self, tabname=None, data=None, conditions=None, not_execute=False, print_sql=False):
        if not conditions:
            self.warn(f"{tabname} update must need conditions")
            return 0
        data = arr.dict_escape(data)
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        session = self.get_session()
        try:
            query = session.query(table_class)
            query = self.filter_query(query, table_class, conditions=conditions)
            if not_execute or print_sql:
                print(str(query))
                return 0
            if not not_execute:
                affected_rows = query.update(data)
                session.commit()
                #
                # if len(affected_rows) == 1:
                #     return affected_rows
                # else:
                #     return affected_rows
        finally:
            session.close()


    def connect(self):
        raise NotImplementedError("Subclass must implement connect method")
