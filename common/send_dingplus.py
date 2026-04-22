import time

import requests

from configs.const_conf import ENV
from configs.constant import conf

# 缓存access_token的全局变量
access_token_cache = {"token": None, "expires_at": 0}


# 获取access_token
def get_access_token():
    app_key = conf["robot_conf"][ENV]["app_key"]
    app_secret = conf["robot_conf"][ENV]["app_secret"]
    current_time = time.time()
    if access_token_cache["token"] and access_token_cache["expires_at"] > current_time:
        # print("缓存token")
        return access_token_cache["token"]  # 有效期未到时获取缓存token
    url = f"http://10.182.179.113:8081/gettoken?appkey={app_key}&appsecret={app_secret}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        result = response.json()
        access_token = result.get("access_token")
        if access_token:
            access_token_cache["token"] = access_token
            access_token_cache["expires_at"] = (
                current_time + 7150
            )  # token获取一次有效期为2小时 2小时后再次获取
            # print("新token", access_token)
            return access_token
        else:
            print("未能获取access_token")
    else:
        print("获取access_token失败")
