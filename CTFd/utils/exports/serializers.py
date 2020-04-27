import json
import six
from collections import OrderedDict

from CTFd.utils.exports.encoders import JSONEncoder


class JSONSerializer(object):
    def __init__(self, query, fileobj):
        self.query = query
        self.fileobj = fileobj
        self.buckets = []

    def serialize(self):
        for row in self.query:
            self.write(None, row)
        self.close()

    def write(self, path, result):
        self.buckets.append([result])

    def wrap(self, result):
        result = OrderedDict([("count", len(result)), ("results", result)])
        result["meta"] = {}
        return result

    def close(self):
        for result in self.buckets:
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

            data = json.dumps(result, cls=JSONEncoder, indent=2)
            self.fileobj.write(data.encode("utf-8"))
