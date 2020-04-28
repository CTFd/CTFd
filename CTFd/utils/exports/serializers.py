import json
import six
from collections import defaultdict, OrderedDict
from datetime import datetime, date
from decimal import Decimal


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)


class JSONSerializer(object):
    def __init__(self, query, fileobj):
        self.query = query
        self.fileobj = fileobj
        self.buckets = defaultdict(list)

    def serialize(self):
        for row in self.query:
            self.write(None, row)
        self.close()

    def write(self, path, result):
        self.buckets[path].append(result)

    def wrap(self, result):
        result = OrderedDict(
            [("count", len(result)), ("results", result), ("meta", {})]
        )
        return result

    def close(self):
        for path, result in self.buckets.items():
            result = self.wrap(result)

            # Certain databases (MariaDB) store JSON as LONGTEXT.
            # Before emitting a file we should standardize to valid JSON (i.e. a dict)
            # See Issue #973
            for i, r in enumerate(result["results"]):
                data = r.get("requirements")
                if data:
                    try:
                        if isinstance(data, six.string_types):
                            result["results"][i]["requirements"] = json.loads(data)
                    except ValueError:
                        pass

            data = json.dumps(result, cls=JSONEncoder, separators=(",", ":"))
            self.fileobj.write(data.encode("utf-8"))
