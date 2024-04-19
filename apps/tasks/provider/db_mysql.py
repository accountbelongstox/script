from pycore.dbmode.mysql import Mysql
from apps.tasks.provider.db_tables import tables
mysql_config = {
    'mysql_user': 'root',
    'mysql_password': '123456',
    'mysql_host': 'localhost',
    'mysql_port': '3306',
    'mysql_database': 'dbtask'
}

db = Mysql(mysql_config,tables)
