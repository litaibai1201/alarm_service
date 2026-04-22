# -*- coding: utf-8 -*-
'''
@文件: monitor_verification_api.py
@說明:
'''

from flask.views import MethodView
from flask_smorest import Blueprint

blp = Blueprint("monitor_verification_api", __name__)


@blp.route("/monitor_verification_api")
class ImageUpload(MethodView):

    @blp.response(200)
    def get(self):
        return {"code": 200}
