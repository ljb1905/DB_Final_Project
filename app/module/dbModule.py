import pymysql

class Database():
    def __init__(self):
        self.db = pymysql.connect(host='localhost',
                                  user='movie',
                                  password='123456',
                                  db='DBProject',
                                  charset='utf8')
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def execute(self, query, args={}):
        self.cursor.execute(query, args)

    def executeOne(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row

    # 여러개 데이터 select
    def executeAll(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row

    # insert
    def commit(self):
        self.db.commit()
