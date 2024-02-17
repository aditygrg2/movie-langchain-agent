from flask import Flask
from flask_socketio import SocketIO

CLIENT_URL = "http://localhost:3000"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=[CLIENT_URL])
