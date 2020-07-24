from functools import wraps

from flask import request
from pydantic import ValidationError, create_model

ARG_LOCATIONS = {
    "query": lambda: request.args,
    "json": lambda: request.get_json(),
    "form": lambda: request.form,
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
    props = schema.get("properties", {})
    required = schema.get("required", [])

    for k in props:
        if k in required:
            props[k]["required"] = True
        props[k]["in"] = location

    def decorator(func):
        # Inject parameters information into the Flask-Restx apidoc attribute.
        # Not really a good solution. See https://github.com/CTFd/CTFd/issues/1504
        apidoc = getattr(func, "__apidoc__", {"params": {}})
        apidoc["params"].update(props)
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
