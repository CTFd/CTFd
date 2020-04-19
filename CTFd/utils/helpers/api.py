from enum import Enum


class APITypes(str, Enum):
    STRING = "string"
    INT = "int"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


OPENAPI_TYPE_MAPPING = {
    "String": APITypes.STRING,
    "Int": APITypes.INT,
    "DelimitedList": APITypes.STRING,
}


def build_endpoint_docs(args):
    docs = {}
    for k, v in args.items():
        docs[k] = {
            "description": v.metadata.get("doc", ""),
            "type": OPENAPI_TYPE_MAPPING.get(type(v).__name__),
        }
    return docs
