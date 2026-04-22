from marshmallow import Schema, ValidationError, fields, validates


class SendAlarmMailSchema(Schema):
    mail_type = fields.Str(required=True)
    send_to = fields.List(fields.Str(required=True))
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    service_name = fields.Str(required=True)
    service_type = fields.Str(required=True)
    token = fields.Str(required=True)
    same_alarm_inter = fields.Integer(required=True)

    @validates("mail_type")
    def vaildata_mail_type(self, value):
        if value not in ["zheng", "peng"]:
            raise ValidationError("mail type error!")

    @validates("send_to")
    def validate_send_to(self, value):
        if not value:
            raise ValidationError("send to not empty!")
        for staff in value:
            if staff.find(".") == -1:
                raise ValidationError("send to error!")

    @validates("title")
    def validate_title(self, value):
        if not value.strip():
            raise ValidationError("title not empty!")

    @validates("content")
    def validate_content(self, value):
        if not value.strip():
            raise ValidationError("content not empty!")
