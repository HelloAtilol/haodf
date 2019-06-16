# -*- coding: utf-8 -*-
"""
# @Time    : 2019/6/16 14:17
# @Author  : 王诚坤
# @File    : getHaodf.py
# @des     : 爬取好大夫的所有网络咨询，并保存到数据库：haodf
"""

from tools import ConnectDatabase as conn
from selenium import webdriver
import datetime
import requests

driver = webdriver.Chrome()
# 连接数据库
db_conn = conn.MySQLCommand()
# 爬取文件开始日期
CURRENT_DATE = "20180105"
# 爬取文件结束日期
END_DATE = "20181231"
# 基础url
BASE_URL = "https://www.haodf.com/sitemap-zx/"


def saveURL(current_date):

    current_page = 1
    page_ele = "尾页"
    while page_ele == "尾页":
        print("------------------" * 3)
        print("**********正在查找%s日的第%d页的内容************" % (current_date.strftime('%Y%m%d'), current_page))
        temp_url = "%s%s_%d/" % (BASE_URL, current_date.strftime('%Y%m%d'), current_page)
        driver.get(temp_url)

        # 找到所有的标签
        item = driver.find_elements_by_xpath('//li/a')
        for i in item:
            db_url = {"qa_time": str(current_date.strftime('%Y%m%d')), "qa_status": '0',
                      "qa_url": i.get_attribute('href'), "qa_title": i.text.replace("\"", "\'")}
            # 将数据保存到数据库
            db_conn.insertData(db_url, primary_key="qa_url")

        # 翻页
        page_ele = driver.find_elements_by_class_name("p_num")[-1].text
        # print(page_ele)
        current_page += 1


def getAllURL():
    db_conn.connectMysql(table="all_url")
    current_date = datetime.datetime.strptime(CURRENT_DATE, '%Y%m%d')
    end_date = datetime.datetime.strptime(END_DATE, '%Y%m%d')
    # 按照日期遍历
    while current_date <= end_date:
        saveURL(current_date)
        current_date += datetime.timedelta(days=1)


def main():
    # 获取所有的URL
    getAllURL()


if __name__ == '__main__':
    main()
    driver.close()
