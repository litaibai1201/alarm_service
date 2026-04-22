# -*- coding: utf-8 -*-
"""
@文件: check_service_controller.py
@說明:
@時間: 2023/12/09 16:18:29
@作者: LiDong
"""

from models.registrate_model import OperRegistrationModel


class CheckServiceController:
    def __init__(self, payload) -> None:
        self.oper_registration = OperRegistrationModel()
        self.payload = payload

    def check_service(self):
        service_name = self.payload.get("service_name")
        service_type = self.payload.get("service_type")
        token = self.payload.get("token")
        return self.oper_registration.search_service(
            service_name,
            service_type,
            token,
        )
