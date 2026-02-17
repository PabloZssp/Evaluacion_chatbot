from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel
from deepeval.models import GeminiModel
from metricas import create_custom_metrics
from preguntas import preguntar_chatbot   
import os
from dotenv import load_dotenv
import weaviate
from weaviate.auth import AuthApiKey


load_dotenv(".env.local")  # asegúrate de cargar tu archivo correcto
#S
def main():

    pregunta="que es chapultepec?" 
    
   # Conectar a Weaviate
    client = weaviate.connect_to_weaviate_cloud(
       cluster_url=os.getenv("WEAVIATE_URL"),
       auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    )
    collection = client.collections.use("Eventos_cdmx")

    #eval_model = OllamaModel(model="llama3.2:latest")
    #eval_model = OllamaModel(model="gemma2:latest")
    eval_model = GeminiModel(model="gemini-2.5-flash",api_key=os.getenv("GOOGLE_API_KEY"))
    metrics = create_custom_metrics(eval_model)

    
    actual_output = preguntar_chatbot(pregunta) 

    # Recuperar contexto desde Weaviate 
    response = collection.query.near_text(
        query=pregunta,
        limit=100 #<- aqui mero hay que poner los documentos que queramos que tome
    )
    contexto = [str(obj.properties) for obj in response.objects]#<- aqui se le puede cambiar para tomar campos en especifico


    test_case_simple = LLMTestCase(
        input=pregunta,
        actual_output=actual_output,
        expected_output = """ ¡Claro! La Ciudad de México es vibrante y ofrece muchísimas experiencias. Aquí te doy algunas ideas para que disfrutes al máximo:
        * Museo Nacional de Antropología...
        """,
    retrieval_context=contexto
    )
    
    results_simple = evaluate([test_case_simple], metrics)

    print("\nResultados :")
    for r in results_simple.test_results:
        print(f"Pregunta: {r.input}")
        print(f"Respuesta: {r.actual_output}")
        for m in r.metrics_data:
            print(f"- Métrica: {m.name}")
            print(f"  Puntuación: {m.score}")
            print(f"  Umbral: {m.threshold}")
            print(f"  ¿Pasó?: {m.success}")
            print(f"  Razón: {m.reason}")
            print("----------------------------------------------------")
    client.close()

if __name__ == "__main__":
    main()

