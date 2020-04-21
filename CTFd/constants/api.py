from CTFd.constants import RawEnum


class APITypes(str, RawEnum):
    STRING = "string"
    INT = "int"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


OPENAPI_TYPE_MAPPING = {
    "String": APITypes.STRING,
    "Integer": APITypes.INT,
    "Boolean": APITypes.BOOLEAN,
    "DelimitedList": APITypes.STRING,
}
