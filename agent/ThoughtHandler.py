from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction
from typing import Any

class ThoughtHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self.vec = []

    def on_agent_action(self, action: AgentAction):
        self.vec.append(action)

    def get_vec(self):
        return self.vec

