from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel
from metricas import create_custom_metrics
from preguntas import preguntar_chatbot   

def main():

    """
    Función principal para ejecutar la evaluación del chatbot utilizando métricas personalizadas.:V"""
    eval_model = OllamaModel(model="llama3.2:latest")
    metrics = create_custom_metrics(eval_model)

    
    actual_output = preguntar_chatbot("que puedo hacer en la ciudad de mexico?")  
    test_case_simple = LLMTestCase(
        input="que puedo hacer en la ciudad de mexico?",
        actual_output=actual_output,
        expected_output="La respuesta debe mencionar actividades turísticas y culturales en la Ciudad de México."
    )

    results_simple = evaluate([test_case_simple], [metrics[0], metrics[1], metrics[2]])

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
