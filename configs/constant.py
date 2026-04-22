# -*- coding: utf-8 -*-
"""
@文件: constant.py
@說明: 常量配置
@時間: 2023/10/19 19:03:05
@作者: LiDong
"""


conf = {
    "mail_conf": {
        "sysid": "IMSA",
        "m_from": "系統郵件",
        "wsdl_zheng": "http://eip109.ezdtco.com/wfswebs/Sysdatafunc.asmx?WSDL",
        "wsdl_peng": "http://eip03.ezdtco.com/wfswebs/Sysdatafunc.asmx?WSDL",
    },
    "single_conf": {
        "url": "http://10.182.179.113:8080/v1.0/robot/oToMessages/batchSend"
    },
    "host": {
        "prd": "10.126.1.237",
        "qas": "10.126.1.128",
    },
    "unsuccessful_files": "./unsuccessful_files",
    "check_user_url": "http://10.126.1.237:13570/api/searchData",
    "ldap_url": "http://10.126.1.237:13570/api/ldaplogin",
    "location_list": [
        "鹏鼎园区",
        "礼鼎园区",
        "大园园区",
        "先丰园区",
        "印度园区",
        "鵬鼎園區",
        "禮鼎園區",
        "大園園區",
        "先豐園區",
        "印度園區",
    ],
    "service_name": "alarm-server",
    "robot_conf": {
        "prd": {
            "robotCode": "dingehbonwxljmgqis4i",
            "app_key": "dingehbonwxljmgqis4i",
            "app_secret": "FTKMihQkcAniUQtIivRzI19a8jkpxccNTC7RVACehGkHqSp09Kop9AjOwpi2FxB4",
        },
        "qas": {
            "robotCode": "dingimkv2nskndtvlipl",
            "app_key": "dingimkv2nskndtvlipl",
            "app_secret": "kXwxWT0QMFFX4eW1vXnDhWQxo8077HPjwRrUVMOX4KYgnIYK2-Nxd267OANW6gvN",
        },
    },
}
