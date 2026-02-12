import os
import weaviate
from weaviate.auth import AuthApiKey
from dotenv import load_dotenv
import psycopg2
import google.generativeai as genai

# 1. Cargar variables de entorno
load_dotenv(".env.local")

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# 2. Conectar a Weaviate Cloud
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=AuthApiKey(weaviate_api_key),
)
print("Weaviate listo:", client.is_ready())

# 3. Conectar a Postgres
conn = psycopg2.connect("dbname=chatbot user=postgres password=... host=localhost")
cur = conn.cursor()

# 4. Crear colección en Weaviate (si no existe)
if "Documentos" not in [c.name for c in client.collections.list()]:
    client.collections.create(
        name="Documentos",
        properties=[
            {"name": "title", "dataType": "text"},
            {"name": "descripcion", "dataType": "text"},
            {"name": "fecha", "dataType": "date"},
            {"name": "url", "dataType": "text"},
            {"name": "recinto", "dataType": "text"},
        ]
    )

collection = client.collections.get("Documentos")

# 5. Configurar Gemini para embeddings
genai.configure(api_key=gemini_api_key)

def embed_text(text: str):
    model = genai.GenerativeModel("embedding-001")  # modelo de embeddings de Gemini
    response = model.embed_content(text)
    return response.embedding

# 6. Leer documentos desde Postgres
cur.execute("SELECT id, title, content FROM cultura_cdmx;")
rows = cur.fetchall()

# 7. Insertar documentos en Weaviate con embeddings
for row in rows:
    doc_id, title, content = row
    embedding = embed_text(content)

    collection.data.insert(
        properties={
            "title": title,
            "descripcion": content
        },
        vector=embedding
    )

print("Documentos indexados en Weaviate.")

# 8. Ejemplo de consulta RAG
pregunta = "¿Qué museos visitar en CDMX?"
pregunta_emb = embed_text(pregunta)

result = collection.query.near_vector(
    near_vector=pregunta_emb,
    limit=3
)

retrieval_context = [obj.properties["descripcion"] for obj in result.objects]
print("Contexto recuperado:", retrieval_context)

# 9. Cerrar conexiones
cur.close()
conn.close()
client.close()
