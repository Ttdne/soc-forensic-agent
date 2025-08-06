# multi_agent_system/config/settings.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import httpx
from config import custom_function

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

# def create_openai_client():
#     custom_transport = httpx.HTTPTransport(verify=False, proxy=PROXY)
#     custom_client = httpx.Client(transport=custom_transport)
#     client = OpenAI(
#         api_key=OPENAI_API_KEY,
#         http_client=custom_client
#     )
#     return client


def get_llm_plan():
    # client = create_openai_client()
    function_definitions = [
        {
            "name": "return_step_list",
            "description": "Trả về danh sách các bước hành động với loại bước, mô tả và agent phụ trách.",
            "parameters": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "description": "Danh sách các bước cần thực hiện",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["plan", "tool"],
                                    "description": "Loại bước: lên kế hoạch hoặc gọi công cụ, nếu câu hỏi có thể trả lời luôn thì sử dụng tool để phản hồi"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Giải thích chi tiết bước này cần làm gì"
                                },
                                "agent": { 
                                    "type": "string",
                                    "description": "Tên agent chịu trách nhiệm thực hiện bước này"
                                }
                            },
                            "required": ["type", "description", "agent"]
                        }
                    }
                },
                "required": ["steps"]
            }
        }
    ]

    def call(system_prompt: str = "", user_input: str = "", messages: list = []) -> dict:
        if len(messages) == 0:
            response = custom_function.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                functions=function_definitions,
                function_call={"name": "return_step_list"},
                temperature=0.5,
                max_tokens=4096,
            )
            print(response.choices[0].message.function_call.arguments)
            try:
                return json.loads(response.choices[0].message.function_call.arguments)
            except json.JSONDecodeError:
                return {"respond": response}
        else:
            response = custom_function.create(
                model=MODEL_NAME,
                messages=messages,
                functions=function_definitions,
                function_call={"name": "return_step_list"},
                temperature=0.7,
                max_tokens=4096,
            )
            print(response.choices[0].message.function_call.arguments)
            try:
                return json.loads(response.choices[0].message.function_call.arguments)
            except json.JSONDecodeError:
                return {"respond": response}

    return call
        

def get_llm():
    # client = create_openai_client()

    def call(system_prompt: str, user_input: str) -> dict:
        response = custom_function.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=4096,

        )
        try:
            return {"respond": response.choices[0].message.content.strip()}
        except json.JSONDecodeError:
            return {"respond": response}

    return call