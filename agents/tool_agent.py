# File: agents/tool_agent.py

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from config import custom_function
from agents.guard_agent.guard_agent import GuardAgent   
from toolkits.loader import load_toolkit_plugins
from toolkits.plugins.message_ask_user.schema import MessageAskUserParams
from toolkits.plugins.message_notify_user.schema import MessageNotifyUserParams
from toolkits.plugins.confluence_download.schema import ConfluenceDownloadParams
from toolkits.plugins.documents_extract_comment.schema import DocumentsExtractCommentParams
from toolkits.plugins.docx_fill.schema import DocxFillParams
from toolkits.plugins.file_get_sample_lines.schema import FileGetSampleNLinesParams
from toolkits.plugins.file_read.schema import FileReadParams
from toolkits.plugins.execute_python.schema import ExecutePythonParams
from toolkits.plugins.count_file_line.schema import CountFileLineParams
from toolkits.plugins.command_line.schema import CommandLineParams
import yaml
# Config OpenAI
load_dotenv()

#PROXY = "http://192.168.5.8:3128"
MODEL_NAME = os.getenv("MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROMPT_DIR = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'roles')

PLUGIN_CONFIG = {
    "file_read": FileReadParams,
    # "file_write": FileWriteParams,
    #"command_line": CommandLineParams,
    #"message_ask_user":MessageAskUserParams,
    "message_notify_user":MessageNotifyUserParams,
    # "confluence_download": ConfluenceDownloadParams,
    # "documents_extract_comment":DocumentsExtractCommentParams,
    # "docx_fill":DocxFillParams
    #"calculator": CalculatorParams
    "file_get_sample_lines" : FileGetSampleNLinesParams,
    "file_read": FileReadParams,
    "execute_python" : ExecutePythonParams,
    "count_file_line" : CountFileLineParams,
    "command_line" : CommandLineParams
    }

class ToolAgent:
    def __init__(self ,state_dir: str = None):
        self.plugins = load_toolkit_plugins()
        self.state_dir = state_dir
        self.plugin_metadata = {}
        role_name = "Tool_Agent"
        self.role_prompt = self.load_role_prompt(role_name)
        self.inside_tool = ["file_read"]
        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )
        # Set log_path to <state_dir>/agent_log.json if state_dir is provided
        if self.state_dir:
            log_path = os.path.join(self.state_dir, "guard_agent.json")
        else:
            log_path = None
        self.guard_agent = GuardAgent(log_path=log_path)
    def load_role_prompt(self, role_name: str) -> str:
        prompt_path = os.path.join(PROMPT_DIR, f"{role_name}.json")
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Role prompt file not found for role: {role_name}")
        with open(prompt_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data["prompt"]

    def execute(self, task_description: str):
        tools_definitions = self._build_function_schemas()
        
        #print(tools_definitions)
        response = custom_function.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": self.role_prompt},
                {"role": "user", "content": task_description}
            ],
            tools=tools_definitions,
            tool_choice="auto"
        )

        tool_calls = response.choices[0].message.tool_calls

        if not tool_calls:
            print("No tool call returned.")
            return {"stderr": "No tool call returned."}

        results = []
        for tool_call in tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            description = self.plugin_metadata[name]["description"]
            guard_res = self.guard_agent.check_tool_call(name, arguments, description)
            if guard_res["blocked"]:
                print(f"[GUARD] Blocked tool call: {guard_res}")
                return {"stderr": f"Blocked dangerous tool call: {guard_res['reason']}", "guard": guard_res}

            print(f"{name} - {arguments}")
            arguments["state_dir"] = self.state_dir
            tool = self.plugins[name]
            result = tool.execute(**arguments)
            print(f"{name} - {arguments} - {result}")
            results.append(result)
        return results if len(results) > 1 else results[0]

    def _build_function_schemas(self):
        tools = []

        for plugin_path, schema in PLUGIN_CONFIG.items():
            metadata_path = os.path.join("toolkits", "plugins", plugin_path, "metadata.yaml")
            if not os.path.exists(metadata_path):
                raise FileNotFoundError(f"Metadata file not found for plugin: {plugin_path}")
            
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = yaml.safe_load(f)
                
            tool_name = metadata.get("name")
            if not tool_name:
                raise ValueError(f"Plugin {plugin_path} does not have a 'name' field in metadata.")
            
            self.plugin_metadata[tool_name] = metadata
            tools.append({
                "type": "function",
                "function": {
                    "name": metadata.get("name"),
                    "description": metadata.get("description", "No description provided."),
                    "parameters": schema.model_json_schema()
                }
            })
        return tools
    
    # Load state từ file
    def load_state(self, state_file):
        if os.path.exists(state_file):
            try:
                with open(state_file, "r", encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load state.json: {e}")
        return {}

    # Ghi state ra file
    def save_state(self, state, state_file):
        try:
            with open(state_file, "w", encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to save state.json: {e}")

    def execute_loop(self, task_description: str):
        tools_definitions = self._build_function_schemas()
        
        state_file = os.path.join(self.state_dir, "state.json")
        tool_call_file = os.path.join(self.state_dir, "toolcall.log")


        results = []
        # Load public state ban đầu
        public_state = self.load_state(state_file)

        context_prompt = f"""Kết quả các bước làm việc trước
            {json.dumps(public_state, ensure_ascii=False, indent=2)} 
        """

        messages = [
            {"role": "system", "content": self.role_prompt},
            {"role": "user", "content": f"Mục tiêu : {task_description}" }
            , {"role": "system", "content": context_prompt}
        ]
        
        MAX_STEPS = 15
        local_state = public_state.copy()
        for step in range(MAX_STEPS):
            response = custom_function.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools_definitions,
                tool_choice="auto",
                temperature=0.5

            )

            message = response.choices[0].message
            tool_calls = response.choices[0].message.tool_calls
            if not tool_calls:
                print(f"No tool call returned. message:  {message}")
                break

            tool_call = tool_calls[0]
            print(tool_call)
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            description = self.plugin_metadata[name]["description"]
            guard_res = self.guard_agent.check_tool_call(name, arguments, description)
            if guard_res["blocked"]:
                print(f"[GUARD] Blocked tool call: {guard_res}")
                return {"stderr": f"Blocked dangerous tool call: {guard_res['reason']}", "guard": guard_res}
            print(f"[STEP {step}] Calling tool `{name}` with arguments: {arguments}")
            arguments["state_dir"] = self.state_dir

            tool = self.plugins[name]
            result = tool.execute(**arguments)
            with open(tool_call_file, "a", encoding='utf-8') as toolcall_file:
                tool_call_save = {f"tool_call_{step}" : tool_call, "result": result}
                toolcall_file.writelines(str(tool_call_save) + "\n")




            print(f"[STEP {step}] Tool `{name}` executed with result: {result}")

            # Cập nhật local_state nếu có kết quả mới
            if name not in self.inside_tool:
                results.append(result)

            # Cập nhật messages để duy trì context
            messages.append({
                "role": "assistant",
                "tool_calls": [tool_call]
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        return results if len(results) > 0 else "No tool call returned."