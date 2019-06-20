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


def split_content_1(qa_number, qa_list, qa_soups):
    """
    解析第一种内容的第一条，class=“zzx_yh_stream”
    :param qa_list:  问答的标签
    :param qa_number: url编号
    :param qa_soups: 问答的Beautifulsoup对象
    :return:
    """
    first_describe = qa_soups[0]

    # 患者状态和咨询时间
    user_soup = first_describe.find("div", {"class": "stream_yh_left"})
    # 状态
    patient_status = user_soup.find("div", {"class": "yh_l_states"}).span.string
    # 发表时间
    qa_time = user_soup.find("div", {"class": "yh_l_times"}).string
    # qa_author: 0是患者，1是医生
    first_result = {"qa_url": qa_number, "qa_list": qa_list, "qa_author": '0', "patient_status": patient_status, "qa_time": qa_time}

    # 咨询内容
    content = ""
    describe = first_describe.find("div", {"class": "h_s_info_cons"})
    for child in describe.children:
        if child.name is None or child.name == "script":
            continue
        if child.text is "" or "本人登录后可见" in child.text:
            continue
        content += (child.text.replace("\n", "") + "\n")
    # 去掉最后一个\n
    first_result["qa_content"] = content[:-1]
    print(first_result)
    qa_list += 1
    qa_soups.remove(first_describe)
    return split_soups_1(qa_number, qa_list, qa_soups)


def split_soups_1(qa_number, qa_list, qa_soups):
    """
    解析第一种内容的后续内容class=“zzx_yh_stream”
    :param qa_number: url的编号
    :param qa_list: 内容在问答种的编号
    :param qa_soups: 需要解析的soup的list
    :return:
    """
    for qa_soup in qa_soups:
        qa_time = qa_soup.find("div", {"class": "yh_l_times"}).string
        result = {"qa_url": qa_number, "qa_list": qa_list, "qa_time": qa_time}
        if "yi" in qa_soup.find("div", {"class": "yh_r_t_icon"}).img["src"]:
            qa_author = '1'
            result["qa_author"] = qa_author
            try:
                content = qa_soup.find("h3", {"class": "h_s_cons_title"}).text
            except AttributeError:
                content = qa_soup.find("div", {"class": "yy_vioce_box"})["src"][2:]
                result["qa_tag"] = "语音"
            result["qa_content"] = content
        else:
            qa_author = '0'
            result["qa_author"] = qa_author
            content = qa_soup.find("pre", {"class": "h_s_cons_main"}).text
            result["qa_content"] = content

            # 患者状态
            patient_status = qa_soup.find("div", {"class": "yh_l_states"}).span.string
            result["patient_status"] = patient_status
        print(result["qa_author"], result["qa_content"], result["qa_list"], result["qa_time"])
        qa_list += 1
    return qa_list


def change_split_type(split_type, qa_number, qa_list, qa_soups):
    """
    根据解析类型调用不同的解析方式
    :param split_type: 解析类型
    :param qa_number: url对应的编号
    :param qa_list: 对话顺序
    :param qa_soups: soup的list集合
    :return:
    """
    if split_type is 1:
        # 解析首页
        return split_content_1(qa_number, qa_list, qa_soups)
    elif split_type is 2:
        # 解析后续页面
        return split_soups_1(qa_number, qa_list, qa_soups)
    else:
        raise IndexError("没有对应的解析方式，请重新选值。")


def split_page(qa_number, url):
    # 判断是问答是医生还是团队, 0是医生，1是团队
    if "wenda" in url:
        doctor_patient = url.replace("https://www.haodf.com/wenda/", "").replace(".htm", "")
        _, _, patient = doctor_patient.split("_")
        update_url = {"qa_patient": patient, "qa_type": '0'}
    elif "flow_team" in url:
        doctor_patient = url.replace("https://www.haodf.com/doctorteam/", "").replace(".htm", "")
        _, _, patient = doctor_patient.split("_")
        update_url = {"qa_patient": patient, "qa_type": '1'}
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
    # zzx_yh_stream -->stream_yh_right --> h_s_cons_info
    qa_list = 1
    qa_content_soups = soup.find_all("div", {"class": "zzx_yh_stream"})
    if qa_content_soups is not None:
        split_type = 1
        qa_list = change_split_type(split_type, qa_number=qa_number, qa_list=qa_list, qa_soups=qa_content_soups)
    else:

    # 获取页数，如果有
    page_soup = soup.find("a", {'class': 'page_turn_a', 'rel': 'true'})
    page_num = page_soup.text.split("\xa0")[1]
    for i in range(1, int(page_num)):
        driver.get(url.replace(".htm", "_p_%d.htm" % (i+1)))
        soup = BeautifulSoup(driver.page_source.encode('gbk'), "lxml")
        qa_content_soups = soup.find_all("div", {"class": "zzx_yh_stream"})
        qa_list = change_split_type(split_type+1, qa_number=qa_number, qa_list=qa_list, qa_soups=qa_content_soups)


def main():
    # 从数据库中读取未解析页面的URL
    title_list = ["qa_number", "qa_url"]
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
        temp_url = 'https://www.haodf.com/doctorteam/flow_team_6465190653.htm'
        # 分页 且 无相关ss
        # temp_url = 'https://www.haodf.com/wenda/fingerprints_g_6403406888.htm'

        # temp_url = result[0]
        print(temp_url)
        # TODO 这里尽量传递一个url对应的编号，建立外键
        split_page('1', temp_url)
        break


if __name__ == '__main__':
    main()
    driver.close()
    # select_conn.closeMysql()
