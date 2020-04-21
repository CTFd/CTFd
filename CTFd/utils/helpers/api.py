from CTFd.constants.api import OPENAPI_TYPE_MAPPING


def build_endpoint_docs(args):
    docs = {}
    for k, v in args.items():
        docs[k] = {
            "description": v.metadata.get("doc", ""),
            "type": OPENAPI_TYPE_MAPPING.get(type(v).__name__),
        }
    return docs
