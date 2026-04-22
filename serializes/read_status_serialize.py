from marshmallow import Schema, ValidationError, fields, validates, validates_schema


class SingleSchema(Schema):
    processQueryKey = fields.Str(required=True)

    def validate_processQueryKey(self, value):
        if not value.strip():
            raise ValidationError("processQueryKey not empty!")


class Groupchema(Schema):
    groupid = fields.Str(required=True)
    processQueryKey = fields.Str(required=True)

    def validate_processQueryKey(self, value):
        if not value.strip():
            raise ValidationError("processQueryKey not empty!")


class ReadStatusSchema(Schema):
    type = fields.Str(required=True)
    single = fields.Nested(SingleSchema)
    group = fields.Nested(Groupchema)

    @validates("type")
    def validate_type(self, value):
        if value not in ["single", "group"]:
            raise ValidationError("type error!")

    @validates_schema
    def validate_type_key(self, data, **kwargs):
        if not data.get(data["type"]):
            raise ValidationError("type and parameter value validation failed!")
