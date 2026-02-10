from deepeval import assert_test
from deepeval.test_case import LLMTestCaseParams
from deepeval.metrics import GEval



def create_custom_metrics(eval_model):
    """4 métricas personalizadas del testing manual"""

    # 1. RELEVANCIA
    relevancia_metric = GEval(
        name="Relevancia",
        model=eval_model,
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT
        ],
        evaluation_steps=[
            "Analiza la pregunta del usuario y determina qué información busca",
            "Examina la respuesta generada por el chatbot",
            "Evalúa si la respuesta aborda directamente la pregunta",
            "Verifica que la respuesta sea útil y aplicable al contexto",
            "Determina si hay información irrelevante o fuera de tema"
        ],
        threshold=0.7
    )

    # 2. TONO
    tono_metric = GEval(
        name="Tono",
        model=eval_model,
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT
        ],
        evaluation_steps=[
            "Analiza el tono de la respuesta del chatbot",
            "Verifica que el tono sea profesional, cordial y respetuoso",
            "Comprueba que el lenguaje sea apropiado para el contexto",
            "Evalúa si el tono es consistente con las directrices",
            "Verifica que no haya un tono excesivamente formal o informal",
            "Compara con la respuesta esperada para validar el tono"
        ],
        threshold=0.7
    )

    # 3. CONCISIÓN
    concision_metric = GEval(
        name="Concisión",
        model=eval_model,
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT
        ],
        evaluation_steps=[
            "Analiza la longitud de la respuesta en relación a la pregunta",
            "Verifica que la respuesta sea directa y vaya al grano",
            "Identifica si hay redundancia o información repetitiva",
            "Evalúa si se puede comunicar la misma información de forma más breve",
            "Verifica que no haya divagaciones o información innecesaria",
            "Determina si la respuesta sigue las indicaciones de brevedad"
        ],
        threshold=0.7
    )

    # 4. EXACTITUD
    exactitud_metric = GEval(
        name="Exactitud",
        model=eval_model,
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT
        ],
        evaluation_steps=[
            "Compara la respuesta generada con la respuesta esperada",
            "Verifica que los hechos y datos mencionados sean correctos",
            "Comprueba que la información esté respaldada por el contexto",
            "Identifica cualquier información incorrecta o engañosa",
            "Evalúa si hay alucinaciones (información inventada)",
            "Verifica que las afirmaciones sean confiables"
        ],
        threshold=0.7
    )

    return [relevancia_metric, tono_metric, concision_metric, exactitud_metric]

