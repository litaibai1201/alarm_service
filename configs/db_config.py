# -*- coding: utf-8 -*-
"""
@文件: db_config.py
@說明: db配置
@時間: 2023/10/19 19:03:19
@作者: LiDong
"""


from configs import secrets

db_account = secrets.db_account
db_config_dict = {
    "alarm_server_db": {
        "host": "10.182.190.176",
        "port": "3306",
        "prd": {
            "database_name": "alarm_server_db",
        },
        "qas": {
            "database_name": "alarm_server_db_dev",
        },
        "username": db_account["alarm_db"]["username"],
        "password": db_account["alarm_db"]["password"],
    },
}
