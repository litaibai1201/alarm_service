# -*- coding: utf-8 -*-
"""
@文件: login_api.py
@說明:
@時間: 2023/12/08 16:04:28
@作者: LiDong
"""
from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint

from common.common_method import fail_response_result, response_result
from configs.constant import conf
from controllers.login_and_registrate_controller import (
    LoginController,
    RegistrateController,
)
from serializes.login_and_registrate_serialize import (
    LoginSchema,
    RegistrationModelSchema,
    RegistrationSchema,
)
from serializes.response_serialize import RspMsgSchema, RspRegistrationSchema

blp = Blueprint("login", __name__)


@blp.route("/api/login")
class LogIn(MethodView):
    """
    此類用來定義/Login及請求方式
    """

    @blp.arguments(LoginSchema)
    @blp.response(200, RspMsgSchema)
    def post(self, payload):
        work_no = payload.get("work_no")
        payload["service_name"] = conf.get("service_name")
        ip = request.remote_addr
        lc = LoginController(ip, payload)
        result_ldap = lc.login_ldap()
        if result_ldap["code"] == "S10000":
            token = lc.get_token()
            rsp_result = response_result(content={"token": token})
        else:
            rsp_result = fail_response_result(msg="帳號或密碼或園區錯誤")
        return rsp_result


@blp.route("/api/registrate")
class Registrate(MethodView):
    """
    此類用來定義/Registrate及請求方式
    """

    @jwt_required()
    @blp.arguments(RegistrationSchema)
    @blp.response(200, RspMsgSchema)
    def post(self, payload):
        user_data = get_jwt_identity()
        payload["work_no"] = user_data["work_no"]
        rc = RegistrateController(payload)
        token = rc.search()
        if token:
            return fail_response_result(
                msg="該服務名已經註冊",
                content={"token": token[0]},
            )
        token = rc.get_token()
        payload["token"] = token
        payload["service_host"] = request.remote_addr
        result = rc.add(payload)
        if result:
            return response_result(content=payload)
        return fail_response_result(msg="服務註冊失敗")

    @jwt_required()
    @blp.response(200, RspRegistrationSchema)
    def get(self):
        user_data = get_jwt_identity()
        payload = {"work_no": user_data["work_no"]}
        rc = RegistrateController(payload)
        result = rc.get_datalist()
        rms = RegistrationModelSchema()
        datalist = rms.dump(result, many=True)
        return response_result(content=datalist)
