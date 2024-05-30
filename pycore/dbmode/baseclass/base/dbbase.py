from pycore.base.base import Base
from pycore.utils_linux import arr
from pycore.dbmode.baseclass.base.global_provider import global_ojb

class DBBase(Base):

    def set_globl_session(self,session):
        global_ojb["session"] = session

    def get_globl_session(self):
        return global_ojb.get("session")

    def set_globl_engine(self,engine):
        global_ojb["engine"] = engine

    def get_globl_engine(self):
        return global_ojb.get("engine")

    def set_globl_table_map(self,table_map):
        global_ojb["table_map"] = table_map

    def get_globl_table_map(self):
        return global_ojb.get("table_map")

    def gen_limit_sql(self, limit, default_limit_length=1000):
        if not limit:
            return (None, 0)
        if isinstance(limit, str):
            limit = limit.split(',')
            limit_start = int(limit[0])
            offset = int(arr.get_list_value(limit, 1, 0))
        elif isinstance(limit, int):
            limit_start = limit
            offset = 0
        elif isinstance(limit, (tuple, list)):
            limit_start = int(limit[0])
            offset = int(arr.get_list_value(limit, 1, 0))
            if limit_start == 0 and offset > 0:
                offset, limit_start = limit_start, offset
        else:
            limit_start = default_limit_length
            offset = 0
        return (limit_start, offset)

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