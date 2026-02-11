import os
from dotenv import load_dotenv

load_dotenv(".env.local")

print("--- DIAGNÓSTICO DE VARIABLES ---")
print(f"URL cargada: {os.getenv('URL')}")
print(f"API KEY cargada: {'Sí' if os.getenv('CONFIDENT_API_KEY') else 'No'}")
print("--------------------------------")