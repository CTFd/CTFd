from functools import wraps

from flask import request
from pydantic import Extra, ValidationError, create_model

ARG_LOCATIONS = {
    "query": lambda: request.args,
    "json": lambda: request.get_json(),
    "formData": lambda: request.form,
    "headers": lambda: request.headers,
    "cookies": lambda: request.cookies,
}


def expects_args(spec, location, allow_extras=False, pass_args=False, validate=False):
    """
    A decorator that expects parameters to be passed into a endpoint according to the pydantic spec.

    :param spec: A pydantic model or a dictionary that will be used to create a pydantic model
    :param str location: The location of the parameters to be passed. Can be one of "json", "query", "form", "headers", "cookies"
    :param bool allow_extras: Whether to allow extra parameters to be passed
    :param bool pass_args: Whether to pass the parameters as an argument to the function
    :param bool validate: Whether to validate the parameters before passing them to the function

    :return: A decorator that will inject the parameters into the function

    Example:

    .. code-block:: python

        @expects_args({"name": (str, None), "id": (int, None)}, location="query")
        def my_route(query_args):
            return {"success": True, "name": query_args["name"], "id": query_args["id"]}

    """
    if isinstance(spec, dict):
        spec = create_model("", **spec)
    else:
        # We have to make a copy in order to not overwrite the original config
        spec = create_model("", __base__=spec)

    if allow_extras:
        spec.__config__.extra = Extra.allow

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

            if validate:
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
            else:
                loaded = data

            if pass_args:
                return func(*args, loaded, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_args(spec, location, allow_extras=False, pass_args=True):
    """
    Validate and load arguments according to a pydantic spec.

    :param spec: A pydantic model or a dictionary of fields.
    :param location: A string indicating where to find the arguments. Can be one of "json", "query", "form", "headers", "cookies"
    :param allow_extras: Whether to allow extra arguments not defined in the spec.
    :return: A decorator that validates and loads arguments according to the spec.

    Example usage:

    .. code-block:: python

        @validate_args({"name": (str, None), "id": (int, None)}, location="query")
        def my_route(query_args):
            return {"success": True, "name": query_args["name"], "id": query_args["id"]}
    """
    return expects_args(spec, location, allow_extras, pass_args, validate=True)
