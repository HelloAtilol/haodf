# -*- coding: utf-8 -*-
"""
# @Time    : 2019/7/12 17:52
# @Author  : 王诚坤
# @File    : Logger
# @des     : log管理
"""

import logging
import os
import time


class Logger(object):
    def __init__(self, logger):
        """
        指定保存日志的文件路径，日志级别，调用文件
        将日志存入到指定的文件中
        :param logger:
        """

        # 创建一个logger(记录器)
        # 日志记录的工作主要由Logger对象来完成。在调用getLogger时要提供Logger的名称
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        rq = time.strftime('%Y%m%d', time.localtime(time.time()))
        log_path = os.path.dirname(os.getcwd()) + '/logs/'
        log_name = log_path + rq + '.log'  # 文件名

        # 将日志写入磁盘
        fh = logging.FileHandler(log_name)
        fh.setLevel(logging.INFO)

        # 创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def getLog(self):
        return self.logger
