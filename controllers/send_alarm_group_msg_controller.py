import json
from datetime import datetime, timedelta

import requests

from models.alarm_models import OperAlarmRecorModel


class SendAlarmMsgController:
    def __init__(self, ip, payload) -> None:
        self.ip = ip
        self.headers = {"Content-Type": "application/json"}
        self.corpid = "ding2b4c83bec54a29c6f2c783f7214b6d69"
        self.oper_alarm = OperAlarmRecorModel()
        self.payload = payload

    def __search_data(self):
        type = self.payload.get("type")
        if self.payload.get(type).get("isatall"):
            atuser = "all"
        else:
            atuser = self.payload.get(type).get("atuserids")
            if atuser:
                atuser = ",".join(atuser)
        if type == "text":
            content = self.payload.get("text").get("content")
        elif type == "link":
            content = json.dumps(
                {
                    "message_url": self.payload.get("link").get("message_url"),
                    "title": self.payload.get("link").get("title"),
                    "text": self.payload.get("link").get("text"),
                },
                ensure_ascii=False,
            )
        filter_list = self.oper_alarm.search_data(
            self.ip,
            "group",
            content,
            self.payload.get("webhook"),
            type,
            atuser,
            datetime.now() - timedelta(minutes=self.payload.get("same_alarm_inter")),
        )
        return filter_list

    def __format_data(self):
        data_dict = dict()
        data_dict["ip"] = self.ip
        data_dict["service_name"] = self.payload.get("service_name")
        data_dict["method_to_inform"] = "group"
        data_dict["webhook"] = self.payload.get("webhook")
        data_dict["type"] = self.payload.get("type")
        return data_dict

    def __send_request_get_remark(self, data, data_dict):
        url = self.payload.get("webhook")
        rep = requests.post(url, headers=self.headers, json=data)
        error_msg = rep.json().get("errmsg")
        if error_msg == "ok":
            data_dict["status"] = 1
        else:
            data_dict["status"] = 2
        data_dict["remark"] = error_msg
        return error_msg

    def send_text(self):
        filter_list = self.__search_data()
        if not filter_list:
            text = self.payload.get("text", {})
            data = {
                "msgtype": "text",
                "text": {"content": text["content"]},
                "at": {
                    "isAtAll": text.get("isatall", False),
                    "atUserIds": text.get("atuserids", []),
                },
            }
            data_dict = self.__format_data()
            data_dict["content"] = text.get("content", "")
            if text.get("isatall"):
                at_user = "all"
            else:
                at_user = ",".join(text.get("atuserids", []))
            data_dict["at_user"] = at_user
            rsp_msg = self.__send_request_get_remark(data, data_dict)
            self.oper_alarm.add_data_to_db(data_dict)
            return rsp_msg
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }

    def send_link(self):
        filter_list = self.__search_data()
        if not filter_list:
            data = {
                "msgtype": "link",
                "link": {
                    "messageUrl": self.payload["link"]["message_url"],
                    "title": self.payload["link"]["title"],
                    "text": self.payload["link"]["text"],
                },
            }
            data_dict = self.__format_data()
            data_dict["content"] = json.dumps(
                self.payload.get("link", {}),
                ensure_ascii=False,
            )
            rsp_msg = self.__send_request_get_remark(data, data_dict)
            self.oper_alarm.add_data_to_db(data_dict)
            return rsp_msg
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }

    def __search_markdown_data(self):
        if self.payload.get("markdown").get("atuserids"):
            at_ids = self.payload.get("markdown").get("atuserids").get("at", [])
            cc_ids = self.payload.get("markdown").get("atuserids").get("cc", [])
            atuser = "at " + ",".join(at_ids) + " cc " + ",".join(cc_ids)
        else:
            atuser = None
        filter_list = self.oper_alarm.search_data(
            self.ip,
            "group",
            self.payload.get("markdown").get("text"),
            self.payload.get("webhook"),
            self.payload.get("type"),
            atuser,
            datetime.now() - timedelta(minutes=self.payload.get("same_alarm_inter")),
        )
        return filter_list

    def __get_transmission_method(self, list_id):
        tx_method = ""
        for at_id in list_id:
            tx_method += f"[@{at_id}](dingtalk://dingtalkclient/page/profile?corp_id={self.corpid}&staff_id={at_id}) "
        return tx_method

    def __get_at_temp(self, data_dict):
        at_ids = self.payload.get("markdown").get("atuserids").get("at", [])
        cc_ids = self.payload.get("markdown").get("atuserids").get("cc", [])
        atuserids = at_ids + cc_ids
        at_tx_method = self.__get_transmission_method(at_ids)
        data_dict["content"] = self.payload["markdown"]["text"]
        text = (
            self.payload["markdown"]["text"]
            + f"\n {at_tx_method}"
            + self.payload.get("markdown").get("atuserids").get("after_at_msg", "")
        )
        if cc_ids:
            cc_tx_method = self.__get_transmission_method(cc_ids)
            text += f"\n\r cc {cc_tx_method}"
        data_dict["at_user"] = "at " + ",".join(at_ids) + " cc " + ",".join(cc_ids)
        return atuserids, text, data_dict

    def send_markdown(self):
        filter_list = self.__search_markdown_data()
        if not filter_list:
            data_dict = self.__format_data()
            if self.payload.get("markdown").get("atuserids"):
                atuserids, text, data_dict = self.__get_at_temp(data_dict)
            else:
                atuserids, data_dict["at_user"] = [], None
                text = self.payload["markdown"]["text"]
                data_dict["content"] = text
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": self.payload["markdown"]["title"],
                    "text": text,
                },
                "at": {"atUserIds": atuserids},
            }
            rsp_msg = self.__send_request_get_remark(data, data_dict)
            self.oper_alarm.add_data_to_db(data_dict)
            return rsp_msg
        else:
            return {
                "err_msg": f"{self.payload.get('same_alarm_inter')}分鐘內禁止發送相同數據"
            }
