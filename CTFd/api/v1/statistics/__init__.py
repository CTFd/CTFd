from flask_restplus import Namespace

statistics_namespace = Namespace(
    "statistics", description="Endpoint to retrieve Statistics"
)

from CTFd.api.v1.statistics import challenges  # noqa: F401
from CTFd.api.v1.statistics import teams  # noqa: F401
from CTFd.api.v1.statistics import users  # noqa: F401
from CTFd.api.v1.statistics import submissions  # noqa: F401
