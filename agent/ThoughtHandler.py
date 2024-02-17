from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction
from typing import Any


class ThoughtHandler(BaseCallbackHandler):
    def __init__(self, socketio):
        super().__init__()
        self.socket = socketio
        self.vec = []

    def on_agent_action(self, action: AgentAction, **kwargs):
        self.socket.emit('agent_log', str(action))
        self.vec.append(action)

    def get_vec(self):
        return self.vec
