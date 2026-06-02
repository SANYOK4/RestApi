from marshmallow import Schema, fields, validate


class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    author = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str(load_default=None)
    year = fields.Int(required=True, validate=validate.Range(min=1, max=2100))


class BookPageSchema(Schema):
    items = fields.List(fields.Nested(BookSchema))
    total = fields.Int()
    limit = fields.Int()
    offset = fields.Int()


book_schema = BookSchema()
books_page_schema = BookPageSchema()