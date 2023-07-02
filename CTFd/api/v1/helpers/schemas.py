from typing import Container, Dict, Type

from pydantic import BaseModel, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty


def sqlalchemy_to_pydantic(
    db_model: Type, *, include: Dict[str, type] = None, exclude: Container[str] = None
) -> Type[BaseModel]:
    """
    Mostly copied from https://github.com/tiangolo/pydantic-sqlalchemy
    """
    if exclude is None:
        exclude = []
    mapper = inspect(db_model)
    fields = {}
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                column = attr.columns[0]
                python_type = column.type.python_type
                name = attr.key
                if name in exclude:
                    continue
                default = None
                if column.default is None and not column.nullable:
                    default = ...
                fields[name] = (python_type, default)
    if bool(include):
        for name, python_type in include.items():
            default = None
            fields[name] = (python_type, default)
    pydantic_model = create_model(db_model.__name__, **fields)  # type: ignore
    return pydantic_model
