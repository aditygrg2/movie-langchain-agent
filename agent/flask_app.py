from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS


# CLIENT_URL = "http://localhost:3000"
CLIENT_URL = "https://movie-langchain-agent.vercel.app"

app = Flask(__name__)
CORS(app=app, origins=[CLIENT_URL])
socketio = SocketIO(app, cors_allowed_origins=[CLIENT_URL], engineio_logger=True, ping_timeout=5, ping_interval=5)
