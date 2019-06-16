#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/10 18:54
# @FileName: advisory_page_down.py
# @Function: 根据输入的起止时间，下载该时段内好大夫医患对话详情页，可自定义全局常量 2018-09-12 0234（断点续爬）

import datetime
import os
import time

import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 定义抓取数据的url，时间跨度及存储路径等初始值
BASE_URL = 'https://www.haodf.com/sitemap-zx/'
DATE_START = '20080222'
DATE_END = '20080223'
DIR_PATH = './'
TIME_WAIT = 30
TIME_SLEEP = 2
# log 编码方式
ENCODING_STYLE = 'gb18030'
# status
# 断点发生日，默认为爬虫起始页
CURRENT_DATE = DATE_START
# 断点发生时正在爬取的日期页为第几页，默认为1
CURRENT_PAGE = 1
# 断点发生时 list 下标 current_index 正好等于已成功爬取的条数，默认为0
current_index = 0

# chrome 无窗模式
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)

# 显式等待
wait = WebDriverWait(browser, TIME_WAIT)


def down_detail_page(file_path, local_time):
    """
    构造日期循环，调用creat_date_page_url函数，下载医患对话详情页到本地
    :param file_path:
    :param local_time:
    :return: 
    """
    # 抓取网页的起止时间的字符串型时间格式化为日期型
    advisory_date = datetime.datetime.strptime(DATE_START, '%Y%m%d')
    # 断点发生日
    current_date = datetime.datetime.strptime(CURRENT_DATE, '%Y%m%d')
    advisory_date_end = datetime.datetime.strptime(DATE_END, '%Y%m%d')
    # 是否断点续爬
    if advisory_date < current_date:
        advisory_date = current_date
    # else:
        # print('从初始日期 DATE_START 开始爬取。')
    # 获取断点页页码，首次爬取页面数一般是 CURRENT_PAGE，这里为了防止输入页码小于1
    current_page = max(CURRENT_PAGE, 1)
    # 遍历待抓取网页起止时间区间
    while advisory_date <= advisory_date_end:
        # 下面调用函数生成全部每日所有页面的  URL ，解析出医患对话详情页的 URL
        # 该函数内部调用获取详情页源码的函数 get_detail_page
        # =====================
        # 首先考虑生成时间戳，然后取前后两次的差，如果差小于某个值，说明可能存在拒绝访问、
        # 网速差或其他未知错误，抓取页面不正常，但程序仍在无效运行，可能出现在抓取日期页过程中
        # =====================
        start_time = time.perf_counter()
        print(advisory_date)
        # 调用函数生成某一天的每一页页面 url，然后解析获取该页面中的 title 和 url
        # creat_date_page_url(advisory_date, file_path, local_time, current_page)
        # 后面的每一天都从第一页开始爬取
        current_page = 1
        # 输出浮点型数据
        delta_time = time.perf_counter() - start_time
        # 这里设置完成某天抓取小于多少时间或大于多少时间意义不大，可以将时差打印出来，人工来判断手工终止程序
        # 暂时不清楚 browser.get()会不会触发异常
        # 以下本来在一行，delta_time 有 warning
        print(advisory_date.strftime('%Y-%m-%d'), ' 日的页面用时  ', end='')
        print(delta_time, end='')
        print('  秒解析并抓取完毕')
        # 日期推进一天，联系下文不用加 time.sleep
        advisory_date += datetime.timedelta(days=1)
    else:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), ' 程序顺利运行结束!')


def creat_date_page_url(advisory_date, file_path, local_time, current_page):
    """
    根据传入的日期参数，生成该日所有页面的 URL
    然后解析该页面获取医患对话详情页 URL，然后调用 get_detail_page 保存详情页
    :param current_page:
    :param local_time:
    :param file_path:
    :param advisory_date:
    :return:
    """
    for date_page in range(current_page, 1000):
        date_page_url = BASE_URL + advisory_date.strftime('%Y%m%d') + '_' + str(date_page) + '/'
        # 打印状态
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), ' 开始尝试抓取 ', advisory_date.strftime('%Y-%m-%d'),
              ' 日第 ', str(date_page), ' 页问诊记录')
        try:
            # 获取含 title 和 detail page url的页面
            browser.get(date_page_url)
            # 等页面加载成功直到时间超过 TIME_WAIT
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="map_all"]')))
            # 查找页面class name为'hh'的节点。这里也可以用 try except 做
            # 判断如果有 hh 存在，对话详情页 title 和 url 一定存在，至少为1个
            browser.find_element_by_xpath('//li[@class="hh"]')
            # 和 html.xpath 获取 text()不同。用 elements
            item = browser.find_elements_by_xpath('//li/a')
            # 取详情页数量
            len_item = len(item)
            # 将 item 的属性值即 title 和 url 存入二维数组中，调用函数creat_arr_title_url（）
            arr_title_url = creat_arr_title_url(item, len_item)
            # 生成最后网页文件名称前缀
            pre_file_name = advisory_date.strftime('%Y%m%d') + '_' + str(date_page) + '_'
            # 判断是否从某页非第一条 url 开始爬取，并通过修改全局变量确保只执行一次
            global current_index
            start_index = 0
            if current_index:
                start_index = current_index
                current_index = 0
            for i in range(start_index, len_item):
                # 打印状态
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), advisory_date.strftime('%Y-%m-%d'),
                      ' 日第 ', str(date_page), ' 页问诊列表共有 ', str(len_item), ' 条问诊页地址，正在抓取第 ', str(i+1), ' 条')
                # 记录所有成功加载的某日某页面中所有的 title 和 url，包含可能将没有成功保存至本地的
                record_title_url_filename = 'TitleandUrl' + DATE_START + DATE_END + local_time
                with open(file_path + 'log/' + record_title_url_filename + '.txt', 'a', encoding=ENCODING_STYLE) \
                        as record_title_url:
                    record_title_url.write(arr_title_url[i][0] + '\t' + arr_title_url[i][1] + '\n')
                # 调用函数获取某一日某一页上所有医患对话详情页 URL 对应的页面并存入本地
                get_detail_page(arr_title_url[i][0], pre_file_name, file_path, local_time)
                # 记录成功爬取的最后一个 url 的状态，断点时正在爬取的为这里的下一条
                # 可能存在已经成功爬取当前 url 问诊记录的前几页然后异常中断
                current_status_filename = 'CurrentStatus' + DATE_START + DATE_END + local_time
                current_status_content = advisory_date.strftime('%Y-%m-%d') + ' 日第 ' + str(date_page) + \
                                         ' 页问诊列表共有 ' + str(len_item) + ' 条问诊页地址，已成功抓取 ' + str(i+1) + ' 条'
                with open(file_path + 'log/' + current_status_filename + '.txt', 'w', encoding=ENCODING_STYLE) \
                        as current_status:
                    current_status.write(current_status_content)
            # 记录含有 医患对话 title 和 url的 date_page_url
            normal_date_page_url = 'NormalDatePageUrl' + DATE_START + DATE_END + local_time
            with open(file_path + 'log/' + normal_date_page_url + '.txt', 'a', encoding=ENCODING_STYLE) \
                    as normal_date_page:
                normal_date_page.write(date_page_url + '\n')
            time.sleep(TIME_SLEEP)
        except NoSuchElementException:
            # 记录该日无记录（首页无 title，url）或该日有记录的最后一页的后一页的 url
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), advisory_date.strftime('%Y-%m-%d'),
                  ' 日只有 ', str(date_page-1), ' 页问诊列表，全部抓取完毕')
            empty_date_page_url = 'EmptyDatePageUrl' + DATE_START + DATE_END + local_time
            with open(file_path + 'log/' + empty_date_page_url + '.txt', 'a', encoding=ENCODING_STYLE) \
                    as empty_date_page:
                empty_date_page.write(date_page_url + '\n')
            # 防止频繁访问
            time.sleep(TIME_SLEEP)
            # 遇到某日某页没有 title 和 url，即空白，结束页码循环，等待开始下一日
            break
        except TimeoutException:
            # 考虑 IP 被封
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), date_page_url, ' 加载失败，请检查网络质量，IP！')
            # 打印 date_page_url 没有加载成功的情况，记录 url
            record_bug_date_page_url = 'BugDatePageUrl' + DATE_START + DATE_END + local_time
            with open(file_path + 'log/' + record_bug_date_page_url + '.txt', 'a', encoding=ENCODING_STYLE) \
                    as record_bug_date_page:
                record_bug_date_page.write(date_page_url + '\n')
            # 结束循环，开始请求下一日的第一页
            break


def creat_arr_title_url(item, len_item):
    """
    解析出当前页中的所有 title 和 url，并存入二维数组
    :param item:
    :param len_item:
    :return: arr_title_url
    """
    # 数组初始化，行数为节点的个数，j 为临时变量
    arr_title_url = [[] for j in range(len_item)]
    for i in range(len_item):
        arr_title_url[i].append(item[i].get_attribute('href'))
        arr_title_url[i].append(item[i].text)
    return arr_title_url


def get_detail_page(detail_page_url, pre_file_name, file_path, local_time):
    """
    获取某一页中所有 title 和 url对应的医患对话详情页，并保存到本地
    :param detail_page_url:
    :param pre_file_name:
    :param file_path:
    :param local_time:
    :return:
    """
    try:
        # 注意 href 值的'//'问题，暂未处理
        browser.get(detail_page_url)
        # 等待所有节点加载出来
        wait.until(EC.presence_of_all_elements_located)
        # 保存网页源码为 HTML 文件到本地，注意编码问题
        source_code = browser.page_source
        # HTML 命名形如20180322_1_xxx.htm,以下用切片的方法获取没有'/'的部分，不然会被认为是路径
        # 切片也可以用 detail_page_url.split('/')[-1]
        # file_name = pre_file_name + detail_page_url.split('/')[-1]
        file_name = pre_file_name + detail_page_url[28:] + '.txt'
        # 命名 记录所有成功保存至本地的网页的名称 的文本
        record_filename_name = 'NameofSavedPages' + DATE_START + DATE_END + local_time
        # 保存网页源码到本地， file_name 自带'.htm' 后缀，采用和网页相同的 gbk 编码
        with open(file_path + file_name, 'w', encoding=ENCODING_STYLE) as file:
            file.write(source_code)
        # 保存成功下载的网页的名称到'NameofSavedPages'(根目录)文件中，这里暂时不加对应 title
        with open(file_path + 'log/' + record_filename_name + '.txt', 'a', encoding=ENCODING_STYLE) as record_filename:
            record_filename.write(file_name + '\n')
        # 抓取每个页面后等候一下，防止过快被屏蔽或出现 5k 文件
        time.sleep(TIME_SLEEP)
        # 判断该页是否有后续页（翻页）
        detail_pages_amount = re.search('<div class="mt50">.*?\D*?(\d+)\D*?页', source_code, re.S)
        if detail_pages_amount:
            for i in range(2, int(detail_pages_amount.group(1)) + 1):
                print('当前问诊记录共有 ', detail_pages_amount.group(1), ' 页，', '正在爬取第 ', str(i), ' 页！')
                detail_page_more_url = detail_page_url[:-4] + '_p_' + str(i) + '.htm'
                get_detail_page_more(detail_page_more_url, pre_file_name, file_path, local_time)
        # else:
        # print(detail_page_url, '没有后续页！')
    except Exception:
        print(detail_page_url, ' 未抓取成功!')
        # 为记录没有成功保存的 HTML 的 URL 的 TXT 文件命名
        record_errfilename_name = 'NameofUnsavedPages' + DATE_START + DATE_END + local_time
        with open(file_path + 'log/' + record_errfilename_name + '.txt', 'a', encoding=ENCODING_STYLE) \
                as record_errfilename:
            record_errfilename.write(pre_file_name + '_' + detail_page_url + '\n')
        time.sleep(TIME_SLEEP)


def get_detail_page_more(detail_page_url, pre_file_name, file_path, local_time):
    """
    如果某个对话有多个页面，这里负责爬取后续页
    :param detail_page_url:
    :param pre_file_name:
    :param file_path:
    :param local_time:
    :return:
    """
    try:
        browser.get(detail_page_url)
        wait.until(EC.presence_of_all_elements_located)
        source_code = browser.page_source
        file_name = pre_file_name + detail_page_url[28:] + '.txt'
        record_filename_name = 'NameofSavedPages' + DATE_START + DATE_END + local_time
        with open(file_path + file_name, 'w', encoding=ENCODING_STYLE) as file:
            file.write(source_code)
        with open(file_path + 'log/' + record_filename_name + '.txt', 'a', encoding=ENCODING_STYLE) as record_filename:
            record_filename.write(file_name + '\n')
        time.sleep(TIME_SLEEP)
    except Exception:
        print(detail_page_url, ' 未抓取成功!')
        record_errfilename_name = 'NameofUnsavedPages' + DATE_START + DATE_END + local_time
        with open(file_path + 'log/' + record_errfilename_name + '.txt', 'a', encoding=ENCODING_STYLE) \
                as record_errfilename:
            record_errfilename.write(pre_file_name + '_' + detail_page_url + '\n')
        time.sleep(TIME_SLEEP)


def make_dir():
    """
    生成以网页起止时间命名的文件夹，并返回路径 file_path
    :return: file_path
    """
    # 定义存储 HTML 文件的路径为初始路径下起止时间命名的文件夹
    file_path = DIR_PATH + DATE_START + '_' + DATE_END + '/'
    # 生成 TXT 日志存储路径
    log_path = file_path + 'log/'
    exists = os.path.exists(log_path)
    if not exists:
        os.makedirs(log_path)
        # 返回两个参数麻烦
        return file_path
    else:
        return file_path


def main():
    """
    生成file_path 和local_time 供整个程序使用
    :return:
    """
    # 考虑 try 一个对常量的检查，如 DATE_START 一定在 DATE_ENG 前面
    local_time = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    # 可以考虑给文件夹名称也接一个 local_time 标识
    # ========================================================
    # 当前路径设置要求，如果程序因异常终止，需要人工删除系列 log 文件
    # ========================================================
    file_path = make_dir()
    try:
        # 下载医患对话的详情页
        down_detail_page(file_path, local_time)
        print('🍺🍺🍺🍺🍺🍺🍺🍺🍺🍺  从 ', DATE_START, ' 到 ', DATE_END, ' 期间的网页已全部存入 ', file_path)
    except Exception:
        print('😰😰😰😰😰😰😰😰😰😰  从 ', DATE_START, ' 到 ', DATE_END, ' 期间的网页获取失败!')
    browser.close()


if __name__ == '__main__':
    main()
