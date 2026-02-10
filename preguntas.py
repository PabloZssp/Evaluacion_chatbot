import os
import requests
from dotenv import load_dotenv
load_dotenv(".env.local")

url = os.getenv("URL")
headers = {
    "Content-Type": os.getenv("CONTENT_TYPE"),
    "Authorization": os.getenv("AUTHORIZATION")
}
payload = {
    "question": "Que eventos hay en febrero",
    "chat_history": [],
    "session_id": "testing-https-prod"
}

response = requests.post(url, headers=headers, json=payload)

# Imprime la respuesta del servidor
print("Status code:", response.status_code)
print("Respuesta JSON:", response.json())
