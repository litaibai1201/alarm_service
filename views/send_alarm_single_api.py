from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint

from common.common_method import fail_response_result, response_result
from common.common_tools import define_exist
from controllers.check_service_controller import CheckServiceController
from controllers.send_alarm_single_controller import (
    SendAlarmSingleFileController,
    SendAlarmSingleMsgController,
)
from serializes.response_serialize import RspMsgSchema
from serializes.send_alarm_single_serialize import SendAlarmSingleSchema

blp = Blueprint("send_single_alarm", __name__)


@blp.route("/api/sendSingleAlarm")
class SendSingleAlarm(MethodView):
    """
    此類用來定義/sendSingleAlarm及請求方式
    """

    @blp.arguments(SendAlarmSingleSchema, location="form")
    @blp.response(200, RspMsgSchema)
    def post(self, payload):
        csc = CheckServiceController(payload)
        if not csc.check_service():
            return fail_response_result(msg="服務還沒有進行註冊，無法發送消息")
        atuserids = payload.get("userids")
        content = define_exist(atuserids)
        if content:
            rsp_result = fail_response_result(content=content)
            return rsp_result
        ip = request.remote_addr
        sasmc = SendAlarmSingleMsgController(ip, payload)
        if payload["type"] == "text":
            rsp_msg = sasmc.send_text()
        elif payload["type"] == "markdown":
            rsp_msg = sasmc.send_markdown()
        elif payload["type"] == "link":
            rsp_msg = sasmc.send_link()
        elif payload["type"] in ["image", "file"]:
            file = request.files.get(payload["type"])
            if not file:
                return fail_response_result(content={"errmsg": "文件不能為空"})
            sasfc = SendAlarmSingleFileController(ip, payload, file)
            rsp_msg = sasfc.send_file()
        if rsp_msg.get("status") == "ok":
            rsp_result = response_result(content=rsp_msg)
        else:
            rsp_result = fail_response_result(content={"errmsg": rsp_msg})
        return rsp_result
