# -*- coding: utf-8 -*-
"""
# @Time    : 2019/6/16 18:34
# @Author  : 王诚坤
# @File    : getContent.py
# @des     :解析页面
"""

from tools import ConnectDatabase as conn
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# 连接数据库
select_conn = conn.MySQLCommand()
select_conn.connectMysql(table="all_url")

driver = webdriver.Chrome()


def split_content(url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source.encode('gbk'), "lxml")
    result = soup.title.string
    print(result)


def main():
    # 从数据库中读取未解析页面的URL
    title_list = ["qa_url"]
    situation = "WHERE qa_status = '0'"
    select_cursor = select_conn.select_order(title_list=title_list, situation=situation)
    while True:
        result = select_cursor.fetchone()
        if result is None:
            break
        temp_url = result[0]
        print(temp_url)
        split_content(temp_url)
        break


if __name__ == '__main__':
    main()
    driver.close()
    select_conn.closeMysql()
