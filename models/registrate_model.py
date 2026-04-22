# -*- coding: utf-8 -*-
"""
@文件: registrate_model.py
@說明:
@時間: 2023/12/08 19:33:38
@作者: LiDong
"""
import time
import traceback

from flask import current_app as app
from sqlalchemy.dialects import mysql

from dbs.mysql_db import db
from dbs.mysql_db.model_tables import RegistrationModel

# from uuid import uuid4




class OperRegistrationModel:
    def add_data_to_db(self, data):
        if not data:
            return False
        start_time = time.time()
        sql_str = ""
        status = "success"
        try:
            statement = RegistrationModel.__table__.insert().values(**data)
            sql_str = str(statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))

            # data["id"] = uuid4().hex
            db.session.add(RegistrationModel(**data))
            db.session.commit()

            duration = round(time.time() - start_time, 3)
            app.logger.info(db={"statement": sql_str, "status": status, "duration": duration})  # type: ignore
            return True
        except Exception:
            db.session.rollback()

            status = "fail"
            duration = round(time.time() - start_time, 3)
            app.logger.error("數據插入失敗", db={"statement": sql_str, "status": status, "duration": duration})  # type: ignore
            app.logger.error(traceback.format_exc())
            return False

    def search_token(self, service_name, service_type):
        result = (
            db.session.query(RegistrationModel.token)
            .filter(
                RegistrationModel.service_name == service_name,
                RegistrationModel.service_type == service_type,
            )
            .first()
        )
        return result

    def search_service(self, service_name, service_type, token):
        result = (
            db.session.query(RegistrationModel)
            .filter(
                RegistrationModel.token == token,
                RegistrationModel.service_name == service_name,
                RegistrationModel.service_type == service_type,
            )
            .first()
        )
        if result:
            return True
        return False

    def search_data(self, work_no):
        result = (
            db.session.query(
                RegistrationModel.service_name,
                RegistrationModel.service_type,
                RegistrationModel.service_host,
                RegistrationModel.token,
                RegistrationModel.created_at,
            )
            .filter(RegistrationModel.work_no == work_no)
            .order_by(RegistrationModel.created_at)
            .all()
        )
        return result
