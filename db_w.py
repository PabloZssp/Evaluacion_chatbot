import os
import weaviate
from weaviate.auth import AuthApiKey
from dotenv import load_dotenv
from weaviate.collections.classes.filters import Filter

# 1. Configuración
load_dotenv(".env.local")
weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_key = os.getenv("WEAVIATE_API_KEY")

# 2. Conectar a Weaviate
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=AuthApiKey(weaviate_key),
)
collection = client.collections.use("DemoCollection")

# 3. Consulta semántica simple
response = collection.query.near_text(
    query="ciudad",
    limit=5
)

print("Resultados de búsqueda:\n")
for obj in response.objects:
    print(f"- {obj.properties['title']}: {obj.properties['description']}")

# 4. Consulta semántica con filtro
response = collection.query.near_text(
    query="peliculas para ver en familia",
    limit=3,
    filters=Filter.by_property("description").like("familia")
)

print("\nResultados filtrados (que mencionan 'familia'):\n")
for obj in response.objects:
    print(f"- {obj.properties['title']}: {obj.properties['description']}")

# 5. Cerrar conexión
client.close()
