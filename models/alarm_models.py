# -*- coding: utf-8 -*-
"""
@文件: test_model.py
@說明: 模型方法
@時間: 2023/10/26 17:13:07
@作者: LiDong
"""
import hashlib
import time

from sqlalchemy.dialects import mysql

from dbs.mysql_db import db
from dbs.mysql_db.model_tables import AlarmRecorModel
from loggers import logger


def _compute_content_hash(content: str) -> str:
    """计算内容的 SHA256 哈希值，用于去重查询"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class OperAlarmRecorModel:
    def add_data_to_db(self, data):
        if not data:
            return False
        # 自动计算 content_hash
        if "content" in data and "content_hash" not in data:
            data["content_hash"] = _compute_content_hash(data["content"])

        start_time = time.time()
        sql_str = ""
        status = "success"
        try:
            statement = AlarmRecorModel.__table__.insert().values(**data)
            sql_str = str(statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))

            db.session.add(AlarmRecorModel(**data))
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

    def __format_session_data(self, ip, method, content_hash, at_user, filter_time):
        session_data = db.session.query(AlarmRecorModel).filter(
            AlarmRecorModel.ip == ip,
            AlarmRecorModel.method_to_inform == method,
            AlarmRecorModel.content_hash == content_hash,
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
        content_hash = _compute_content_hash(content)
        session_data = self.__format_session_data(
            ip, method, content_hash, at_user, filter_time
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
