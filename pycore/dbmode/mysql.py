from pycore.dbmode.baseclass.dbcommon import DBCommon
from sqlalchemy import create_engine #,Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker

class Mysql(DBCommon):
    session = None
    config = {}
    tables = {}

    def __init__(self,config,tables):
        self.config = config
        self.tables = tables
        self.main()

    def main(self):
        self.init_database()

    def connect(self):
        if self.session != None:
            return self.session
        username = self.config.get('mysql_user')
        password = self.config.get('mysql_password')
        host = self.config.get('mysql_host')
        port = self.config.get('mysql_port')
        db_name = self.config.get('mysql_database')
        if username and password:
            engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}')
        else:
            engine = create_engine(f'mysql+pymysql://{host}:{port}/{db_name}')
        Session = sessionmaker(bind=engine)
        session = Session()

        self.set_engine_to_global(engine)
        self.set_session_to_global(session)
        self.set_table_map_to_global(self.tables)

        return session

    def set_engine_to_global(self,engine):
        self.set_globl_engine(engine)
    def set_session_to_global(self,session):
        self.set_globl_session(session)
    def set_table_map_to_global(self,table_map):
        self.set_globl_table_map(table_map)



