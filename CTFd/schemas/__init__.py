from apispec.ext.marshmallow.openapi import OpenAPIConverter
from flask_restx import Model, fields, marshal_with

Converter = OpenAPIConverter("3.0", schema_name_resolver=lambda: None, spec=None)


def JSONSchema(schema):
    return Converter.schema2jsonschema(schema)
