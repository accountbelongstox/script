from kernel.db_baseclass.dbcommon import DBCommon
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

class Sqlite(DBCommon):
    session = None

    def __init__(self, args):
        pass

    # 自动创建数据库
    def main(self, args):
        self.init_database()
        return self.session

    def connect(self):
        db_name = self.load_module.get_control_name()
        db_name = f"control_{db_name}_sqlite.db"
        database_dir = self.load_module.get_control_core_dir(f"db")
        if os.path.exists(database_dir) != True:
            os.mkdir(database_dir)
        database_file = os.path.join(database_dir, db_name)
        engine = create_engine(f'sqlite:///{database_file}', poolclass=QueuePool)
        Session = sessionmaker(bind=engine)
        session = Session()
        self.session = session
        self.engine = engine
        super().__init__(session, engine)
