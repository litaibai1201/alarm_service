import hashlib
import io
import os

import requests
from flask import current_app as app

from common.send_dingplus import get_access_token
from configs.constant import conf


class SendAlarmFile:
    def __init__(self) -> None:
        self.url = "http://10.182.179.113:8080/v1.0/robot/groupMessages/send"
        self.media_url = (
            "http://10.182.179.113:8081/media/upload?access_token={}&type={}"
        )
        self.token = app.config["TOKEN"]
        self.headers = {"Content-Type": "application/json"}

    def get_encode_string(self, image_data):
        hashed_string = hashlib.sha256(str(image_data).encode()).hexdigest()
        return hashed_string

    def send_req_get_upload_media(self, file_path, send_type):
        url = self.media_url.format(self.token, send_type)
        with open(file_path, "rb") as f:
            res = requests.post(url, files={"media": f}, timeout=30).json()
        msg = res.get("errmsg")
        if msg == "不合法的access_token":
            self.token = get_access_token()
            app.config["TOKEN"] = self.token
            url = self.media_url.format(self.token, send_type)
            with open(file_path, "rb") as f:
                res = requests.post(url, files={"media": f}, timeout=30).json()
            msg = res.get("errmsg")
        if msg != "ok":
            return msg
        self.headers["x-acs-dingtalk-access-token"] = self.token
        media_id = res.get("media_id")
        return media_id

    def send_request_get_remark(
        self,
        data,
        data_dict,
        file_path,
        orig_file_data,
    ):
        rep = requests.post(self.url, headers=self.headers, json=data, timeout=10).json()
        rep_query = rep.get("processQueryKey")
        if rep_query:
            data_dict["status"] = 1
            if os.path.exists(file_path):
                os.remove(file_path)
            return {"status": "ok", "processQueryKey": rep_query}
        else:
            data_dict["status"] = 2
            file_exten = file_path.split(".")[-1]
            file_name = f"{data_dict['content']}.{file_exten}"
            with open(conf["unsuccessful_files"] + f"/{file_name}", "wb") as f:
                f.write(orig_file_data)
            err_msg = rep.get("message")
            data_dict["remark"] = err_msg + f"，{file_name}"
            return {"err_msg": err_msg}

    def receive_convert_archive_file(self, file_path, file_data):
        dir_path = file_path[: -len(file_path.split("/")[-1])]
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        try:
            with io.FileIO(file_path, "w+") as file_io:
                file_io.write(file_data)
            return True
        except Exception:
            return False


class SendAlarmSingleFile(SendAlarmFile):
    def __init__(self) -> None:
        super().__init__()
        self.url = "http://10.182.179.113:8080/v1.0/robot/oToMessages/batchSend"
