# This file is no longer used. If you're importing the function from here please update your imports

from CTFd.utils.helpers.models import build_model_filters as _build_model_filters


def build_model_filters(model, query, field):
    print("CTFd.api.v1.helpers.models.build_model_filters has been deprecated.")
    print("Please switch to using CTFd.utils.helpers.models.build_model_filters")
    print(
        "This function will raise an exception in a future minor release of CTFd and then be removed in a major release."
    )
    return _build_model_filters(model, query, field)
