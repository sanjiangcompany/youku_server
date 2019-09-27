import pymysql
from orm.db_pool import POOL


class Mysql:

    def __init__(self):
        # 建立链接
        self.conn = POOL.connection()

        # 获取游标
        self.cursor = self.conn.cursor(
            pymysql.cursors.DictCursor
        )

    # 关闭游标\链接方法
    def close_db(self):
        self.cursor.close()
        self.conn.close()

    # 查看
    def my_select(self, sql, args=None):

        self.cursor.execute(sql, args)

        res = self.cursor.fetchall()
        # [{}, {}, {}]
        # print(res)
        return res

    # 提交
    def my_execute(self, sql, args):
        try:
            # 把insert , update...一系列sql提交到mysql中
            self.cursor.execute(sql, args)

        except Exception as e:
            print(e)
