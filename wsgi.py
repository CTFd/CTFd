import os

# Detect if we're running via `flask run` and don't monkey patch
if not os.getenv("FLASK_RUN_FROM_CLI"):
    from gevent import monkey

    monkey.patch_all()

from CTFd import create_app

app = create_app()


# Backwards compatible host header injection vulnerability fix
import re
from flask import request, abort

# TODO this would have to be added to configuration settings available to user for this to be functional
ALLOWED_HOSTS = app.config.get("ALLOWED_HOSTS")  # eg ["yourdomain.com", "192.0.2.1"]
ALLOWED_PROXIES = app.config.get("ALLOWED_PROXIES")  # eg ["127.0.0.1", "192.0.2.1"]

# Regex to block insecure local hostnames
BLOCKED_HOST_REGEX = re.compile(r"^(localhost|127\.0\.0\.1|0\.0\.0\.0|::1|local)$", re.IGNORECASE)

@app.before_request
def strict_host_protection():
    # If ALLOWED_HOSTS is not configured skip strict host checking to allow unconfigured instances to still function.
    if not ALLOWED_HOSTS:
        return

    host = request.headers.get("Host", "").split(":")[0]
    forwarded_host = request.headers.get("X-Forwarded-Host", "").split(":")[0]
    remote_addr = request.remote_addr
    forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    real_ip = forwarded_for if forwarded_for else remote_addr

    if forwarded_host:
        if forwarded_host not in ALLOWED_HOSTS:
            print(f"[SECURITY] Blocked forwarded host: {forwarded_host} from {real_ip}")
            abort(400)
    else:
        if ALLOWED_PROXIES and remote_addr in ALLOWED_PROXIES:
            if BLOCKED_HOST_REGEX.match(host) or host not in ALLOWED_HOSTS:
                print(f"[SECURITY] Blocked host: {host} from {real_ip}")
                abort(400)
        else:
            if host not in ALLOWED_HOSTS:
                print(f"[SECURITY] Blocked host: {host} from {real_ip}")
                abort(400)

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host="127.0.0.1", port=4000)

