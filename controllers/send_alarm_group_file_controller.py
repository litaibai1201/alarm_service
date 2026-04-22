import json
import os
from datetime import datetime, timedelta

import requests
from flask import current_app as app

from common.send_alarm_file import SendAlarmFile
from common.send_dingplus import get_access_token
from configs.const_conf import ENV
from configs.constant import conf
from models.alarm_models import OperAlarmRecorModel


class SendAlarmFileController:
    def __init__(self, ip, payload) -> None:
        self.saf = SendAlarmFile()
        self.ip = ip
        self.payload = payload
        self.oper_alarm = OperAlarmRecorModel()
        self.robot_conf = conf["robot_conf"][ENV]
        self.url = "http://10.182.179.113:8080/v1.0/robot/groupMessages/send"
        self.headers = {
            "Content-Type": "application/json",
            "x-acs-dingtalk-access-token": app.config["TOKEN"],
        }

    def __search_data_file(self, hashed_string):
        filter_list = self.oper_alarm.search_data(
            self.ip,
            "group",
            hashed_string,
            self.payload.get("groupid"),
            self.payload.get("type"),
            None,
            datetime.now() - timedelta(minutes=self.payload.get("same_alarm_inter")),
        )
        return filter_list

    def __format_datadict(self):
        data_dict = dict()
        data_dict["ip"] = self.ip
        data_dict["method_to_inform"] = "group"
        data_dict["service_name"] = self.payload.get("service_name")
        data_dict["webhook"] = self.payload.get("groupid")
        data_dict["type"] = self.payload.get("type")
        return data_dict

    def __format_data(self, file_path, result):
        data = {
            "robotCode": self.robot_conf["robotCode"],
            "openConversationId": self.payload.get("groupid"),
            "msgKey": "sampleImageMsg",
        }
        if self.payload.get("type") == "image":
            data["msgParam"] = json.dumps({"photoURL": result})
        else:
            file_name = os.path.basename(file_path)
            data["msgKey"] = "sampleFile"
            data["msgParam"] = json.dumps(
                {
                    "mediaId": result,
                    "fileName": file_name,
                    "fileType": file_name.split(".")[-1],
                }
            )
        return data

    def send_file(self, file):
        send_type = self.payload["type"]
        file_data = file.stream.read()
        file_path = f"./static/{send_type}s/" + file.filename
        if not self.saf.receive_convert_archive_file(file_path, file_data):
            return {"err_msg": "文件流創建失敗"}
        hashed_string = self.saf.get_encode_string(file_data)
        filter_list = self.__search_data_file(hashed_string)
        if not filter_list:
            data_dict = self.__format_datadict()
            result = self.saf.send_req_get_upload_media(file_path, send_type)
            if not result.startswith("@"):
                return {"err_msg": result}
            data = self.__format_data(file_path, result)
            data_dict["content"] = hashed_string
            rsp_msg = self.saf.send_request_get_remark(
                data, data_dict, file_path, file_data
            )
            data_dict["at_user"] = None
            if self.oper_alarm.add_data_to_db(data_dict):
                return rsp_msg
            else:
                return {"err_msg": f"{data_dict}: 數據插入數據庫失敗"}
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }

    def __build_content_on_type(self):
        type = self.payload.get("type")
        if type == "text":
            text = json.loads(self.payload.get("text"))
            content = text.get("content")
        elif type == "markdown":
            markdown = json.loads(self.payload["markdown"])
            content = json.dumps(
                {"title": markdown["title"], "text": markdown["text"]},
                ensure_ascii=False,
            )
        elif type == "link":
            link = json.loads(self.payload["link"])
            content = json.dumps(
                {
                    "title": link["title"],
                    "text": link["text"],
                    "messageUrl": link["url"],
                },
                ensure_ascii=False,
            )
        return content

    def __search_data(self, content):
        filter_list = self.oper_alarm.search_data(
            self.ip,
            "group",
            content,
            self.payload.get("groupid"),
            self.payload.get("type"),
            None,
            datetime.now() - timedelta(minutes=self.payload.get("same_alarm_inter")),
        )
        return filter_list

    def __send_request_get_remark(self, data, data_dict):
        url = self.url
        res = requests.post(url, headers=self.headers, json=data, timeout=10).json()
        msg = res.get("message")
        if msg == "不合法的access_token":
            app.config["TOKEN"] = get_access_token()
            self.headers["x-acs-dingtalk-access-token"] = app.config["TOKEN"]
            res = requests.post(url, headers=self.headers, json=data, timeout=10).json()
        if res.get("message"):
            data_dict["status"] = 2
            rsp_msg = res.get("message")
        else:
            rep_query = res.get("processQueryKey")
            rsp_msg = {"status": "ok", "processQueryKey": rep_query}
        data_dict["remark"] = json.dumps(rsp_msg, ensure_ascii=False)
        return rsp_msg

    def send_text(self):
        content = self.__build_content_on_type()
        filter_list = self.__search_data(content)
        if not filter_list:
            data = {
                "robotCode": self.robot_conf["robotCode"],
                "openConversationId": self.payload.get("groupid"),
                "msgKey": "sampleText",
                "msgParam": json.dumps({"content": content}, ensure_ascii=False),
            }
            data_dict = self.__format_datadict()
            data_dict["content"] = content
            rsp_msg = self.__send_request_get_remark(data, data_dict)
            self.oper_alarm.add_data_to_db(data_dict)
            return rsp_msg
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }

    def send_markdown(self):
        content = self.__build_content_on_type()
        filter_list = self.__search_data(content)
        if not filter_list:
            data = {
                "robotCode": self.robot_conf["robotCode"],
                "openConversationId": self.payload.get("groupid"),
                "msgKey": "sampleMarkdown",
                "msgParam": content,
            }
            data_dict = self.__format_datadict()
            data_dict["content"] = content
            rsp_msg = self.__send_request_get_remark(data, data_dict)
            if self.oper_alarm.add_data_to_db(data_dict):
                return rsp_msg
            else:
                return {"err_msg": f"{data_dict}: 數據插入數據庫失敗"}
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }

    def send_link(self):
        content = self.__build_content_on_type()
        filter_list = self.__search_data(content)
        if not filter_list:
            data = {
                "robotCode": self.robot_conf["robotCode"],
                "openConversationId": self.payload.get("groupid"),
                "msgKey": "sampleLink",
                "msgParam": content,
            }
            data_dict = self.__format_datadict()
            data_dict["content"] = content
            rsp_msg = self.__send_request_get_remark(data, data_dict)
            if self.oper_alarm.add_data_to_db(data_dict):
                return rsp_msg
            else:
                return {"err_msg": f"{data_dict}: 數據插入數據庫失敗"}
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }
