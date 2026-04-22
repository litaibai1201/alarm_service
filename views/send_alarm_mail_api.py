from flask.views import MethodView
from flask_smorest import Blueprint

from common.common_method import fail_response_result, response_result
from controllers.check_service_controller import CheckServiceController
from controllers.send_alarm_mail_controller import SendAlarmMailController
from serializes.response_serialize import RspMsgSchema
from serializes.send_alarm_mail_serialize import SendAlarmMailSchema

blp = Blueprint("send_alarm_mail", __name__)


@blp.route("/api/sendAlarmMail")
class SendEmailAlarmMail(MethodView):
    """
    此類用來定義/SendAlarmMail及請求方式
    """

    @blp.arguments(SendAlarmMailSchema)
    @blp.response(200, RspMsgSchema)
    def post(self, payload):
        csc = CheckServiceController(payload)
        if not csc.check_service():
            return fail_response_result(msg="服務還沒有進行註冊，無法發送消息")
        samc = SendAlarmMailController(payload)
        rsp = samc.send_mail()
        if rsp == "ok":
            rsp_result = response_result()
        else:
            rsp_result = fail_response_result(content={"errmsg": rsp})
        return rsp_result
