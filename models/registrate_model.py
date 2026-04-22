# -*- coding: utf-8 -*-
"""
@文件: registrate_model.py
@說明:
@時間: 2023/12/08 19:33:38
@作者: LiDong
"""
import time

from sqlalchemy.dialects import mysql

from dbs.mysql_db import db
from dbs.mysql_db.model_tables import RegistrationModel
from loggers import logger


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

            db.session.add(RegistrationModel(**data))
            db.session.commit()

            duration = round(time.time() - start_time, 3)
            logger.info("數據插入成功", db={"statement": sql_str, "status": status, "duration": duration})
            return True
        except Exception as e:
            db.session.rollback()

            status = "fail"
            duration = round(time.time() - start_time, 3)
            logger.error("數據插入失敗", db={"statement": sql_str, "status": status, "duration": duration}, error=e)
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
