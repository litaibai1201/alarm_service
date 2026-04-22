# -*- coding: utf-8 -*-
"""
@文件: common_tools.py
@說明: 公共方法模塊
@時間: 2023/10/19 14:14:33
@作者: LiDong
"""
import datetime

import requests

from configs.constant import conf


def get_now(data=None, days=0):
    """
    獲取時間字符
    """

    now_time = datetime.datetime.now() + datetime.timedelta(days=days)
    if data == "date":
        return now_time.strftime("%Y-%m-%d")
    elif data == "time":
        return now_time.strftime("%H:%M:%S")
    elif data == "datetime":
        return now_time
    elif data == "datetime_nums":
        return now_time.strftime("%Y%m%d%H%M%S")
    elif data == "date_nums":
        return now_time.strftime("%Y%m%d")
    else:
        return now_time.strftime("%Y-%m-%d %H:%M:%S")


def define_exist(atuserids):
    for at_id in atuserids:
        res = requests.get(conf.get("check_user_url"), params={"workno": at_id}).json()
        if not res.get("content"):
            content = {"err_msg": f"{at_id}，此工號不存在!"}
            return content
    return {}
