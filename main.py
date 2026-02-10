from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel
from metricas import create_custom_metrics
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    eval_model = OllamaModel(model="llama3.2:latest")
    metrics = create_custom_metrics(eval_model)

    # Caso SIN expected_output (solo relevancia y concisión)
    test_case_simple = LLMTestCase(
        input="What is the capital of France?",
        actual_output="The capital of France is Paris."
    )
    results_simple = evaluate([test_case_simple], [metrics[0], metrics[2]])  # Relevancia y Concisión
    print("\nResultados sin expected_output:")
    for r in results_simple.test_results:
        for m in r.metrics_data:
            print(f"- {m.name}: {m.score} → {m.reason}")

    # Caso CON expected_output (todas las métricas)
    test_case_full = LLMTestCase(
        input="I have a persistent cough and fever. Should I be worried?",
        actual_output="A persistent cough and fever could be a viral infection or something more serious. See a doctor if symptoms worsen or don't improve in a few days.",
        expected_output="A persistent cough and fever could indicate a range of illnesses, from a mild viral infection to more serious conditions like pneumonia or COVID-19. You should seek medical attention if your symptoms worsen, persist for more than a few days, or are accompanied by difficulty breathing, chest pain, or other concerning signs.",
        retrieval_context=["Medical guidelines about respiratory infections"]
    )
    results_full = evaluate([test_case_full], metrics)
    print("\nResultados con expected_output:")
    for r in results_full.test_results:
        for m in r.metrics_data:
            print(f"- {m.name}: {m.score} → {m.reason}")

if __name__ == "__main__":
    main()

