from CTFd import create_app, socketio

app = create_app()
# app.run(debug=True, threaded=True, host="127.0.0.1", port=4000)

socketio.run(app, debug=True, host="127.0.0.1", port=4000)
