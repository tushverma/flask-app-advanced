from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage


class FileStorageField(fields.Field):
    default_error_messages = {"invalid": "Not a valid image."}

    def _deserialize(self, value, attr, data) -> FileStorage:
        if value is None:
            return None
        if not isinstance(value, FileStorage):
            self.fail("invalid")  # raise Validation Error
        return value


class ImageSchema(Schema):
    image = FileStorageField(required=True)
