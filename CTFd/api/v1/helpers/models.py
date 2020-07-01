def build_model_filters(model, query, field):
    filters = []
    if query:
        # The field exists as an exposed column
        if model.__mapper__.has_property(field):
            filters.append(getattr(model, field).like("%{}%".format(query)))
    return filters
