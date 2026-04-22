# -*- coding: utf-8 -*-
'''
@文件: sckedule_task.py
@說明: 定時任務
'''
import datetime
import json
import traceback
from functools import cached_property

import requests
from apscheduler.schedulers.background import BackgroundScheduler


class UploadDataScheduleTask:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()

    @cached_property
    def conf(self):
        with open("./sdk/conf/conf.json", "r", encoding="utf-8") as f:
            data = json.loads(f.read())
        return data

    def get_now(self):
        now_time = datetime.datetime.now()
        return now_time.strftime("%Y-%m-%d %H:%M:%S")

    def upload_data(self, service_status):
        url = "http://monitor.ai.eavarytech.com:19360/api/upload_data"
        payload = {
            "address": self.conf.get("ADDRESS", ""),
            "service_name": self.conf.get("SERVICE_NAME", ""),
            "service_id": self.conf.get("SERVICE_ID", ""),
            "data": [{
                "service_status": service_status
            }],
            "time": self.get_now()
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            content = response.json()
            if content.get("code", "F10001") == "S10000":
                print("數據上報成功")
            else:
                print("數據上報失敗")
        except Exception:
            traceback.print_exc()

    def do_job_per_minute(self):
        address = self.conf.get("ADDRESS", "")
        port = self.conf.get("PORT", "")
        try:
            url = f"http://{address}:{port}/monitor_verification_api"
            res = requests.get(url, timeout=30).json()
        except Exception:
            print("/monitor_verification_api 接口訪問失敗")
            traceback.print_exc()
            res = dict()
        if res.get("code", 400) == 200:
            self.upload_data(2)
        else:
            self.upload_data(1)

    def run(self):
        period = int(self.conf.get("PERIOD", 1))
        seconds = int(period/5)*4
        if seconds < 1:
            seconds = 1
        self.scheduler.add_job(
            func=self.do_job_per_minute,
            trigger="interval", seconds=seconds
        )
        self.scheduler.start()
