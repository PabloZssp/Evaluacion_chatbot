import os
import weaviate
from weaviate.auth import AuthApiKey
import pandas as pd
from dotenv import load_dotenv

load_dotenv(".env.local")

def datos_contexto(pregunta):
    pregunta_obtenida = pregunta
    # Conectar a Weaviate--------------------------------------
    client = weaviate.connect_to_weaviate_cloud(
       cluster_url=os.getenv("WEAVIATE_URL"),
       auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    )
    collection = client.collections.use("Eventos_cdmx") #Tabla 

    # Recuperar contexto desde Weaviate-----------------------
    response = collection.query.near_text(
        query=pregunta_obtenida,
        limit=100 #<- aqui mero hay que poner los documentos que queramos que tome
    )
    contexto = [str(obj.properties) for obj in response.objects]#<- aqui se le puede cambiar para tomar campos en especifico
    return contexto

a = datos_contexto('¿Cuáles son los mejores restaurantes de la CDMX?')

print(a)