from marshmallow import Schema, ValidationError, fields, validates, validates_schema


class TextSchema(Schema):
    content = fields.Str(required=True)
    isatall = fields.Bool()
    atuserids = fields.List(fields.Str())

    @validates("content")
    def validate_content(self, value):
        if not value.strip():
            raise ValidationError("content not empty!")
        if len(value) > 1300:
            raise ValidationError("content must be no more than 1300 words!")
        if value.count("\n") > 30:
            raise ValidationError("content must be no more than 30 lines!")


class LinkSchema(Schema):
    message_url = fields.Str(required=True)
    title = fields.Str(required=True)
    text = fields.Str(required=True)

    @validates("message_url")
    def validate_message_url(self, value):
        if not str(value).startswith("http"):
            raise ValidationError("message url error!")

    @validates("text")
    def validate_text(self, value):
        if not value.strip():
            raise ValidationError("text not empty!")

    @validates("title")
    def validate_title(self, value):
        if not value.strip():
            raise ValidationError("title not empty!")


class AtuseridsSchema(Schema):
    at = fields.List(fields.Str())
    after_at_msg = fields.Str()
    cc = fields.List(fields.Str())


class MarkdownSchema(Schema):
    title = fields.Str(required=True)
    text = fields.Str(required=True)
    atuserids = fields.Nested(AtuseridsSchema)


class SendAlarmGroupMsgSchema(Schema):
    webhook = fields.Str(required=True)
    type = fields.Str(required=True)
    service_name = fields.Str(required=True)
    service_type = fields.Str(required=True)
    token = fields.Str(required=True)
    text = fields.Nested(TextSchema)
    link = fields.Nested(LinkSchema)
    markdown = fields.Nested(MarkdownSchema)
    same_alarm_inter = fields.Integer(required=True)

    @validates("webhook")
    def validate_webhook(self, value):
        if not str(value).startswith("http://10.182.179.113:8081/"):
            raise ValidationError("webhook error!")

    @validates("type")
    def validate_type(self, value):
        if value not in ["text", "link", "markdown"]:
            raise ValidationError("type error!")

    @validates_schema
    def validate_type_key(self, data, **kwargs):
        if not data.get(data["type"]):
            raise ValidationError("type and parameter value validation failed!")
