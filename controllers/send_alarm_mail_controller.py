import json
from datetime import datetime, timedelta

from flask import request
from zeep import Client

from configs.constant import conf
from models.alarm_models import OperAlarmRecorModel


class SendAlarmMailController:
    def __init__(self, payload) -> None:
        self.ip = request.remote_addr
        self.conf = conf.get("mail_conf", {})
        self.oper_alarm = OperAlarmRecorModel()
        self.data = request.get_json()
        self.mail_type = self.data.get("mail_type")
        self.same_alarm_inter = self.data.get("same_alarm_inter")
        self.payload = payload

    def __search_data(self, text):
        filter_list = self.oper_alarm.search_data(
            self.ip,
            "email",
            text,
            self.payload.get("webhook"),
            self.mail_type,
            ",".join(self.payload.get("send_to")),
            datetime.now() - timedelta(minutes=self.same_alarm_inter),
        )
        return filter_list

    def __get_text(self, title, content):
        text = json.dumps(
            {"title": title, "content": content},
            ensure_ascii=False,
        )
        return text

    def __format_data(self):
        data_dict = dict()
        data_dict["service_name"] = self.payload.get("service_name", "")
        data_dict["method_to_inform"] = "email"
        data_dict["type"] = self.mail_type
        return data_dict

    def send_mail(self):
        title = self.payload["title"]
        content = self.payload["content"]
        text = self.__get_text(title, content)
        filter_list = self.__search_data(text)
        if not filter_list:
            if self.mail_type == "zheng":
                client = Client(wsdl=self.conf.get("wsdl_zheng", ""))
            elif self.mail_type == "peng":
                client = Client(wsdl=self.conf.get("wsdl_peng", ""))
            sysid = self.conf.get("sysid", "IMSA")
            m_from = self.conf.get("m_from", "系統郵件")
            send_to_list = self.payload["send_to"]
            for to in send_to_list:
                client.service.System_InsertMailData(
                    sysid,
                    m_from,
                    to,
                    title,
                    content,
                )
            data_dict = self.__format_data()
            data_dict["content"] = text
            data_dict["at_user"] = ",".join(send_to_list)
            data_dict["status"] = 2
            data_dict["ip"] = self.ip
            self.oper_alarm.add_data_to_db(data_dict)
            return "ok"
        return {"err_msg": f"{self.same_alarm_inter}分鐘內禁止發送相同數據"}
