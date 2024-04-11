
from pycore.dbmode.baseclass.dbcommon import DBCommon
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Mysql(DBCommon):
    session = None
    def __init__(self, args):
        pass

    def main(self, args):
        self.init_database()

    def connect(self):
        if self.session != None:
            return self.session
        username = self.com_config.get_global('mysql_user')
        password = self.com_config.get_global('mysql_password')
        host = self.com_config.get_global('mysql_host')
        port = self.com_config.get_global('mysql_port')
        db_name = self.com_config.get_global('mysql_database')
        if username and password:
            engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}')
        else:
            engine = create_engine(f'mysql+pymysql://{host}:{port}/{db_name}')
        Session = sessionmaker(bind=engine)
        session = Session()
        self.session = session
        self.engine = engine
        super().__init__(session, engine)
