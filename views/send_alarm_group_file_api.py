from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint

from common.common_method import fail_response_result, response_result
from controllers.check_service_controller import CheckServiceController
from controllers.send_alarm_group_file_controller import SendAlarmFileController
from serializes.response_serialize import RspMsgSchema
from serializes.send_alarm_group_file_serialize import SendAlarmGroupFileSchema

blp = Blueprint("send_group_alarm_file", __name__)


@blp.route("/api/sendGroupAlarmFile")
class SendGroupAlarmFile(MethodView):
    """
    此類用來定義/SendAlarmFile及請求方式
    """

    @blp.arguments(SendAlarmGroupFileSchema, location="form")
    @blp.response(200, RspMsgSchema)
    def post(self, payload):
        csc = CheckServiceController(payload)
        if not csc.check_service():
            return fail_response_result(msg="服務還沒有進行註冊，無法發送消息")
        samc = SendAlarmFileController(request.remote_addr, payload)
        if payload["type"] == "text":
            rsp_msg = samc.send_text()
        elif payload["type"] == "markdown":
            rsp_msg = samc.send_markdown()
        elif payload["type"] == "link":
            rsp_msg = samc.send_link()
        elif payload["type"] in ["image", "file"]:
            file = request.files.get(payload.get("type"))
            if not file:
                rsp_msg = {"err_msg": "文件不能為空"}
            else:
                rsp_msg = samc.send_file(file)
        if rsp_msg.get("status") == "ok":
            rsp_result = response_result(content=rsp_msg)
        else:
            rsp_result = fail_response_result(content={"errmsg": rsp_msg})
        return rsp_result
