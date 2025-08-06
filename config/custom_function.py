# multi_agent_system/config/settings.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import httpx
from masking.masking import MaskingRule
import copy

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
PROXY = "http://192.168.5.8:3128"
# Create a custom httpx client with SSL verification disabled

custom_transport = httpx.HTTPTransport(verify=False, proxy=PROXY)
custom_client = httpx.Client(transport=custom_transport)
client = OpenAI(
    api_key= OPENAI_API_KEY,
    http_client=custom_client
)
MaskingRule = MaskingRule()

def create(model, messages, **kwargs):
    mask_maps = {}
    clone_messages = copy.deepcopy(messages)
    for item in clone_messages:
        if "content" in item.keys():
            item["content"], mask_map = MaskingRule.mask_text(item["content"], placeholder_map=mask_maps)
            mask_maps.update(mask_map)
        if "tool_calls" in item.keys():
            for i in range(0, len(item["tool_calls"])):
                text = item["tool_calls"][i].function.arguments
                item["tool_calls"][i].function.arguments, mask_map = MaskingRule.mask_text(text, placeholder_map=mask_maps)
                mask_maps.update(mask_map)

    response = client.chat.completions.create(
                model="gpt-4o",
                messages=clone_messages,
                **kwargs
            )

    if response.choices[0].message.tool_calls != None:
        for i in range(0, len(response.choices[0].message.tool_calls)):
            text = response.choices[0].message.tool_calls[i].function.arguments
            response.choices[0].message.tool_calls[i].function.arguments = MaskingRule.unmask_text(text, mask_maps)
    if response.choices[0].message.content != None:
            text = response.choices[0].message.content
            response.choices[0].message.content = MaskingRule.unmask_text(text, mask_maps)
    if response.choices[0].message.function_call != None :
            text = response.choices[0].message.function_call.arguments
            response.choices[0].message.function_call.arguments = MaskingRule.unmask_text(text, mask_maps)
    print(mask_maps)
    print(response)
    return response