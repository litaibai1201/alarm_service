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
    if not atuserids:
        return {}

    from concurrent.futures import ThreadPoolExecutor, as_completed

    url = conf.get("check_user_url")

    def check_one(at_id):
        try:
            res = requests.get(url, params={"workno": at_id}, timeout=5).json()
            if not res.get("content"):
                return at_id
        except requests.exceptions.RequestException:
            return at_id
        return None

    with ThreadPoolExecutor(max_workers=min(len(atuserids), 10)) as executor:
        futures = {executor.submit(check_one, at_id): at_id for at_id in atuserids}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                return {"err_msg": f"{result}，此工號不存在!"}
    return {}
