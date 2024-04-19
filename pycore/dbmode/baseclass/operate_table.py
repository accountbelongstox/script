from pycore.dbmode.baseclass.base.dbbase import DBBase
from pycore.dbmode.baseclass.provider.common import SqlalchemyBase
from sqlalchemy import inspect

class OperateTable(DBBase):

    def __init__(self):
        pass


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
            table_class = self.create_table_class(tabname, fields)
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
        print("columns",columns)
        return columns

    def get_tables(self):
        inspector = inspect(self.engine)
        return inspector.get_table_names()



operate_table = OperateTable()