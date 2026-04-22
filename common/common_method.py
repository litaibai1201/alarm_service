# -*- coding: utf-8 -*-
"""
@文件: common_method.py
@說明: API響應方法
@時間: 2023/10/19 14:15:34
@作者: LiDong
"""
from configs.const_conf import ENV
from configs.constant import conf


def response_result(content={}, msg="OK", code="S10000"):
    """"""
    rsp_dict = {}
    rsp_dict["code"] = code
    rsp_dict["msg"] = msg
    rsp_dict["content"] = content
    return rsp_dict


def fail_response_result(content={}, msg="Error", code="F10001"):
    """"""
    rsp_dict = {}
    rsp_dict["code"] = code
    remind_msg = f"，詳情請參考：http://{conf['host'][ENV]}:17650/static/files/alarm_server服務指導文檔.pdf"
    rsp_dict["msg"] = msg + remind_msg
    rsp_dict["content"] = content
    return rsp_dict
