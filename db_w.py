import os
import weaviate
from weaviate.auth import AuthApiKey
from dotenv import load_dotenv


load_dotenv(".env.local")

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")


client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=AuthApiKey(weaviate_api_key),
)

print(client.is_ready())  


client.close()
