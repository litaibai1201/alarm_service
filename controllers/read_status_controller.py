import requests
from flask import current_app as app

from common.send_dingplus import get_access_token
from configs.const_conf import ENV
from configs.constant import conf


class ReadStatusController:
    def __init__(self, payload):
        self.robot_conf = conf["robot_conf"][ENV]
        self.payload = payload

    def read_status_single(
        self,
    ):
        url = "http://10.182.179.113:8080/v1.0/robot/oToMessages/readStatus"
        headers = {"x-acs-dingtalk-access-token": app.config["TOKEN"]}
        data = {
            "robotCode": self.robot_conf["robotCode"],
            "processQueryKey": self.payload["single"]["processQueryKey"],
        }
        res = requests.get(url, headers=headers, params=data).json()
        msg = res.get("message")
        if msg == "不合法的access_token":
            app.config["TOKEN"] = get_access_token()
            headers["x-acs-dingtalk-access-token"] = app.config["TOKEN"]
            res = requests.get(url, headers=headers, params=data).json()
        return res

    def read_status_group(self):
        url = "http://10.182.179.113:8080/v1.0/robot/groupMessages/query"
        headers = {
            "x-acs-dingtalk-access-token": app.config["TOKEN"],
            "Content-Type": "application/json",
        }
        data = {
            "openConversationId": self.payload["group"]["groupid"],
            "robotCode": self.robot_conf["robotCode"],
            "processQueryKey": self.payload["group"]["processQueryKey"],
            "maxResults": 50,
            "nextToken": "",
        }
        res = requests.post(url, headers=headers, json=data).json()
        msg = res.get("message")
        if msg == "不合法的access_token":
            app.config["TOKEN"] = get_access_token()
            headers["x-acs-dingtalk-access-token"] = app.config["TOKEN"]
            res = requests.post(url, headers=headers, json=data).json()
        return res
