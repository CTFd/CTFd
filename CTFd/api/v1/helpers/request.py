from functools import wraps

from flask import request
from pydantic import ValidationError, create_model

ARG_LOCATIONS = {
    "query": lambda: request.args,
    "json": lambda: request.get_json(),
    "formData": lambda: request.form,
    "headers": lambda: request.headers,
    "cookies": lambda: request.cookies,
}


def validate_args(spec, location):
    """
    A rough implementation of webargs using pydantic schemas. You can pass a
    pydantic schema as spec or create it on the fly as follows:

    @validate_args({"name": (str, None), "id": (int, None)}, location="query")
    """
    if isinstance(spec, dict):
        spec = create_model("", **spec)

    schema = spec.schema()

    defs = schema.pop("definitions", {})
    props = schema.get("properties", {})
    required = schema.get("required", [])

    # Remove all titles and resolve all $refs in properties
    for k in props:
        if "title" in props[k]:
            del props[k]["title"]

        if "$ref" in props[k]:
            definition: dict = defs[props[k].pop("$ref").split("/").pop()]

            # Check if the schema is for enums, if so, we just add in the "enum" key
            # else we add the whole schema into the properties
            if "enum" in definition:
                props[k]["enum"] = definition["enum"]
            else:
                props[k] = definition

    def decorator(func):
        # Inject parameters information into the Flask-Restx apidoc attribute.
        # Not really a good solution. See https://github.com/CTFd/CTFd/issues/1504
        nonlocal location

        apidoc = getattr(func, "__apidoc__", {"params": {}})

        if location == "form":
            location = "formData"

            if any(v["type"] == "file" for v in props.values()):
                apidoc["consumes"] = ["multipart/form-data"]
            else:
                apidoc["consumes"] = [
                    "application/x-www-form-urlencoded",
                    "multipart/form-data",
                ]

        if location == "json":
            title = schema.get("title", "")
            apidoc["consumes"] = ["application/json"]
            apidoc["params"].update({title: {"in": "body", "schema": schema}})
        else:
            for k, v in props.items():
                v["in"] = location

                if k in required:
                    v["required"] = True

                apidoc["params"][k] = v

        func.__apidoc__ = apidoc

        @wraps(func)
        def wrapper(*args, **kwargs):
            data = ARG_LOCATIONS[location]()
            try:
                # Try to load data according to pydantic spec
                loaded = spec(**data).dict(exclude_unset=True)
            except ValidationError as e:
                # Handle reporting errors when invalid
                resp = {}
                errors = e.errors()
                for err in errors:
                    loc = err["loc"][0]
                    msg = err["msg"]
                    resp[loc] = msg
                return {"success": False, "errors": resp}, 400
            return func(*args, loaded, **kwargs)

        return wrapper

    return decorator
