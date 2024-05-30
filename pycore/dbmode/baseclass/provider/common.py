# from pycore.dbmode.baseclass.abs.dbcommon import DBCommon
# from pycore.dbmode.baseclass.base.dbbase import DBBase
# from pycore.dbmode.baseclass.init_database import DBInit
# from pycore.dbmode.baseclass.operate_table import OperateTable
# from pycore.utils_linux import arr
# # from sqlalchemy import create_engine
# # from sqlalchemy.orm import sessionmaker
# from sqlalchemy import asc, desc, inspect
# from sqlalchemy import insert
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy import and_, literal
# # from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, DECIMAL, BigInteger, \
# #     SmallInteger, LargeBinary, Float, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base
from pycore.dbmode.baseclass.base.global_provider import global_ojb
engine = global_ojb.get("engine")

SqlalchemyBase = declarative_base()