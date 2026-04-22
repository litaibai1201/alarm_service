# -*- coding: utf-8 -*-
"""
@文件: app_config.py
@說明: 增加 SQLALCHEMY_DATABASE_TEST_URI 的配置
@時間: 2023/10/27 08:36:31
@作者: LiaoHengYi
"""

from configs.const_conf import ENV
from configs.db_config import db_config_dict

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(
    db_config_dict["alarm_server_db"]["username"],
    db_config_dict["alarm_server_db"]["password"],
    db_config_dict["alarm_server_db"]["host"],
    db_config_dict["alarm_server_db"]["port"],
    db_config_dict["alarm_server_db"][ENV]["database_name"],
)

port = {"prd": 17651, "qas": 17650}
