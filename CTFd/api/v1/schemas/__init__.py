from typing import Any, List, Optional

from pydantic import BaseModel


class APISimpleSuccessResponse(BaseModel):
    success: bool = True


class APIDetailedSuccessResponse(APISimpleSuccessResponse):
    data: Optional[Any]

    @classmethod
    def apidoc(cls):
        """
        Helper to inline references from the generated schema
        """
        schema = cls.schema()

        try:
            key = schema["properties"]["data"]["$ref"]
            ref = key.split("/").pop()
            definition = schema["definitions"][ref]
            schema["properties"]["data"] = definition
            del schema["definitions"][ref]
            if bool(schema["definitions"]) is False:
                del schema["definitions"]
        except KeyError:
            pass

        return schema


class APIListSuccessResponse(APIDetailedSuccessResponse):
    data: Optional[List[Any]]

    @classmethod
    def apidoc(cls):
        """
        Helper to inline references from the generated schema
        """
        schema = cls.schema()

        try:
            key = schema["properties"]["data"]["items"]["$ref"]
            ref = key.split("/").pop()
            definition = schema["definitions"][ref]
            schema["properties"]["data"]["items"] = definition
            del schema["definitions"][ref]
            if bool(schema["definitions"]) is False:
                del schema["definitions"]
        except KeyError:
            pass

        return schema


class APISimpleErrorResponse(BaseModel):
    success: bool = False
    errors: Optional[List[str]]
