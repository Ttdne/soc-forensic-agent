import os
import json
import uuid
from datetime import datetime
from agents.base_agent import BaseAgent
from agents.tool_agent import ToolAgent
from agents.respond_agent import RespondAgent

PROMPT_DIR = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'roles')

class PlanAgent(BaseAgent):
    def __init__(self, depth=0, pin=None, role_name="Product_Owner", state_dir=None):
        super().__init__()
        self.depth = depth
        self.pin = pin or []
        self.max_depth = 3
        self.role_name = role_name

        if state_dir is None:
            state_id = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4()}"
            self.state_dir = f"./test_environment/{state_id}"
            os.makedirs(self.state_dir, exist_ok=True)
            self.state_file_path = f"{self.state_dir}/state.json"
            self._write_state({"plan": {}})
        else:
            self.state_dir = state_dir
            self.state_file_path = f"{self.state_dir}/state.json"

    def load_role_prompt(self, role_name: str) -> str:
        prompt_path = os.path.join(PROMPT_DIR, f"{role_name}.json")
        if not os.path.exists(prompt_path):
            role_name = "Product_Owner"
            prompt_path = os.path.join(PROMPT_DIR, f"{role_name}.json")
        with open(prompt_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data["prompt"]

    def plan_steps(self, role_prompt, user_request):
        state = self._read_state()
        context_prompt = f"""Kết quả các bước làm việc trước\n{json.dumps(state, ensure_ascii=False, indent=2)}"""
        messages = [
            {"role": "system", "content": role_prompt},
            {"role": "user", "content": user_request},
            {"role": "system", "content": context_prompt}
        ]
        llm_response = self.llm_plan(messages=messages)
        return llm_response.get("steps", llm_response)

    def execute(self, role_name: str, user_request: str, path=""):
        state = self._read_state()
        state = {"user_input": user_request, **state}
        results = []
        if self.depth >= self.max_depth:
            tool_agent = ToolAgent(state_dir=self.state_dir)
            result = tool_agent.execute_loop(user_request)
            result = {"description": user_request, **result} if isinstance(result, dict) else {"description": user_request, "action": result}
            self._update_nested_state(state["plan"], path + ".result", result)
            self._update_nested_state(state["plan"], path + ".status", "completed")
            self._write_state(state)
            return {"result": [result]}

        role_prompt = self.load_role_prompt(role_name)
        steps = self.plan_steps(role_prompt, user_request)

        for idx, step in enumerate(steps):
            step_key = f"step_{idx}"
            child_path = f"{path}.children.{step_key}" if path else step_key
            step_meta = {
                "description": step["description"],
                "type": step["type"],
                "agent": step.get("agent"),
                "status": "pending",
                "children": {}
            }
            self._set_nested_state(state["plan"], child_path, step_meta)

        self._write_state(state)

        for idx, step in enumerate(steps):
            step_key = f"step_{idx}"
            child_path = f"{path}.children.{step_key}" if path else step_key

            self._update_nested_state(state["plan"], child_path + ".status", "running")
            self._write_state(state)

            if step["type"] == "tool" or step.get("agent") == "ToolAgent":
                agent = ToolAgent(state_dir=self.state_dir)
                result = agent.execute_loop(step["description"])
            elif step["type"] == "respond":
                agent = RespondAgent(state_file_path=self.state_file_path)
                result = agent.respond(step["description"])
            elif step["type"] == "plan":
                agent = PlanAgent(
                    depth=self.depth + 1,
                    role_name=step["agent"],
                    state_dir=self.state_dir,
                    pin=self.pin + [idx]
                )
                result = agent.run(step["description"], path=child_path)["result"]
            else:
                raise ValueError(f"Unknown step type: {step['type']}")

            step_result = {"description": step["description"], **result} if isinstance(result, dict) else {"description": step["description"], "action": result}
            self._update_nested_state(state["plan"], child_path + ".result", step_result)
            self._update_nested_state(state["plan"], child_path + ".status", "completed")
            self._write_state(state)
            results.append(step_result)

        return {"result": results}

    def run(self, input_data: str, path="") -> dict:
        return self.execute(self.role_name, input_data, path=path)

    def _read_state(self):
        if not os.path.exists(self.state_file_path):
            return {"plan": {}}
        with open(self.state_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_state(self, state: dict):
        with open(self.state_file_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _set_nested_state(self, root, path, value):
        keys = path.split(".")
        current = root
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def _update_nested_state(self, root, path, value):
        keys = path.split(".")
        current = root
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
