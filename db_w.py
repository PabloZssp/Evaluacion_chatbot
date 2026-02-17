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
collection = client.collections.use("Eventos_cdmx")

# 3. Consulta semántica simple
response = collection.query.near_text(
    query="Febrero",
    limit=2
)

print("Resultados de búsqueda:\n")
for obj in response.objects:
    print(f"- {obj.properties['title']}: {obj.properties['description']}")

# 4. Consulta semántica con filtro
response = collection.query.near_text(
    query="febrero",
    limit=3,
    filters=Filter.by_property("description").like("febrero")
)

print("\nResultados filtrados (que mencionan 'febrero'):\n")
for obj in response.objects:
    print(f"- {obj.properties['title']}: {obj.properties['description']}")

# 5. Cerrar conexión
client.close()
