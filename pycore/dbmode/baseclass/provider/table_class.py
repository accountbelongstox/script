
from sqlalchemy.ext.declarative import declarative_base

# import sqlalchemy.types as types
# from sqlalchemy.orm import sessionmaker

SqlalchemyBase = declarative_base()
class TableClass(SqlalchemyBase):
    __abstract__ = True
    def __init__(self):
        pass
    def _asdict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
