import json

from marshmallow import Schema, ValidationError, fields, validates, validates_schema


class SendAlarmGroupFileSchema(Schema):
    groupid = fields.Str(required=True)
    type = fields.Str(required=True)
    image = fields.Raw(type="image")
    file = fields.Raw(type="file")
    text = fields.Str()
    link = fields.Str()
    markdown = fields.Str()
    same_alarm_inter = fields.Integer(required=True)
    service_name = fields.Str(required=True)
    service_type = fields.Str(required=True)
    token = fields.Str(required=True)

    @validates("groupid")
    def validate_groupid(self, value):
        if not value.strip():
            raise ValidationError("groupid not empty!")

    @validates("type")
    def validate_type(self, value):
        if value not in ["image", "file", "text", "link", "markdown"]:
            raise ValidationError("type error!")

    @validates_schema
    def validate_type_key(self, data, **kwargs):
        if data["type"] not in ["image", "file"] and not data.get(data["type"]):
            raise ValidationError("type and parameter value validation failed!")

    @validates("text")
    def validate_text(self, value):
        try:
            text = json.loads(value)
            content = text.get("content")
            if not content:
                raise ValidationError("text's key must be 'content'!")
            if not content.strip():
                raise ValidationError("content not empty!")
            if len(content) > 1300:
                raise ValidationError("content must be no more than 1300 words!")
            if content.count("\n") > 30:
                raise ValidationError("content must be no more than 30 lines!")
        except json.decoder.JSONDecodeError:
            raise ValidationError("text's type must be json!")

    @validates("markdown")
    def validate_markdown(self, value):
        try:
            markdown = json.loads(value)
            title = markdown.get("title")
            if not title:
                raise ValidationError("markdown's key must be 'title'!")
            text = markdown.get("text")
            if not text:
                raise ValidationError("markdown's key must be 'text'!")
        except json.decoder.JSONDecodeError:
            raise ValidationError("markdown's type must be json!")

    @validates("link")
    def validate_link(self, value):
        try:
            link = json.loads(value)
            title = link.get("title")
            if not title:
                raise ValidationError("link's key must be 'title'!")
            text = link.get("text")
            if not text:
                raise ValidationError("link's key must be 'text'!")
            url = link.get("url")
            if not url:
                raise ValidationError("link's key must be 'url'!")
        except json.decoder.JSONDecodeError:
            raise ValidationError("link's type must be json!")
