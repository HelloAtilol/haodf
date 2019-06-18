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
# select_conn = conn.MySQLCommand()
# select_conn.connectMysql(table="all_url")
# update_conn = conn.MySQLCommand()

driver = webdriver.Chrome()


def split_relative(qa_number, relative_soups):
    """
    负责解析相关问答、文章和疾病
    :param qa_number: 访问页面对应的编号
    :param relative_soups: 需要解析的Beautifulsoup对象
    :return:
    """
    for relative_soup in relative_soups:
        # print(relative_soup)
        r_text = relative_soup.p.find("span", {"class": "fl f18"}).text
        # 相关标签，0代表问答；1代表文章；2代表疾病
        if "相关回复" in r_text:
            tag = 0
        elif "相关文章" in r_text:
            tag = 1
        elif "相关疾病" in r_text:
            tag = 2
        rq_lis = relative_soup.find_all("li")
        for rq_li in rq_lis:
            result = {"rela_tag": tag, "rela_title": rq_li.a.string, "rela_url": rq_li.a["href"][2:],
                      "qa_number": qa_number}
            # TODO 保存到数据库
            print(result)


def split_content(qa_number, url):
    # 判断是问答是医生还是团队
    if "wenda" in url:
        doctor_patient = url.replace("https://www.haodf.com/wenda/", "").replace(".htm", "")
        _, _, patient = doctor_patient.split("_")
        update_url = {"qa_patient": patient, "qa_type": '0'}
    elif "flow_team" in url:
        doctor_patient = url.replace("https://www.haodf.com/doctorteam/", "").replace(".htm", "")
        _, _, patient = doctor_patient.split("_")
        update_url = {"qa_patient": patient, "qa_type": '0'}
    else:
        print("出现新的URL方式，请手动解析！")

    # 将页面变为Beautisoup对象
    driver.get(url)
    soup = BeautifulSoup(driver.page_source.encode('gbk'), "lxml")

    # 更新医生id
    doctor_id_soup = soup.find("span", {"class": "space_b_url"})
    update_url["qa_doctor"] = doctor_id_soup.string
    # 更新title
    title_soup = soup.find("h1", {"class": "fl f20 fn fyahei pl20 bdn"})
    if title_soup is None:
        title_soup = soup.find("div", {"class": "fl-title ellps"})
    update_url["qa_title"] = title_soup.string
    # 更改URL的status，0代表未解析，1代表已解析，其他代表异常
    # update_url["qa_status"] = '1'
    # update_conn.connectMysql(table="all_url")
    # update_conn.update_database(datadict=update_url, situation="WHERE qa_url = '%s'" % url)
    print(update_url)

    # 解析相关问答、文章、疾病 TODO， 放在一个数据库
    relative_soups = soup.find_all("div", {"class": "mt20 w670 bg_w zzx_t_repeat"})

    split_relative(qa_number=qa_number, relative_soups=relative_soups)

    # 解析QA TODO
    qa_content_soup = soup.find("div", {"class": "stream_left_content fl"})
    # 获取页数，如果有
    # page_soup = soup.find("a", {'class': 'page_turn_a', 'rel': 'true'})
    # page_num = page_soup.text.split("\xa0")[1]
    # print(page_num)


def main():
    # 从数据库中读取未解析页面的URL
    title_list = ["qa_url"]
    situation = "WHERE qa_status = '0'"
    # select_cursor = select_conn.select_order(title_list=title_list, situation=situation)
    while True:
        # result = select_cursor.fetchone()
        # if result is None:
        #     break
        # 语音
        # temp_url = 'https://www.haodf.com/wenda/kongweimin_g_5974272953.htm'
        # 医生
        # temp_url = 'https://www.haodf.com/wenda/abc195366_g_5673322365.htm'
        # 团队
        # temp_url = 'https://www.haodf.com/doctorteam/flow_team_6465190653.htm'
        # 分页 且 无相关
        temp_url = 'https://www.haodf.com/wenda/fingerprints_g_6403406888.htm'

        # temp_url = result[0]
        print(temp_url)
        # TODO 这里尽量传递一个url对应的编号，建立外键
        split_content('1', temp_url)
        break


if __name__ == '__main__':
    main()
    driver.close()
    # select_conn.closeMysql()
