import weaviate
import os
from dotenv import load_dotenv
load_dotenv(".env.local")  # asegúrate de cargar tu archivo correcto

client = weaviate.Client(
    url="https://TU-CLUSTER.weaviate.network",
    auth_client_secret=weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))
)
