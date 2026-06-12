import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "Hello, test connection."}
    ]
}

resp = requests.post("https://api.deepseek.com/v1/chat/completions", json=data, headers=headers)

print("Status:", resp.status_code)
print("Response:", resp.text)
