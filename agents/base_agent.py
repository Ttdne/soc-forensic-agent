# multi_agent_system/agents/base_agent.py
from abc import ABC, abstractmethod
from config.settings import get_llm, get_llm_plan
import os 

class BaseAgent(ABC):
    PROMPT_DIR = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'roles')
    def __init__(self):
        self.llm = get_llm()
        self.llm_plan = get_llm_plan()


    def call_llm(self, system_prompt: str, user_input: str) -> str:
        return self.llm(system_prompt = system_prompt, user_input =  user_input )

    @abstractmethod
    def run(self, input_data: str) -> dict:
        pass