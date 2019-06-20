# -*- coding: utf-8 -*-
"""
# @Time    : 2019/6/16 18:34
# @Author  : 王诚坤
# @File    : getContent.py
# @des     :解析页面
"""

from tools import ConnectDatabase as conn
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import random

# 连接数据库
select_conn = conn.MySQLCommand()
select_conn.connectMysql(table="all_url")
update_conn = conn.MySQLCommand()

driver = webdriver.Chrome()


def split_relative(qa_number, relative_soups):
    """
    负责解析相关问答、文章和疾病
    :param qa_number: 访问页面对应的编号
    :param relative_soups: 需要解析的Beautifulsoup对象
    :return: None
    """
    # 更换数据存储的表名
    update_conn.connectMysql(table="relative_url")

    for relative_soup in relative_soups:
        # print(relative_soup)
        r_text = relative_soup.p.find("span", {"class": "fl f18"}).text
        # 相关标签，0代表问答；1代表文章；2代表疾病
        if "相关回复" in r_text:
            tag = '0'
        elif "相关文章" in r_text:
            tag = '1'
        elif "相关疾病" in r_text:
            tag = '2'
        rq_lis = relative_soup.find_all("li")
        for rq_li in rq_lis:
            result = {"rela_tag": tag, "rela_title": rq_li.a.string, "rela_url": rq_li.a["href"][2:],
                      "qa_number": qa_number}
            update_conn.insertData(data_dict=result, primary_key="rela_url")


def split_content_1(qa_number, qa_list, qa_soups):
    """
    解析第一种内容的第一条，class=“zzx_yh_stream”
    :param qa_list:  问答的标签
    :param qa_number: url编号
    :param qa_soups: 问答的Beautifulsoup对象
    :return: qa_list 在一个问答中发言的编号
    """
    # 更换数据存储的表名
    update_conn.connectMysql(table="QA")

    # 取出第一个提问
    first_describe = qa_soups[0]
    # 患者状态和咨询时间
    user_soup = first_describe.find("div", {"class": "stream_yh_left"})
    # 状态
    patient_status = user_soup.find("div", {"class": "yh_l_states"}).span.string
    # 发表时间
    qa_time = user_soup.find("div", {"class": "yh_l_times"}).string
    # qa_author: 0是患者，1是医生
    first_result = {"qa_number": qa_number, "qa_list": qa_list, "qa_author": '0', "patient_status": patient_status, "qa_time": qa_time}

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
    # 表QA无主键，主键为QA编号
    update_conn.insertData(first_result, primary_key="")
    qa_list += 1
    qa_soups.remove(first_describe)

    # qa_list 在一个问答中发言的编号
    return split_soups_1(qa_number, qa_list, qa_soups)


def split_soups_1(qa_number, qa_list, qa_soups):
    """
    解析第一种内容的后续内容class=“zzx_yh_stream”
    :param qa_number: url的编号
    :param qa_list: 内容在问答种的编号
    :param qa_soups: 需要解析的soup的list
    :return: qa_list 在一个问答中发言的编号
    """
    # 更换数据存储的表名
    update_conn.connectMysql(table="QA")

    for qa_soup in qa_soups:
        # 时间
        qa_time = qa_soup.find("div", {"class": "yh_l_times"}).string
        # 结果字典初始化
        result = {"qa_number": qa_number, "qa_list": qa_list, "qa_time": qa_time, "qa_tag": ""}
        # 判断是医生发言还是患者发言
        if "yi" in qa_soup.find("div", {"class": "yh_r_t_icon"}).img["src"]:
            # 医生发言对应的处理过程
            qa_author = '1'
            result["qa_author"] = qa_author
            # 判断是否是语音
            try:
                content_soup = qa_soup.find("h3", {"class": "h_s_cons_title"})
                if content_soup is None:
                    content_soup = qa_soup.find("p", {"class": "h_s_cons_main mb10"})
                    if content_soup is not None:
                        result["qa_tag"] += qa_soup.find("h3", {"class": "h_s_docs_title mb10 ml10"}).text
                content = content_soup.text
            except AttributeError:
                # 语音的处理方法
                content_soup = qa_soup.find("div", {"class": "yy_vioce_box"})
                if content_soup is not None:
                    content = content_soup["src"][2:]
                else:
                    content = ""
                result["qa_tag"] += "语音"
            result["qa_content"] = content
        else:
            # 患者提问的解析办法
            qa_author = '0'
            result["qa_author"] = qa_author
            # 使用最多的结构
            content_soup = qa_soup.find("pre", {"class": "h_s_cons_main"})
            # 开药方请求
            if content_soup is None:
                content_soup = qa_soup.find("h3", {"class": "h_s_cons_title iconyaofang"})
            # 送礼物
            if content_soup is None:
                content_soup = qa_soup.find("h3", {"class": "h_s_cons_title gifts"})
                if content_soup is not None:
                    result["qa_tag"] = "送礼物"
                    content_soup = qa_soup.find("p", {"class": "h_s_cons_main"})
            # 感谢信
            if content_soup is None:
                content_soup = qa_soup.find("h3", {"class": "h_s_cons_title iconmails"})
                if content_soup is not None:
                    result["qa_tag"] = content_soup.text
                    content_soup = qa_soup.find("p", {"class": "pt5 wb"}).span
            # 上传视频
            if content_soup is None:
                content_soup = qa_soup.find("span", {"class": "fl bingli_hide_word"})

            # 再次上传病历
            if content_soup is None:
                # 判断是不是有病例专有头部标签
                content_soup = qa_soup.find("div", {"class": "h_s_cons_info_top"})
                if content_soup is not None:
                    qa_list = split_content_1(qa_number, qa_list, [qa_soup])

            # 患者Tag
            if content_soup is None:
                content_soup = qa_soup.find("h3", {"class": "h_s_cons_title"})
                if content_soup is not None:
                    result["qa_tag"] = content_soup.text
                    content = ""
                    for p_soup in qa_soup.find("div", {"class": "h_s_cons"}).children:
                        if p_soup.name != "p":
                            continue
                        content += p_soup.text

            # 以上方式都未检测到，需要添加解析方式
            if content_soup is None:
                input("患者出现新的解析方式")
            if len(content) > 0:
                result["qa_content"] = content
            else:
                result["qa_content"] = content_soup.text

            # 患者状态
            patient_status = qa_soup.find("div", {"class": "yh_l_states"}).span.string
            result["patient_status"] = patient_status

        # 将数据保存到数据库
        update_conn.insertData(result, primary_key="")
        qa_list += 1

    # qa_list 在一个问答中发言的编号
    return qa_list


def split_content_2(qa_number, qa_list, qa_soups):
    """
    解析第二种内容的第一条，class=“f-card clearfix js-f-card”
    :param qa_list:  问答的标签
    :param qa_number: url编号
    :param qa_soups: 问答的Beautifulsoup对象
    :return: qa_list 在一个问答中发言的编号
    """
    # 更换数据存储的表名
    update_conn.connectMysql(table="QA")

    # 取出第一个提问内容
    first_describe = qa_soups[0]

    # 患者状态和咨询时间
    user_soup = first_describe.find("div", {"class": "f-c-left"})
    # 状态
    patient_status = user_soup.find("div", {"class": "f-c-l-status"}).span.string
    # 发表时间
    qa_time = user_soup.find("div", {"class": "f-c-l-date"}).string
    # qa_author: 0是患者，1是医生
    first_result = {"qa_number": qa_number, "qa_list": qa_list, "qa_author": '0',
                    "patient_status": patient_status, "qa_time": qa_time}

    # 咨询内容
    content = ""
    describe = first_describe.find("div", {"class": "f-c-r-wrap"})
    for child in describe.children:
        if child.name == "h4" or child.name == "p":
            content += (child.text+"\n")
    # 去掉最后一个\n
    first_result["qa_content"] = content[:-1]
    update_conn.insertData(first_result, primary_key="")
    qa_list += 1

    # 从list中去掉第一个
    qa_soups.remove(first_describe)

    # qa_list 在一个问答中发言的编号
    return split_soups_2(qa_number, qa_list, qa_soups)


def split_soups_2(qa_number, qa_list, qa_soups):
    """
    解析第一种内容的后续内容class=“f-card clearfix js-f-card”
    :param qa_number: url的编号
    :param qa_list: 内容在问答种的编号
    :param qa_soups: 需要解析的soup的list
    :return: qa_list 在一个问答中发言的编号
    """
    # 更换数据存储的表名
    update_conn.connectMysql(table="QA")

    for qa_soup in qa_soups:
        # 时间
        qa_time = qa_soup.find("div", {"class": "f-c-l-date"}).string
        # 结果字典初始化
        result = {"qa_number": qa_number, "qa_list": qa_list, "qa_time": qa_time, "qa_tag": ""}
        # 判断是医生还是患者
        if "doctor" in qa_soup.find("img", {"class": "f-c-r-usertype"})["src"]:
            # 医生的处理方式
            qa_author = '1'
            result["qa_author"] = qa_author
            qa_tag_soup = qa_soup.find("h2", {"class": "f-c-r-w-title"})
            # 添加标签(一问一答、图文问诊)
            if qa_tag_soup is not None:
                result["qa_tag"] += qa_tag_soup.text
            # 判断是不是语音
            try:
                content_soup = qa_soup.find("h4", {"class": "f-c-r-w-subtitle"})
                if content_soup is None:
                    content_soup = qa_soup.find("p", {"class": "f-c-r-doctext"})
                # 医生回答中出现了新的结构，需要手动更新
                if content_soup is None:
                    print(qa_soup.find("div", {"class": "f-c-r-wrap"}))
                    input("医生出现了新的解析方式，可能是语音，重新查看")
                content = content_soup.text.replace("\t", "").replace("\n", "").replace(" ", "")
            except AttributeError:
                # 这里暂时没有找到对应的语音，出现了语音，重新编写
                input("出现了语音！")
                content = qa_soup.find("div", {"class": "yy_vioce_box"})["src"][2:]
                result["qa_tag"] += "语音"
            result["qa_content"] = content
        else:
            # 患者的处理方式
            qa_author = '0'
            result["qa_author"] = qa_author
            content = qa_soup.find("p", {"class": "f-c-r-w-text"}).text
            result["qa_content"] = content.replace("\t", "").replace("\n", "").replace(" ", "")

            # 患者状态
            patient_status = qa_soup.find("div", {"class": "f-c-l-status"}).span.string
            result["patient_status"] = patient_status
        # 将数据保存到数据库
        update_conn.insertData(result, primary_key="")
        qa_list += 1
    # qa_list 在一个问答中发言的编号
    return qa_list


def change_split_type(split_type, qa_number, qa_list, qa_soups):
    """
    根据解析类型调用不同的解析方式
    :param split_type: 解析类型
    :param qa_number: url对应的编号
    :param qa_list: 对话顺序
    :param qa_soups: soup的list集合
    :return: qa_list 在一个问答中发言的编号
    """
    if split_type is 1:
        # 解析首页
        return split_content_1(qa_number, qa_list, qa_soups)
    elif split_type is 2:
        # 解析后续页面
        return split_soups_1(qa_number, qa_list, qa_soups)

    elif split_type is 3:
        return split_content_2(qa_number, qa_list, qa_soups)
    elif split_type is 4:
        return split_soups_2(qa_number, qa_list, qa_soups)
    else:
        raise IndexError("没有对应的解析方式。需要查看URL对应的解析方式。")


def split_page(qa_number, url):
    """
    根据url进行解析
    :param qa_number: url对应的数据库编号
    :param url: url
    :return: None
    """

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
    try:
        soup = BeautifulSoup(driver.page_source.encode('gbk'), "lxml")
    except UnicodeEncodeError:
        # 编码异常
        update_url["qa_status"] = '3'
        update_conn.connectMysql(table="all_url")
        update_conn.update_database(datadict=update_url, situation="WHERE qa_number = '%s'" % qa_number)
        return

    # 更新医生id
    doctor_id_soup = soup.find("span", {"class": "space_b_url"})
    update_url["qa_doctor"] = doctor_id_soup.string
    # 更新title
    title_soup = soup.find("h1", {"class": "fl f20 fn fyahei pl20 bdn"})
    if title_soup is None:
        title_soup = soup.find("div", {"class": "fl-title ellps"})
    # 判断页面是否存在
    try:
        update_url["qa_title"] = title_soup.string
    except AttributeError:
        # 2代表网页异常
        update_url["qa_status"] = '2'
        update_conn.connectMysql(table="all_url")
        update_conn.update_database(datadict=update_url, situation="WHERE qa_number = '%s'" % qa_number)
        return

    # 解析相关问答、文章、疾病
    relative_soups = soup.find_all("div", {"class": "mt20 w670 bg_w zzx_t_repeat"})
    split_relative(qa_number=qa_number, relative_soups=relative_soups)

    # 解析QA
    qa_list = 1
    # 默认第一种解析方式{"class": "zzx_yh_stream"}
    split_type = 1
    qa_content_soups = soup.find_all("div", {"class": "zzx_yh_stream"})

    # 第二种解析方式{"class": "f-card clearfix js-f-card"}
    if len(qa_content_soups) == 0:
        split_type = 3
        print("第二种解析方式")
        qa_content_soups = soup.find_all("div", {"class": "f-card clearfix js-f-card"})

    # 出现了新的网站结构。需要手动解析
    if len(qa_content_soups) == 0:
        split_type = 5
        input("未知解析方式！")

    qa_list = change_split_type(split_type, qa_number=qa_number, qa_list=qa_list, qa_soups=qa_content_soups)

    # 获取页数，如果有,做翻页处理。
    page_soup = soup.find("a", {'class': 'page_turn_a', 'rel': 'true'})
    if page_soup is not None:
        page_num = page_soup.text.split("\xa0")[1]
        for i in range(1, int(page_num)):
            driver.get(url.replace(".htm", "_p_%d.htm" % (i+1)))
            soup = BeautifulSoup(driver.page_source.encode('gbk'), "lxml")
            qa_content_soups = soup.find_all("div", {"class": "zzx_yh_stream"})
            qa_list = change_split_type(split_type+1, qa_number=qa_number, qa_list=qa_list, qa_soups=qa_content_soups)

    # 更改URL的status，0代表未解析，1代表已解析，其他代表异常，并更新到数据库
    update_url["qa_status"] = '1'
    update_conn.connectMysql(table="all_url")
    update_conn.update_database(datadict=update_url, situation="WHERE qa_number = '%s'" % qa_number)


def main():
    # 从数据库中读取未解析页面的URL
    title_list = ["qa_number", "qa_url"]
    situation = "WHERE qa_status = '0'"
    select_cursor = select_conn.select_order(title_list=title_list, situation=situation)
    while True:
        result = select_cursor.fetchone()
        if result is None:
            break
        qa_number, temp_url = result
        # 测试用的URL
        # 语音
        # temp_url = 'https://www.haodf.com/wenda/kongweimin_g_5974272953.htm'
        # 医生
        # temp_url = 'https://www.haodf.com/wenda/abc195366_g_5673322365.htm'
        # 团队， 第二种解析方式
        # temp_url = 'https://www.haodf.com/doctorteam/flow_team_6465190653.htm'
        # 分页 且 无相关ss,第一种解析方式
        # temp_url = 'https://www.haodf.com/wenda/fingerprints_g_6403406888.htm'
        # 送礼物
        # temp_url = "https://www.haodf.com/wenda/blueesky_g_5673307901.htm"

        # 如果之前爬取过该页面，删除相关信息
        delete_situation = "WHERE qa_number = '%s'" % (str(qa_number))
        update_conn.connectMysql(table="QA")
        update_conn.delete_data(situation=delete_situation)
        update_conn.connectMysql(table="relative_url")
        update_conn.delete_data(situation=delete_situation)

        if qa_number % 100 == 0:
            print("休息30s")
            time.sleep(10)

        print("---------------------------------------" * 3)
        print("\t第%s个URL正在解析.URL：%s" % (str(qa_number), temp_url))
        try:
            split_page(str(qa_number), temp_url)
        except AttributeError:
            continue
        except TypeError:
            continue
        print("---------------------------------------" * 3)
        # 设置睡眠时间，不然会出现被跳转的情况，目前无法try到那个异常
        time.sleep(random.randint(1, 3))


if __name__ == '__main__':
    main()
    driver.close()
    select_conn.closeMysql()
    update_conn.closeMysql()
