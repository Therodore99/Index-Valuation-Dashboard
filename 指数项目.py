from iFinDPy import *
from datetime import datetime
import pandas as pd
import time as _time
import json
from threading import Thread,Lock,Semaphore
import requests

sem = Semaphore(5)  # 此变量用于控制最大并发数

# 登录函数
def thslogindemo():
    # 输入用户的帐号和密码
    thsLogin = THS_iFinDLogin("hazqzb008","wy990801")
    print(thsLogin)
    if thsLogin in {0, -201}:
        print('登录成功')
    else:
        print('登录失败')

def datepool_basicdata_demo():
    # 通过专题报表函数的板块成分报表和基础数据函数，提取全部A股在2025-05-14日的日不复权收盘价
    print(THS_HQ('000001.SZ','preClose','','2025-01-30','2026-01-30'))
   

def main():
    # 本脚本为数据接口通用场景的实例,可以通过取消注释下列示例函数来观察效果

    # 登录函数
    thslogindemo()
    # 通过专题报表的板块成分函数和基础数据函数，提取全部A股的全部股票在2025-05-14日的日不复权收盘价
    #datepool_basicdata_demo()
    #通过专题报表的板块成分函数和实时行情函数，提取上证50的全部股票的最新价数据,并将其导出为csv文件
    # datapool_realtime_demo()
    # 演示如何通过不消耗流量的自然语言语句调用常用数据
    # iwencai_demo()
    # 本函数为通过高频序列函数,演示如何使用多线程加速数据提取的示例,本例中通过将所有A股分100组,最大线程数量sem进行提取
    # multiThread_demo()
    # 本函数演示如何使用公告函数提取满足条件的公告，并下载其pdf
    # reportDownload()

if __name__ == '__main__':
    main()