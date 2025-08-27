import os
os.environ['http_proxy'] = "192.168.5.8:3128"
os.environ['https_proxy'] = "192.168.5.8:3128"

print("http_proxy:", os.environ.get('http_proxy'))
print("https_proxy:", os.environ.get('https_proxy'))


from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Bạn là một trợ lý AI."},
        {"role": "user", "content": "Xin chào, bạn có khỏe không?"}
    ],
)

print(response.choices[0].message.content)