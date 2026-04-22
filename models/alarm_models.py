# -*- coding: utf-8 -*-
"""
@文件: test_model.py
@說明: 模型方法
@時間: 2023/10/26 17:13:07
@作者: LiDong
"""
import time
import traceback

from flask import current_app as app
from sqlalchemy.dialects import mysql

from dbs.mysql_db import db
from dbs.mysql_db.model_tables import AlarmRecorModel


class OperAlarmRecorModel:
    def add_data_to_db(self, data):
        if not data:
            return False
        start_time = time.time()
        sql_str = ""
        status = "success"
        try:
            statement = AlarmRecorModel.__table__.insert().values(**data)
            sql_str = str(statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))

            # data["id"] = int(time.time() * 1000)
            db.session.add(AlarmRecorModel(**data))
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

    def __format_session_data(self, ip, method, content, at_user, filter_time):
        session_data = db.session.query(AlarmRecorModel).filter(
            AlarmRecorModel.ip == ip,
            AlarmRecorModel.method_to_inform == method,
            AlarmRecorModel.content == content,
            AlarmRecorModel.at_user == at_user,
            AlarmRecorModel.created_at >= filter_time,
        )
        return session_data

    def search_data(
        self,
        ip,
        method,
        content,
        webhook,
        type,
        at_user,
        filter_time,
    ):
        session_data = self.__format_session_data(
            ip, method, content, at_user, filter_time
        )
        if method == "group":
            filter_list = session_data.filter(
                AlarmRecorModel.webhook == webhook,
                AlarmRecorModel.type == type,
            ).first()
        elif method == "single":
            filter_list = session_data.first()
        elif method == "email":
            filter_list = session_data.filter(
                AlarmRecorModel.type == type,
            ).first()
        return filter_list
