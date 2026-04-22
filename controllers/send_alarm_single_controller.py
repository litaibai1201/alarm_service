import json
import os
from datetime import datetime, timedelta

import requests
from flask import current_app as app

from common.send_alarm_file import SendAlarmSingleFile
from common.send_dingplus import get_access_token
from configs.const_conf import ENV
from configs.constant import conf
from models.alarm_models import OperAlarmRecorModel


class BaseSendAlarmSingle:
    def __init__(self, ip, payload) -> None:
        self.sasf = SendAlarmSingleFile()
        self.ip = ip
        self.headers = {
            "Content-Type": "application/json",
            "x-acs-dingtalk-access-token": app.config["TOKEN"],
        }
        self.oper_alarm = OperAlarmRecorModel()
        self.single_conf = conf.get("single_conf", {})
        self.robot_conf = conf["robot_conf"][ENV]
        self.payload = payload

    def format_datadict(self):
        data_dict = dict()
        data_dict["ip"] = self.ip
        data_dict["service_name"] = self.payload.get("service_name", "")
        data_dict["method_to_inform"] = "single"
        data_dict["type"] = self.payload.get("type")
        return data_dict

    def search_data(self, content):
        same_alarm_inter = self.payload.get("same_alarm_inter")
        filter_list = self.oper_alarm.search_data(
            self.ip,
            "single",
            content,
            None,
            self.payload.get("type"),
            ",".join(self.payload.get("userids")),
            datetime.now() - timedelta(minutes=same_alarm_inter),
        )
        return filter_list


class SendAlarmSingleMsgController(BaseSendAlarmSingle):
    def __init__(self, ip, payload) -> None:
        super().__init__(ip, payload)

    def __build_content_on_type(self, send_type):
        if send_type == "text":
            text = json.loads(self.payload.get("text"))
            content = text.get("content")
        elif send_type == "markdown":
            markdown = json.loads(self.payload["markdown"])
            content = json.dumps(
                {"title": markdown["title"], "text": markdown["text"]},
                ensure_ascii=False,
            )
        elif send_type == "link":
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

    def __send_request_get_remark(self, data, data_dict):
        url = self.single_conf.get("url", "")
        res = requests.post(url, headers=self.headers, json=data).json()
        msg = res.get("message")
        if msg == "不合法的access_token":
            app.config["TOKEN"] = get_access_token()
            self.headers["x-acs-dingtalk-access-token"] = app.config["TOKEN"]
            res = requests.post(url, headers=self.headers, json=data).json()
        if res.get("message"):
            data_dict["status"] = 2
            rsp_msg = res.get("message")
            at_user = ""
        else:
            nonexist = res.get("invalidStaffIdList")
            rep_query = res.get("processQueryKey")
            data_dict["status"] = 1
            if nonexist:
                at_user = self.payload.get("userids")
                for stff in nonexist:
                    at_user.remove(stff)
                at_user = ",".join(at_user)
                rsp_msg = {
                    "status": "ok, but {} nonexistent.".format(nonexist),
                    "processQueryKey": rep_query,
                }
            else:
                at_user = ",".join(self.payload.get("userids", []))
                rsp_msg = {"status": "ok", "processQueryKey": rep_query}
        data_dict["at_user"] = at_user
        data_dict["remark"] = json.dumps(rsp_msg, ensure_ascii=False)
        return rsp_msg

    def send_text(self):
        content = self.__build_content_on_type("text")
        filter_list = self.search_data(content)
        if not filter_list:
            data = {
                "robotCode": self.robot_conf["robotCode"],
                "userIds": self.payload.get("userids", []),
                "msgKey": "sampleText",
                "msgParam": json.dumps(
                    {"content": content},
                    ensure_ascii=False,
                ),
            }
            data_dict = self.format_datadict()
            data_dict["content"] = content
            rsp_msg = self.__send_request_get_remark(data, data_dict)
            self.oper_alarm.add_data_to_db(data_dict)
            return rsp_msg
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }

    def send_markdown(self):
        content = self.__build_content_on_type("markdown")
        filter_list = self.search_data(content)
        if not filter_list:
            data_dict = self.format_datadict()
            data = {
                "robotCode": self.robot_conf["robotCode"],
                "userIds": self.payload.get("userids"),
                "msgKey": "sampleMarkdown",
                "msgParam": content,
            }
            rsp_msg = self.__send_request_get_remark(data, data_dict)
            data_dict["content"] = content
            data_dict["at_user"] = ",".join(self.payload.get("userids"))
            if self.oper_alarm.add_data_to_db(data_dict):
                return rsp_msg
            else:
                return {"err_msg": f"{data_dict}: 數據插入數據庫失敗"}
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }

    def send_link(self):
        content = self.__build_content_on_type("link")
        filter_list = self.search_data(content)
        if not filter_list:
            data_dict = self.format_datadict()
            data = {
                "robotCode": self.robot_conf["robotCode"],
                "userIds": self.payload.get("userids"),
                "msgKey": "sampleLink",
                "msgParam": content,
            }
            rsp_msg = self.__send_request_get_remark(data, data_dict)
            data_dict["content"] = content
            data_dict["at_user"] = ",".join(self.payload.get("userids"))
            if self.oper_alarm.add_data_to_db(data_dict):
                return rsp_msg
            else:
                return {"err_msg": f"{data_dict}: 數據插入數據庫失敗"}
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }


class SendAlarmSingleFileController(BaseSendAlarmSingle):
    def __init__(self, ip, payload, file) -> None:
        super().__init__(ip, payload)
        self.file = file

    def __format_data(self, send_type, file_path, result):
        data = {
            "robotCode": self.robot_conf["robotCode"],
            "userIds": self.payload.get("userids"),
            "msgKey": "sampleImageMsg",
        }
        if send_type == "image":
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

    def send_file(self):
        send_type = self.payload["type"]
        file_data = self.file.stream.read()
        file_path = f"./static/{send_type}s/" + self.file.filename
        if not self.sasf.receive_convert_archive_file(file_path, file_data):
            return {"err_msg": "文件流創建失敗"}
        hashed_string = self.sasf.get_encode_string(file_data)
        filter_list = self.search_data(hashed_string)
        if not filter_list:
            data_dict = self.format_datadict()
            result = self.sasf.send_req_get_upload_media(file_path, send_type)
            if not result.startswith("@"):
                return {"err_msg": result}
            data = self.__format_data(send_type, file_path, result)
            data_dict["content"] = hashed_string
            rsp_msg = self.sasf.send_request_get_remark(
                data, data_dict, file_path, file_data
            )
            data_dict["at_user"] = ",".join(self.payload.get("userids"))
            if self.oper_alarm.add_data_to_db(data_dict):
                return rsp_msg
            else:
                return {"err_msg": f"{data_dict}: 數據插入數據庫失敗"}
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }
