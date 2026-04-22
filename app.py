# -*- coding: utf-8 -*-
"""
@文件: app.py
@說明: server啟動文件
@時間: 2023/10/19 19:09:13
@作者: LiDong
"""
import json
import os
import time
import traceback
from datetime import timedelta
from threading import Thread

from flask import Flask, request, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_smorest import Api
from waitress import serve

from common.common_method import fail_response_result
from common.scheduler_get_token import process_get_token
from configs.app_config import SQLALCHEMY_DATABASE_URI, port
from configs.const_conf import ENV
from configs.constant import conf
from dbs.mysql_db import db
import structlog
# from loggers import logger
from loggers.logger import configure_logger
from views.login_and_registrate_api import blp as login_and_registrate_blp
from views.read_status_api import blp as read_status_blp
from views.send_alarm_group_file_api import blp as send_alarm_group_file_blp
from views.send_alarm_group_msg_api import blp as send_alarm_group_msg_blp
from views.send_alarm_mail_api import blp as send_alarm_mail_blp
from views.send_alarm_single_api import blp as send_alarm_single_blp
from sdk.monitor_verification_api import blp as sdk_blp
from sdk.schedule_task import UploadDataScheduleTask

def create_app():
    app = Flask(__name__, static_folder="./static/")
    CORS(app, supports_credentials=True)
    app.config["TOKEN"] = "default"
    app.config["CORS_HEADERS"] = "Content-Type"
    app.config["Access-Control-Allow-Origin"] = "*"
    app.config["API_TITLE"] = "ALARM SERVER REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JSON_AS_ASCII"] = False
    app.config["JSONIFY_MIMETYPE"] = "application/json;charset=utf-8"
    app.config["KEEP_ALIVE"] = False
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config["JWT_SECRET_KEY"] = "Avary88!"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(weeks=4)
    app.config["SECRET_KEY"] = "AASDFASDF"
    # app.logger = logger
    service_name = conf.get("service_name")
    app.logger = structlog.get_logger("my.custom").bind(service={"name": service_name, "environment": ENV})
    migrate = Migrate()
    migrate.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    marsh = Marshmallow()
    marsh.init_app(app)

    jwt = JWTManager()
    jwt.init_app(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return fail_response_result(msg="Token is expired")

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return fail_response_result(msg="Token is invalid")

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return fail_response_result(msg="Missing Authentication Token")

    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.req_body = request.get_data(as_text=True)

    @app.after_request
    def after_request(resp):
        try:
            data = json.loads(resp.data)
            if data.get("code", 200) == 422:
                resp.data = json.dumps(
                    fail_response_result(content=data.get("errors")),
                    ensure_ascii=False,
                )
                resp.status = 200
        except Exception:
            app.logger.error(traceback.format_exc())

        event = "after_request"
        body = json.loads(resp.data)
        status_code = resp.status_code
        event_duration = round(time.time() - g.start_time, 3)

        req_head = {k: v for k, v in request.headers.items()}

        # 判断是否为 multipart/form-data（即上传文件场景）
        if request.content_type and "multipart/form-data" in request.content_type:
            # 为不被前置业务逻辑影响，需要重置文件流指针
            for file in request.files.values():
                file.stream.seek(0)
            # 只记录表单字段 + 每个文件的 元信息（文件名 + 大小），避免把整个文件体写入日志
            files_info = {
                name: {"filename": file.filename,
                       "size": len(file.read())}
                for name, file in request.files.items()
            }
            # 读取了 file.read()，为不影响后续业务逻辑，需要重置文件流指针
            for file in request.files.values():
                file.stream.seek(0)

            req_body = {
                "form": request.form.to_dict(),
                "files": files_info
            }
        else:
            # 非文件上传请求，继续使用之前 stored 的请求体
            req_body = getattr(g, "req_body", None)
        try:
            req_body = json.dumps(json.loads(req_body), ensure_ascii=False)
        except Exception: pass
        log_req = {"method": request.method, "path": request.path, "headers": req_head, "body": req_body}
        log_resp = {"status_code": status_code, "body": body, "event_duration": event_duration}

        if body.get("code") == "S10000":
            app.logger.info(event, req=log_req, resp=log_resp)  # type: ignore
        else:
            app.logger.warning(event, req=log_req, resp=log_resp)  # type: ignore
        return resp

    api = Api(app)
    api.register_blueprint(login_and_registrate_blp)
    api.register_blueprint(send_alarm_single_blp)
    api.register_blueprint(send_alarm_group_msg_blp)
    api.register_blueprint(send_alarm_group_file_blp)
    api.register_blueprint(send_alarm_mail_blp)
    api.register_blueprint(read_status_blp)
    api.register_blueprint(sdk_blp)
    return app


if __name__ == "__main__":
    app = create_app()
    with open("pid", "w") as f:
        pid = str(os.getpid())
        print(">> pid: ", pid)
        f.write(pid)
    print("===================server starting============================")
    UploadDataScheduleTask().run()
    task_get_token = Thread(
        target=process_get_token, args=(app,), name="task_get_token"
    )
    task_get_token.setDaemon(True)
    task_get_token.start()
    # serve(app, host="0.0.0.0", port=port[ENV], threads=30)
    app.run("0.0.0.0", port[ENV], debug=True, use_reloader=False)
