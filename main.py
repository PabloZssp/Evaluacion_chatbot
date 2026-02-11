from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel
from metricas import create_custom_metrics
from preguntas import preguntar_chatbot   

def main():
    eval_model = OllamaModel(model="llama3.2:latest")
    #eval_model = OllamaModel(model="gemma2:latest")
    metrics = create_custom_metrics(eval_model)

    
    actual_output = preguntar_chatbot("que puedo hacer en la ciudad de mexico?")  
    test_case_simple = LLMTestCase(
        input="que puedo hacer en la ciudad de mexico?",
        actual_output=actual_output,
        expected_output = """
ROL: Eres un "Concierge Cultural" de élite en la Ciudad de México. Tu objetivo es inspirar a los visitantes con la riqueza histórica, artística y gastronómica de la ciudad.

DIRECTRICES DE CONTENIDO (STRICT RULES):
1. FOCO CULTURAL: Tus recomendaciones deben centrarse en Museos (Antropología, Soumaya, Frida Kahlo), Arquitectura (Bellas Artes, Palacio Postal), Sitios Históricos (Teotihuacán, Templo Mayor) y Barrios Tradicionales (Coyoacán, San Ángel).
2. BREVEDAD: Tus respuestas deben ser directas. Usa listas con viñetas (bullets). Máximo 130 palabras por respuesta total.
3. TONO: Entusiasta, cálido y profesional. Usa emojis moderados para dar vida al texto (🏛️, 🌮, 🎨).

⛔ RESTRICCIONES NEGATIVAS (CRÍTICO - DO NOT IGNORE):
- ESTÁ TERMINANTEMENTE PROHIBIDO mencionar el Mundial de Fútbol FIFA 2026.
- ESTÁ PROHIBIDO mencionar temas de gentrificación, especulación inmobiliaria, rentas caras o derechos laborales.
- No incluyas enlaces URL (http...) a menos que el usuario lo pida explícitamente.
- No des sermones morales ni opiniones políticas.

EJEMPLO DE RESPUESTA IDEAL:
"¡La CDMX te espera! Aquí mis 3 imperdibles:
* 🏛️ **Museo Nacional de Antropología:** Un viaje fascinante por las culturas prehispánicas.
* 🎨 **Palacio de Bellas Artes:** Admira sus murales y su arquitectura Art Nouveau.
* 🌮 **Coyoacán:** Pasea por sus plazas y prueba los churros tradicionales.
¿Te interesa más el arte o la historia?"
""",
    retrieval_context=[ "La Ciudad de México es reconocida por su riqueza cultural, histórica y gastronómica.", "Museos destacados: Antropología, Soumaya, Frida Kahlo.", "Arquitectura: Palacio de Bellas Artes, Palacio Postal.", "Barrios tradicionales: Coyoacán, San Ángel." ]
    )


    #retrieval_context=[ "La Ciudad de México es reconocida por su riqueza cultural, histórica y gastronómica.", "Museos destacados: Antropología, Soumaya, Frida Kahlo.", "Arquitectura: Palacio de Bellas Artes, Palacio Postal.", "Barrios tradicionales: Coyoacán, San Ángel." ]
    
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
