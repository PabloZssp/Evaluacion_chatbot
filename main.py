from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel
from metricas import create_custom_metrics
from preguntas import preguntar_chatbot   # importa tu función

def main():
    eval_model = OllamaModel(model="llama3.2:latest")
    metrics = create_custom_metrics(eval_model)

    # Caso SIN expected_output (solo relevancia y concisión)
    actual_output = preguntar_chatbot("What is the capital of France?")
    test_case_simple = LLMTestCase(
        input="What is the capital of France?",
        actual_output=actual_output
    )

    results_simple = evaluate([test_case_simple], [metrics[0], metrics[2]])  # Relevancia y Concisión
    print("\nResultados sin expected_output:")
    for r in results_simple.test_results:
        for m in r.metrics_data:
            print(f"- {m.name}: {m.score} → {m.reason}")

if __name__ == "__main__":
    main()
