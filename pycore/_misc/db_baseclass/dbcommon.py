from pycore._base import *
from pycore.db_baseclass.dbbase import *
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

SqlalchemyBase = declarative_base()


class DBCommon(Base, DBBase):
    def __init__(self, session, engine):
        self.session = session
        self.engine = engine
        pass

    def main(self, args):
        pass

    def init_database(self):
        self.connect()
        SqlalchemyBase.metadata.create_all(self.engine)

    def exist_table(self, tabname):
        tablemaps = self.get_tablemaps()
        return tabname in tablemaps

    def exist_field(self, tabname, field_name):
        tablemaps = self.get_tablemaps()
        if self.exist_table(tabname):
            table_class = tablemaps[tabname]
            return hasattr(table_class, field_name)
        return False

    def modify_field(self, tabname, fields):
        tablemaps = self.get_tablemaps()
        session = self.get_session()
        if self.exist_table(tabname):
            table_class = tablemaps[tabname]
            for field_name, new_value in fields.items():
                if self.exist_field(tabname, field_name):
                    session.query(table_class).update({getattr(table_class, field_name): new_value})
                    session.commit()
                    session.close()

    def create_table(self, tabname, fields):
        tablemaps = self.get_tablemaps()
        if isinstance(fields, list):
            fields = fields[0]
        if not self.exist_table(tabname):
            table_class = self.com_dbbase.create_table_class(tabname, fields)
            SqlalchemyBase.metadata.create_all(self.engine, [table_class.__table__])
            tablemaps[tabname] = table_class

    def query_table_info(self, tabname):
        inspector = inspect(self.engine)
        return {
            "columns": inspector.get_columns(tabname),
            "indexes": inspector.get_indexes(tabname),
            "foreign_keys": inspector.get_foreign_keys(tabname),
        }

    def get_columns(self, tabname):
        inspector = inspect(self.engine)
        columns = inspector.get_columns(tabname)
        columns = [c.get('name') for c in columns]
        return columns

    def get_tables(self):
        inspector = inspect(self.engine)
        return inspector.get_table_names()

    def commit(self):
        session = self.get_session()
        session.commit()

    def close(self):
        session = self.get_session()
        session.close()

    def get_session(self):
        if not self.session:
            self.connect()
        return self.session

    def get_tablemaps(self):
        if not self.tablemaps:
            self.tablemaps = self.com_dbbase.get_tablemaps()
        return self.tablemaps

    def save(self, tabname=None, data=None, result_id=True):
        tablemaps = self.get_tablemaps()
        table_class = tablemaps.get(tabname)
        if not table_class:
            self.com_util.print_warn("save tabname must be provided")
            return
        if not data:
            self.com_util.print_warn("save data must be provided")
            return
        session = self.get_session()
        data = self.com_dbbase.escape_andsetdate(tabname, data)
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
                            self.com_util.print_warn(self.com_dbbase.trim_data(item))
                            self.com_util.print_warn(e_inner)
                            session.rollback()
            elif isinstance(data, dict):
                stmt = insert(table_class).prefix_with("OR IGNORE").values(data)
                session.execute(stmt)
                # record = table_class(**data)
                # session.add(record)
                # new_id = getattr(record, record.__mapper__.primary_key[0].name)
                # session.commit()
            else:
                self.com_util.print_warn("save Invalid data type for 'data' parameter. Expected list or dict.")
                return
            session.commit()
        except Exception as e:
            self.com_util.print_warn(self.com_dbbase.trim_data(data))
            self.com_util.print_warn("db_save Exception")
            self.com_util.print_warn(e)
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
        lst = self.com_util.list_tojson(lst)
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
                check_like = self.com_dbbase.check_like(value)
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
        limit = self.com_dbbase.gen_limit_sql(limit)
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
                    self.com_util.print_warn(f"Unsupported sort order: {order}")
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
        return records

    def delete(self, tabname=None, conditions=None, physical=False):
        data = {
            self.com_dbbase.get_delete_token(): 1
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
            self.com_util.print_warn(f"No table_class found for tabname: {tabname}")
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
            self.com_util.print_warn(f"No table_class found for tabname: {tabname}")
            return 0

    def delete_physical(self, tabname, conditions=None, not_execute=False):
        if not conditions:
            self.com_util.print_warn(f"{tabname} delete must need conditions")
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
            self.com_util.print_warn(f"{tabname} update must need conditions")
            return 0
        data = self.com_util.dict_escape(data)
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
                if len(affected_rows) == 1:
                    return affected_rows[0]
                else:
                    return affected_rows
        finally:
            session.close()

    def connect(self):
        raise NotImplementedError("Subclass must implement connect method")
