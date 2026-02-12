from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel
from deepeval.models import GeminiModel
from metricas import create_custom_metrics
from preguntas import preguntar_chatbot   
import os
from dotenv import load_dotenv

load_dotenv(".env.local")  # asegúrate de cargar tu archivo correcto

def main():
    #eval_model = OllamaModel(model="llama3.2:latest")
    #eval_model = OllamaModel(model="gemma2:latest")
    eval_model = GeminiModel(model="gemini-2.5-flash",api_key=os.getenv("GOOGLE_API_KEY"))
    metrics = create_custom_metrics(eval_model)

    
    actual_output = preguntar_chatbot("que eventos hay para este mes?")  
    test_case_simple = LLMTestCase(
        input="que eventos hay para este mes?",
        actual_output=actual_output,
        expected_output = """ ¡Claro! La Ciudad de México es vibrante y ofrece muchísimas experiencias. Aquí te doy algunas ideas para que disfrutes al máximo:
        * Museo Nacional de Antropología...
        """,
    retrieval_context=[ "La Ciudad de México es reconocida por su riqueza cultural, histórica y gastronómica.", "Museos destacados: Antropología, Soumaya, Frida Kahlo.", "Arquitectura: Palacio de Bellas Artes, Palacio Postal.", "Barrios tradicionales: Coyoacán, San Ángel." ]
    )
    
    results_simple = evaluate([test_case_simple], metrics)

    print("\nResultados sin expected_output:")
    for r in results_simple.test_results:
        print(f"Pregunta: {r.input}")
        print(f"Respuesta: {r.actual_output}")
        for m in r.metrics_data:
            print(f"- Métrica: {m.name}")
            print(f"  Puntuación: {m.score}")
            print(f"  Umbral: {m.threshold}")
            print(f"  ¿Pasó?: {m.success}")
            print(f"  Razón: {m.reason}")


if __name__ == "__main__":
    main()

