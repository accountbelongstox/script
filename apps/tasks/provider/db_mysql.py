
from pycore.base.base import *
# from pycore.dbmode.baseclass.table_class import TableClass
# import re
# from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, DECIMAL, BigInteger, \
#     SmallInteger, LargeBinary, Float, Numeric, Date
# from sqlalchemy.ext.declarative import declarative_base
# SqlalchemyBase = declarative_base()

from pycore.dbmode.mysql import Mysql

mysql_config = {
    'mysql_user': 'root',
    'mysql_password': '123456',
    'mysql_host': 'localhost',
    'mysql_port': '3306',
    'mysql_database': 'dbtask'
}

tables = [
            {
                "tabname": "test",
                "fixed_name": "test",
                "fields": {
                    "text": "TEXT",
                    "origin_type": "TEXT",
                    "read": "REAL",
                }
            },
            {
                "tabname": "translation_dictionary",
                "fixed_name": "translation_dictionary",
                "fields": {
                    "word": "VARCHAR(100) UNIQUE",
                    "language": "TEXT",
                    "translate_bing": "TEXT",
                    "last_time": "DATETIME",
                    "read": "INTEGER",
                    "read_time": "DATETIME",
                    "word_sort": "VARCHAR(100)",
                    "phonetic_us": "VARCHAR(50)",
                    "phonetic_us_sort": "VARCHAR(50)",
                    "phonetic_us_length": "INTEGER",
                    "phonetic_uk": "VARCHAR(50)",
                    "phonetic_uk_sort": "VARCHAR(50)",
                    "phonetic_uk_length": "INTEGER",
                    "word_length": "INTEGER",
                }
            },
            {
                "tabname": "translation_group",
                "fixed_name": "translation_group",
                "fields": {
                    "group_n": "VARCHAR(200) UNIQUE",
                    "uid": "INTEGER",
                    "group_type": "VARCHAR(100)",
                    "language": "TEXT",
                    "count": "INTEGER",
                    "link_words": "TEXT",
                    "word_frequency": "TEXT",
                    "include_words": "TEXT",
                    "include_words_count": "INTEGER",
                    "invalid_words": "TEXT",
                    "invalid_words_count": "INTEGER",
                    "valid_words": "TEXT",
                    "valid_words_count": "INTEGER",
                    "last_time": "DATETIME",
                    "word_read": "INTEGER",
                    "origin_text": "FILE",
                    "sentence": "TEXT",
                }
            },
            {
                "tabname": "translation_voices",
                "fixed_name": "translation_voices",
                "fields": {
                    "group_id": "INTEGER",
                    "sentence": "TEXT",
                    "voice": "TEXT",
                    "md5": "CHAR(32) UNIQUE",
                    "link_words": "TEXT",
                    "last_time": "DATETIME",
                    "read": "INTEGER",
                }
            },
            {
                "tabname": "translation_notebook",
                "fixed_name": "translation_notebook",
                "fields": {
                    "group_id": "INTEGER",
                    "user_id": "INTEGER",
                    "word_id": "INTEGER",
                    "reference_url": "TEXT",
                    "last_time": "DATETIME",
                    "read": "INTEGER",
                }
            },
            {
                "tabname": "user",
                "fixed_name": "user",
                "fields": {
                    "user": "VARCHAR(100) UNIQUE",
                    "pwd": "VARCHAR(32)",
                    "role": "INTEGER",
                    "trans_count": "INTEGER",
                    "last_login": "TEXT",
                    "last_time": "DATETIME",
                    "register_time": "DATETIME",
                    "register_ip": "VARCHAR(32)",
                    "read": "INTEGER",
                }
            },
            {
                "tabname": "user_gtu_map",
                "fixed_name": "user_gtu_map",
                "fields": {
                    "userid": "INTEGER",
                    "group_id": "INTEGER",
                    "group_map": "TEXT",
                }
            },
            {
                "tabname": "user_gtu_haveread",
                "fixed_name": "user_gtu_haveread",
                "fields": {
                    "userid": "INTEGER",
                    "read_ids": "TEXT",
                    "read_time_day": "DATETIME",
                    "read_time": "DATETIME",
                }
            },
            {
                "tabname": "user_gtu_readcount",
                "fixed_name": "user_gtu_readcount",
                "fields": {
                    "userid": "INTEGER",
                    "read_map": "TEXT",
                }
            },
            {
                "tabname": "translation_dictionarymap",
                "fixed_name": "translation_dictionarymap",
                "fields": {
                    "wordids": "TEXT",
                    "words": "TEXT",
                    "count": "INTEGER",
                    "words_count": "INTEGER",
                    "ids_count": "INTEGER",
                }
            },
        ]
db = Mysql(mysql_config,tables)
