# 好大夫的爬虫工具

## Dependence（Python 3.6）
- BeautifulSoup
- selenium
- time
- datetime
- random
- pyprind
- pymysql

## 数据存储方式
包括四个表：all_url, QA, doctor, relative_qa。具体结构如图所示；
![haodf](https://github.com/HelloAtilol/haodf/blob/master/source/haodf.jpg)

## 代码执行步骤
1. 配置`ConnectDatabase.py`中的数据库参数，与数据库建立链接；
2. 执行`getHaodf.py`，获取所有的URL，可以通过设置日期获取；
```python
# 爬取文件开始日期
CURRENT_DATE = "20180714"
# 爬取文件结束日期
END_DATE = "20181231"
```
3. 获取每个URL的信息，好大夫的数据结构有很多种，目前发现了两种：`{"class": "zzx_yh_stream"}`和`{"class": "f-card clearfix js-f-card"}`，如果出现新的数据结构，需要重新编写。

```python
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
```
4. 执行`getContent.py`。

## 更新信息
### 2019.06.21
- 为读取页面URL添加了进度条；
- 进行了1000个页面的测试；

### 2019.07.05
- 增加了多线程访问；
- 优化了代码结构；
- 增加了解析失败url的保存文档；
- 对已知大部分的url解析可能更新了状态；

### 209.07.12
- 增加了日志文件；
- 修复了部分数据存入数据库失败的BUG；
- 整合了存储部分的代码，减少数据库操作；