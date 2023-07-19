from typing import Any, Dict, List, Optional

from marshmallow import Schema, fields
class APISimpleSuccessResponse(Schema):
    success: bool = fields.Bool(default=True)


class APIDetailedSuccessResponse(APISimpleSuccessResponse):
    data: Optional[Any] = fields.Raw()


class APIListSuccessResponse(APIDetailedSuccessResponse):
    data: Optional[List[Any]] = fields.List(fields.Raw())


class PaginationMetadataSchema(Schema):
    page: int = fields.Int()
    next: int = fields.Int()
    prev: int = fields.Int()
    pages: int = fields.Int()
    per_page: int = fields.Int()
    total: int = fields.Int()

class PaginationSchema(Schema):
    pagination: PaginationMetadataSchema = fields.Nested(PaginationMetadataSchema)

class PaginatedAPIListSuccessResponse(APIListSuccessResponse):
    meta: Dict[str, Any] = PaginationSchema

class APISimpleErrorResponse(Schema):
    success: bool = fields.Bool(default=False)
    errors: Optional[List[str]] = fields.List(fields.String())

class StatusMessageSchema(Schema):
    status: str = fields.String()
    message: Optional[str] = fields.String()

class APIStatusMessageResponse(APISimpleSuccessResponse):
    data = fields.Nested(StatusMessageSchema)