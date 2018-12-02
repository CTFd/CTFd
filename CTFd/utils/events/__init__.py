from flask_socketio import SocketIO

# The choice to use threading is intentional to simplify deployment.
# At the moment it is not recommended to build full-duplex systems inside CTFd.
socketio = SocketIO()
