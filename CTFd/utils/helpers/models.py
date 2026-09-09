import sqlalchemy


def _build_column_filter(column, query):
    if type(column.type) == sqlalchemy.sql.sqltypes.Integer:
        try:
            query = int(query)
        except (TypeError, ValueError):
            return sqlalchemy.sql.false()
        return column.op("=")(query)
    return column.like(f"%{query}%")


def build_model_filters(model, query, field, extra_columns=None):
    if extra_columns is None:
        extra_columns = {}
    filters = []
    if query:
        # The field exists as an exposed column
        if model.__mapper__.has_property(field):
            column = getattr(model, field)
            filters.append(_build_column_filter(column=column, query=query))
        else:
            if field in extra_columns:
                column = extra_columns[field]
                filters.append(_build_column_filter(column=column, query=query))
    return filters
