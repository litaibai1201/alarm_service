# -*- coding: utf-8 -*-
"""
@文件: all_db.py
@說明: 模型類
@時間: 2023/10/26 16:54:19
@作者: LiDong
"""

from common.common_tools import get_now
from common.snow_generator import snow_generator
from dbs.mysql_db import db


class BaseMixinModel(db.Model):
    __abstract__ = True

    id = db.Column(
        db.String(18), nullable=False, primary_key=True, comment="時間戳",
        default=snow_generator.get_id
    )
    status = db.Column(db.Integer, default=1, comment="状态")
    created_at = db.Column(
        db.String(19), default=get_now, nullable=False, comment="創建時間"
    )
    update_at = db.Column(db.String(19), comment="更新時間")
    status_update_at = db.Column(db.String(19), comment="状态更新時間")


class AlarmRecorModel(BaseMixinModel):
    __tablename__ = "alarm_record_form"

    ip = db.Column(db.String(15), nullable=False, comment="IP地址")
    method_to_inform = db.Column(db.String(16), nullable=False, comment="通知方式")
    service_name = db.Column(db.String(128), nullable=False, comment="服務名稱")
    content = db.Column(db.Text, nullable=False, comment="內容")
    content_hash = db.Column(db.String(64), nullable=True, comment="內容SHA256哈希", index=True)
    webhook = db.Column(db.String(256), comment="機器人地址")
    type = db.Column(db.String(16), nullable=False, comment="消息類型")
    at_user = db.Column(db.String(1024), comment="通知人")
    remark = db.Column(db.Text, comment="備註")

    __table_args__ = (
        db.Index(
            "ix_alarm_dedup",
            "ip", "method_to_inform", "content_hash", "at_user", "webhook", "type", "created_at",
        ),
    )


class RegistrationModel(BaseMixinModel):
    __tablename__ = "registration_form"

    service_name = db.Column(db.String(64), nullable=False, comment="服務名")
    service_type = db.Column(db.String(32), nullable=False, comment="服務類型")
    service_host = db.Column(db.String(15), nullable=False, comment="IP地址")
    work_no = db.Column(db.String(32), nullable=False, comment="工號")
    token = db.Column(db.String(64), nullable=False, comment="token")

    __table_args__ = (
        db.UniqueConstraint("service_name", "service_type", name="unique_name_type"),
    )
