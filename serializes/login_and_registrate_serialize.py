# -*- coding: utf-8 -*-
"""
@文件: login_serialize.py
@說明:
@時間: 2023/12/08 16:09:41
@作者: LiDong
"""
import re

from marshmallow import Schema, ValidationError, fields, validate, validates

from configs.constant import conf


class LoginSchema(Schema):
    work_no = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=32, error="work_no Length out of range"),
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=1, error="password Length out of range"),
    )
    location = fields.Str(
        required=True,
        validate=validate.OneOf(
            conf.get("location_list"), error="Location parameter error"
        ),
    )


class RegistrationSchema(Schema):
    service_name = fields.Str(required=True)
    service_type = fields.Str(
        required=True,
        validate=validate.OneOf(["RPA", "Web"]),
        error="The service type must be one of: RPA, Web.",
    )

    @validates("service_name")
    def validate_service_name(self, value):
        if not value.strip():
            raise ValidationError("service_name not empty!")
        if len(value) > 30:
            raise ValidationError("service_name must be no more than 30 words!")
        char_str = "[ /@*&%$#^()~!+?><'\"\\\[\]\{\};,.:；“”‘’《》，？、|]"
        result = re.findall(char_str, value)
        if result:
            raise ValidationError(
                f"service_name cannot contain special characters like {' '.join(result)}"
            )


class RegistrationModelSchema(Schema):
    service_name = fields.Str(required=True)
    service_type = fields.Str(required=True)
    service_host = fields.Str(required=True)
    token = fields.Str(required=True)
    created_at = fields.Str(required=True)
