import os
import requests
from dotenv import load_dotenv

load_dotenv("env.local")  # asegúrate de cargar tu archivo correcto

def preguntar_chatbot(question: str, session_id: str = "testing-https-prod"):
    url = os.getenv("URL")
    headers = {
        "Content-Type": os.getenv("CONTENT_TYPE"),
        "Authorization": os.getenv("AUTHORIZATION")
    }
    payload = {
        "question": question,
        "chat_history": [],
        "session_id": session_id
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    return data.get("answer", str(data))
