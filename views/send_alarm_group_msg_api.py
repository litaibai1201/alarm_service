from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint

from common.common_method import fail_response_result, response_result
from common.common_tools import define_exist
from controllers.check_service_controller import CheckServiceController
from controllers.send_alarm_group_msg_controller import SendAlarmMsgController
from serializes.response_serialize import RspMsgSchema
from serializes.send_alarm_group_msg_serialize import SendAlarmGroupMsgSchema

blp = Blueprint("send_group_alarm_msg", __name__)


@blp.route("/api/sendGroupAlarmMsg")
class SendGroupAlarmMsg(MethodView):
    """
    此類用來定義/sendGroupAlarmMsg及請求方式
    """

    @blp.arguments(SendAlarmGroupMsgSchema)
    @blp.response(200, RspMsgSchema)
    def post(self, payload):
        csc = CheckServiceController(payload)
        if not csc.check_service():
            return fail_response_result(msg="服務還沒有進行註冊，無法發送消息")
        samc = SendAlarmMsgController(request.remote_addr, payload)
        if payload["type"] == "text":
            atuserids = payload.get("text").get("atuserids", [])
            content = define_exist(atuserids)
            if content:
                rsp_result = fail_response_result(content=content)
                return rsp_result
            rsp_msg = samc.send_text()
        elif payload["type"] == "link":
            rsp_msg = samc.send_link()
        elif payload["type"] == "markdown":
            atuserids = payload.get("markdown").get("atuserids")
            if atuserids:
                user_id_list = atuserids.get("at") + atuserids.get("cc", [])
                content = define_exist(user_id_list)
                if content:
                    rsp_result = fail_response_result(content=content)
                    return rsp_result
            rsp_msg = samc.send_markdown()
        if rsp_msg == "ok":
            rsp_result = response_result()
        else:
            rsp_result = fail_response_result(content={"errmsg": rsp_msg})
        return rsp_result
