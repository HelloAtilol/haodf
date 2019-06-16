# -*- coding: utf-8 -*-

"""
编写创建数据库的类，并构建connectMysql方法
author:王诚坤
date：2018/10/16
update: 2019/03/20
"""

import pymysql
import csv


class MySQLCommand(object):
    # 初始化类
    def __init__(self):
        # 数据库地址
        self.host = '192.168.1.181'
        # 端口号
        self.port = 3306
        # 用户名
        self.user = 'sim509'
        # 密码
        self.password = 'sim509'
        # 数据库名
        self.db = 'haodf'

    def connectMysql(self, table='topic'):
        """
        建立数据库连接
        :return:
        """
        try:
            self.table = table
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user,
                                        passwd=self.password, db=self.db, charset='utf8')
            self.cursor = self.conn.cursor()
            print(self.table, "表已连接！")
        except pymysql.Error as e:
            print('连接数据库失败！')
            print(e)

    def insertData(self, data_dict, primary_key='msgId'):
        """
        将数据插入数据库，首先检查数据是否已经存在，如果存在则不插入
        :param data_dict: 要插入的数据字典
        :param primary_key: 主键
        :return:
        """
        # 检测数据是否存在
        if primary_key is not "":
            sqlExit = "SELECT %s FROM %s WHERE %s = '%s' " % (primary_key, self.table, primary_key, data_dict[primary_key])
            # 执行查找语句
            # print(sqlExit)
            res = self.cursor.execute(sqlExit)
            if res:
                # print('数据已经存入数据库', res)
                return 0
        # 数据不存在，则执行插入操作
        try:
            # 拼接属性名
            cols = ','.join(data_dict.keys())
            # 拼接属性名对应的值
            values = '","'.join(data_dict.values())
            # 插入语句
            sql = "INSERT INTO %s (%s) VALUES (%s)" % (self.table, cols, '"' + values + '"')
            # print(sql)
            try:
                # 执行插入操作
                result = self.cursor.execute(sql)
                insert_id = self.conn.insert_id()
                self.conn.commit()

                if result:
                    # print('插入成功', insert_id)
                    return insert_id + 1
            except pymysql.Error as e:
                # 如果出现异常，执行回滚操作
                self.conn.rollback()
                if "key 'PRIMARY'" in e.args[1]:
                    print('数据已存在，未再次插入！')
                else:
                    print("插入数据失败，原因 %d: %s" % (e.args[0], e.args[1]))
        except pymysql.Error as e:
            print("数据库错误，原因 %d: %s" % (e.args[0], e.args[1]))

    def select_order(self, title_list, situation='', order_title="", order_type='ASC'):
        """
        查找所有数据中的某几列
        :param order_type: 排序方式，ASC为升序，DESC为降序；
        :param order_title: 排序的列的名称(title)；
        :param situation: 条件语句，即WHERE语句；
        :param title_list: 要查找的列的名称；
        :return:查询的结果;
        """
        title = ','.join(title_list)
        if order_title is not "":
            order_title = "ORDER BY %s %s" % (order_title, order_type)
        sql = "SELECT %s FROM %s %s %s ;" % (title, self.table, situation, order_title)
        self.cursor.execute(sql)
        return self.cursor

    def select_distinct(self, title="talker"):
        """
        获取所有的群编号(talker的数量)
        :param title:默认为talker，可以替换使用其他方式;
        :return:查询结果的元组;
        """
        sqlChatRoom = "SELECT DISTINCT %s FROM %s;" % (title, self.table)
        res = self.cursor.execute(sqlChatRoom)
        if res:
            result = self.cursor.fetchall()
            return result
        else:
            raise Exception("%s 没有内容！" % title)

    def update_database(self, datadict, situation):
        part_sql = ""
        for key, value in datadict.items():
            part_sql = part_sql + "%s = %s," % (key.replace(" ", "_"), str(value))
        sql = "UPDATE %s SET %s %s" % (self.table, part_sql[0: -1], situation)
        # print(sql)
        res = self.cursor.execute(sql)
        self.conn.commit()
        return res

    def closeMysql(self):
        """
        关闭数据库连接
        :return:
        """
        self.cursor.close()
        self.conn.close()
        print(self.table, '数据库连接已关闭！')


def main():
    """
    导入数据的操作。
    只需要修改表名和文件名即可。(推荐文件编码格式为utf-8.否则潜在不能正确编码的问题。)
    :return:
    """
    # 初始化并建立数据库连接
    conn = MySQLCommand()
    conn.connectMysql(table="wechat_contact")
    # 读取csv文件
    with open('data/wechat_contact_0314.csv', 'r', encoding="UTF-8") as f:
        csv_file = csv.DictReader(f)
        i = 0
        while True:
            try:
                i = i + 1
                data_dict = next(csv_file)
            except UnicodeDecodeError as e:
                print(e)
                print(data_dict)
                break
            except StopIteration:
                print('遍历结束！')
                break
            try:
                conn.insertData(data_dict, primary_key="username")
            except pymysql.err.ProgrammingError as e:
                print(e)
                print(str(i) + '行出现错误，手动处理')
                print(data_dict)
    # 关闭数据库连接
    conn.closeMysql()


if __name__ == '__main__':
    main()
