
import sqlite3
import os
# from func_timeout import func_set_timeout,exceptions
import sys


class sqliteNative:

    def __init__(self, db_file, connect_timeout=5.0):
        self.connection = sqlite3.connect(db_file, timeout=connect_timeout)
        self.cursor = self.connection.cursor()

    def insert(self, query, params):
        try:
            self.cursor.executemany(query, params)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()

    def execute(self, code):
        try:
            self.cursor.execute(code)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()

    def executemany(self, code, slist):
        try:
            self.cursor.executemany(code, slist)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()

    @staticmethod
    def dictFactory(cursor, row):
        """将sql查询结果整理成字典形式"""
        d = {}
        for index, col in enumerate(cursor.description):
            d[col[0]] = row[index]
        return d

    def query(self, query, *args):
        self.connection.row_factory = self.dictFactory  # 得到一个可以执行SQL语句并且将结果作为字典返回的游标
        self.cursor = self.connection.cursor()
        result = None
        timeout = None
        if args and len(args) == 1:
            timeout = args[0]

        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def __del__(self):
        self.connection.close()