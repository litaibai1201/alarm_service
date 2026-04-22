from marshmallow import Schema, fields


class RspMsgSchema(Schema):
    code = fields.Str(required=True)
    msg = fields.Str(required=True)
    content = fields.Dict()


class RspRegistrationSchema(Schema):
    code = fields.Str(required=True)
    msg = fields.Str(required=True)
    content = fields.List(fields.Dict())
