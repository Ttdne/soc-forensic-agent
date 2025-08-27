# guard_agent.py
import re
import os
import json
from openai import OpenAI
import yaml
import logging
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

# Configure logging to save logs to a file
logging.basicConfig(filename='guard_agent.log', level=logging.INFO, encoding='utf-8', format='%(asctime)s %(levelname)s %(message)s')

#PROXY = "http://192.168.5.8:3128"
MODEL_NAME = os.getenv("MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROMPT_DIR = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'roles')

class GuardAgent:
    def __init__(self, state_dir: str = None, rules_path: str = None, log_path: str = None):
        self.state_dir = state_dir or "."
        role_name = "Guard_Agent"
        self.role_prompt = self.load_role_prompt(role_name)
        self.rules_path = rules_path or os.path.join(os.path.dirname(__file__), "guard_rules.yaml")
        self.client = OpenAI(
            api_key=OPENAI_API_KEY
            )
        self.log_path = log_path or "guard_agent.log"

        # load rules
        with open(self.rules_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self.regex_block = [
            {"name": r["name"], "pattern": re.compile(r["pattern"], re.IGNORECASE), "reason": r.get("reason", "")}
            for r in cfg.get("regex_block", [])
        ]
        self.whitelist = {
            k: [re.compile(p, re.IGNORECASE) for p in v]
            for k, v in cfg.get("whitelist", {}).items()
        }

    def load_role_prompt(self, role_name):
        """Load the role prompt from a JSON file in the prompts/roles directory."""
        prompt_path = os.path.join(os.path.dirname(__file__), '..', '..', 'prompts', 'roles', f'{role_name}.json')
        prompt_path = os.path.abspath(prompt_path)
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Role prompt file not found: {prompt_path}")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def _to_check_text(self, tool_name, arguments, description):
        # Create a concise textual representation for semantic check
        
        try:
            args_text = json.dumps(arguments, ensure_ascii=False)
        except Exception:
            args_text = str(arguments)
        return f"Tool: {tool_name}, Description: {description}, Arguments: {args_text}"

    def _regex_check(self, tool_name, arguments, description):
        # Check whitelist first (if present and matches, treat as safe)
        if tool_name in self.whitelist:
            args_text = json.dumps(arguments, ensure_ascii=False)
            for pat in self.whitelist[tool_name]:
                if pat.search(args_text):
                    return {"blocked": False, "matched": "whitelist", "reason": f"Whitelisted pattern matched for {tool_name}"}

        # Check block patterns
        text = self._to_check_text(tool_name, arguments, description)
        for r in self.regex_block:
            if r["pattern"].search(text):
                return {"blocked": True, "matched": r["name"], "reason": r["reason"]}

        return {"blocked": False, "matched": None, "reason": None}

    def _semantic_check(self, tool_name, arguments, description):
        text = self._to_check_text(tool_name, arguments, description)
        try:
            # Dùng role_prompt làm system instruction
            system_instruction = None
            if isinstance(self.role_prompt, dict):
                # Nếu JSON có field "prompt" hoặc "content"
                system_instruction = self.role_prompt.get("prompt") or self.role_prompt.get("content")
            elif isinstance(self.role_prompt, str):
                system_instruction = self.role_prompt
            else:
                system_instruction = "You are a guard agent. Classify whether to BLOCK or ALLOW."

            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": text}
                ],
                temperature=0
            )

            label = response.choices[0].message.content.strip()
            print(f"Semantic check label: {label}")

            # Validate output to ensure it matches expected labels
            if not label:
                return {"blocked": True, "reason": "Semantic model returned empty label"}

            if label.lower() not in ["block", "allow"]:
                logging.warning(f"Unexpected label from semantic model: {label}")
                return {"blocked": True, "reason": f"Unexpected label: {label}"}

            if label.lower() == "block":
                return {
                    "blocked": True,
                    "reason": f"Semantic model flagged tool name {tool_name} with arguments {arguments} as dangerous",
                    "label": label
                }
            else:
                return {
                    "blocked": False,
                    "reason": f"Semantic model flagged tool name {tool_name} with arguments {arguments} as safe",
                    "label": label
                }

        except Exception as e:
            logging.error(f"Semantic check error: {e}")
            return {"blocked": True, "reason": f"Semantic check error: {e}"}


    def check_tool_call(self, tool_name, arguments, description):
        """
        Main public method used by ToolAgent.
        Returns a dict: {"blocked": bool, "reason": str, "detail": {...}}
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        # 1) fast regex check
        regex_res = self._regex_check(tool_name, arguments, description)
        if regex_res["blocked"]:
            self._audit_log(tool_name, arguments, "REGEX_BLOCK", regex_res)
            os._exit(1)  # End the process immediately after blocking
            return {"blocked": True, "reason": regex_res["reason"], "detail": {"method": "regex", **regex_res}}

        # 2) semantic check (RoBERTa)
        semantic_res = self._semantic_check(tool_name, arguments, description)
        if semantic_res["blocked"]:
            self._audit_log(tool_name, arguments, "SEMANTIC_BLOCK", semantic_res)
            os._exit(1)  # End the process immediately after blocking
            return {"blocked": True, "reason": semantic_res.get("reason", "semantic block"), "detail": {"method": "semantic", **semantic_res}}

        # allowed
        self._audit_log(tool_name, arguments, "ALLOW", {"method": "none", "regex": regex_res, "semantic": semantic_res})
        return {"blocked": False, "reason": None, "detail": {"regex": regex_res, "semantic": semantic_res}}

    def _audit_log(self, tool_name, arguments, action, meta):
        entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "tool": tool_name,
            "action": action,
            "arguments": arguments,
            "meta": meta
        }
        # Write log as JSON line to the specified log file
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
