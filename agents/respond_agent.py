import os
import json
from agents.base_agent import BaseAgent

class RespondAgent(BaseAgent):
    def __init__(self, state_file_path: str):
        super().__init__()
        self.state_file_path = state_file_path

    def _read_state(self):
        if not os.path.exists(self.state_file_path):
            return {}
        with open(self.state_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def respond(self, user_request: str) -> dict:
        state = self._read_state()

        # Build history context from state
        context = ""
        for key, value in state.items():
            context += f"[{key}]: {value}\n"

        system_prompt = (
            f"You are an assistant helping to summarize and respond based on planning steps.\n"
            f"Context:\n{context}\n"
        )

        user_input = (
            f"User request: {user_request}\n"
            f"Answer accordingly:"
        )

        # Call LLM (using the inherited method from BaseAgent)
        response = self.call_llm(system_prompt = system_prompt, user_input = user_input)
        return response

    def run(self, user_request: str) -> dict:
        return self.respond(user_request)
