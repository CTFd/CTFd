import os

# Detect if we're running via `flask run` and don't monkey patch
if not os.getenv("FLASK_RUN_FROM_CLI"):
    from gevent import monkey

    monkey.patch_all()

from CTFd import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host="127.0.0.1", port=4000)
