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
update_conn = conn.MySQLCommand()

driver = webdriver.Chrome()


def split_content(url):

    # 判断是问答是医生还是团队
    if "wenda" in url:
        doctor_patient = url.replace("https://www.haodf.com/wenda/", "").replace(".htm", "")
        print(doctor_patient.split("_"))
        doctor, _, patient = doctor_patient.split("_")
        update_url = {"qa_doctor": doctor, "qa_patient": patient, "qa_type": '0'}
    else:
        print("出现新的URL方式，请手动解析！")

    # 将页面变为Beautisoup对象
    driver.get(url)
    soup = BeautifulSoup(driver.page_source.encode('gbk'), "lxml")

    # 更新title
    title = soup.title.string
    update_url["qa_title"] = title
    # 更改URL的status，0代表未解析，1代表已解析，其他代表异常
    # update_url["qa_status"] = '1'
    update_conn.connectMysql(table="all_url")
    update_conn.update_database(datadict=update_url, situation="WHERE qa_url = '%s'" % url)
    # print(update_url)

    # 解析QA

    # 解析相关问答、文章、疾病


def main():
    # 从数据库中读取未解析页面的URL
    title_list = ["qa_url"]
    situation = "WHERE qa_status = '0'"
    select_cursor = select_conn.select_order(title_list=title_list, situation=situation)
    while True:
        result = select_cursor.fetchone()
        if result is None:
            break
        # temp_url = https://www.haodf.com/wenda/abc195366_g_5673322365.htm
        temp_url = result[0]
        print(temp_url)
        split_content(temp_url)
        break


if __name__ == '__main__':
    main()
    driver.close()
    select_conn.closeMysql()
