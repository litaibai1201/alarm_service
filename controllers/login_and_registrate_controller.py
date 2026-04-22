# -*- coding: utf-8 -*-
"""
@文件: login_controller.py
@說明:
@時間: 2023/12/08 16:20:29
@作者: LiDong
"""

import hashlib

import requests
from flask_jwt_extended import create_access_token

from configs.constant import conf
from models.registrate_model import OperRegistrationModel


class LoginController:
    def __init__(self, ip, payload):
        self.url = conf.get("ldap_url")
        self.headers = {"Content-Type": "application/json"}
        self.ip = ip
        self.payload = payload

    def login_ldap(self):
        res = requests.post(self.url, json=self.payload, headers=self.headers)
        return res.json()

    def get_token(self):
        user_info = self.payload.copy()
        user_info["ip"] = self.ip
        del user_info["password"], user_info["location"], user_info["service_name"]
        token = create_access_token(identity=user_info)
        return token


class RegistrateController:
    def __init__(self, payload) -> None:
        self.oper_rm = OperRegistrationModel()
        self.payload = payload

    def get_token(self):
        data = self.payload.get("service_name") + "&" + self.payload.get("service_type")
        token = hashlib.sha256(str(data).encode()).hexdigest()
        return token

    def add(self, data):
        return self.oper_rm.add_data_to_db(data)

    def search(self):
        return self.oper_rm.search_token(
            self.payload.get("service_name"), self.payload.get("service_type")
        )

    def get_datalist(self):
        return self.oper_rm.search_data(self.payload["work_no"])
