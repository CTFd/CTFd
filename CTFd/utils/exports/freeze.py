from CTFd.utils.exports.serializers import JSONSerializer
from sqlalchemy.exc import ProgrammingError, OperationalError


def freeze_export(result, fileobj):
    try:
        query = result
        serializer = JSONSerializer(query, fileobj)
        serializer.serialize()
    except (OperationalError, ProgrammingError) as e:
        raise OperationalError("Invalid query: %s" % e)
