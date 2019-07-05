# -*- coding: utf-8 -*-
"""
# @Time    : 2019/7/4 17:46
# @Author  : 王诚坤
# @File    : study.py
# @des     :
"""
import threading
import time

# 定义一个全局变量
g_num = 0


def test1(num):
    global g_num

    for i in range(num):
        mutex.acquire()  # 上锁 注意了此时锁的代码越少越好
        g_num += 1
        mutex.release()  # 解锁

    print("-----in test1 g_num=%d----" % g_num)


def test2(num):
    global g_num
    for i in range(num):
        mutex.acquire()  # 上锁
        g_num += 1
        mutex.release()  # 解锁
    print("-----in test2 g_num=%d----" % g_num)


# 创建一个互斥锁，默认是没有上锁的
mutex = threading.Lock()


def main():
    t1 = threading.Thread(target=test1, args=(1000000,))
    t2 = threading.Thread(target=test2, args=(1000000,))

    t1.start()
    t2.start()

    # 等待上面的2个线程执行完毕....
    time.sleep(2)

    print("-----in main Thread g_num = %d---" % g_num)


if __name__ == "__main__":
    main()
