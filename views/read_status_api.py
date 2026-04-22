from flask.views import MethodView
from flask_smorest import Blueprint

from common.common_method import response_result
from controllers.read_status_controller import ReadStatusController
from serializes.read_status_serialize import ReadStatusSchema
from serializes.response_serialize import RspMsgSchema

blp = Blueprint("read_status", __name__)


@blp.route("/api/ReadStatus")
class ReadStatus(MethodView):
    """
    此類用來定義/ReadStatus及請求方式
    """

    @blp.arguments(ReadStatusSchema)
    @blp.response(200, RspMsgSchema)
    def get(self, payload):
        rsc = ReadStatusController(payload)
        if payload["type"] == "single":
            rsp_msg = rsc.read_status_single()
        elif payload["type"] == "group":
            rsp_msg = rsc.read_status_group()
        return response_result(content={"errmsg": rsp_msg})
