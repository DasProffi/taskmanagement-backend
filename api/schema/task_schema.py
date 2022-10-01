from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from api.util.enums import ProgressState


class TaskSchema(Schema):
    last_updated_by = fields.Str()
    due_date = fields.DateTime()
    updated_at = fields.DateTime()
    id = fields.Number()
    name = fields.Str()
    time_estimate_sec = fields.Integer()
    created_at = fields.DateTime()
    description = fields.Str()
    priority = fields.Integer()
    progress_state = EnumField(ProgressState, by_value=True)
    email = fields.Str()
