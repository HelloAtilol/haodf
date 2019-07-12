# -*- coding: utf-8 -*-
"""
# @Time    : 2019/7/4 18:27
# @Author  : 王诚坤
# @File    : multi_start.py
# @des     : 多线程启动函数
"""

from multi_haodf import getContent
import threading
from tools import ConnectDatabase as conn


def main():
    # 查询数据库连接
    select_conn = conn.MySQLCommand()
    select_conn.connectMysql(table="all_url")

    # 确定线程数量
    num = int(input("Threading Number:\t"))

    print("Current Number:\t %d" % num)
    # 获取启动函数
    start = getContent.start

    # 查询
    title_list = ["qa_number", "qa_url"]
    situation = "WHERE qa_status = '0' or qa_status ='3'"
    select_cursor = select_conn.select_order(title_list=title_list, situation=situation)

    # 定义一个tag控制循环
    tag = True

    while tag:
        th_list = []
        for i in range(num):
            temp_result = select_cursor.fetchmany(10)
            if temp_result[0] is None:
                tag = False
                break
            th = threading.Thread(target=start, args=(temp_result,))
            th.start()
            th_list.append(th)

        # 使主线程等待所有子线程执行完成
        for t in th_list:
            t.join()
            
    # 关闭数据库连接
    select_conn.closeMysql()


if __name__ == '__main__':
    main()

