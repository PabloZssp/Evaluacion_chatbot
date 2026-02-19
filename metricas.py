from deepeval.metrics import GEval
from deepeval.metrics import GEval, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCaseParams



def create_custom_metrics(eval_model):
    # 1. RELEVANCIA: Métrica nativa para medir qué tan bien responde a la consulta.
    relevancia_metric = AnswerRelevancyMetric(
        model=eval_model,
        threshold=0.8
    )

    # 2. TONO: Para validar el branding (emojis, entusiasmo e idioma).
    tono_metric = GEval(
        name="Tono",
        model=eval_model,
        evaluation_params=[
            LLMTestCaseParams.INPUT,          # Para validar el idioma del usuario
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT # Para saber si debe ser empático (sin resultados)
        ],
        evaluation_steps=[
            "Responde en español",
            "1. Identificar elementos de estilo: ¿Existen exclamaciones y emojis que transmitan entusiasmo?",
            "2. Verificación de Idioma: ¿El idioma del output coincide estrictamente con el del input?",
            "3. Validación de Apertura: ¿Se utilizó la frase introductoria específica requerida por el template?",
            "4. Análisis de Empatía: En caso de errores o falta de datos, ¿la respuesta mantiene la calidez o se vuelve robótica?",
            "La puntuación es el grado de cumplimiento de estos 4 pilares de voz de marca."
        ],
        threshold=0.8
    )

    # 3. CONCISIÓN: Foco en la limpieza de datos "No disponibles".
    concision_metric = GEval(
    name="Concisión",
    model=eval_model,
    evaluation_params=[
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.RETRIEVAL_CONTEXT
    ],
    evaluation_steps=[
        "Responde en español.",
        "1. Si la pregunta es sobre eventos locales (listado con nombre, fecha, descripción, precios, lugares), identificar las 'unidades de información útil' y verificar que al menos 1 provengan del contexto. En otro caso, omite esta verificación.",
        "2. Si la pregunta es general, evaluar que la respuesta sea concisa, factual y sin relleno, aunque no provenga del contexto.",
        "3. Evaluar la estructura: ¿El bot va directo al grano tras el saludo inicial?",
        "4. Penalizar etiquetas técnicas internas (ej. 'building_name:'), pero permitir URLs de eventos si aportan valor.",
        "5. Penalizar si hay más de 4000 caracteres en la respuesta completa.",
        "6. Asignar puntuación alta solo si al menos el 90% del mensaje consiste en información útil o frases de cortesía obligatorias.",
        "7. Penalizar si hay párrafos explicativos fuera del contexto o relleno excesivo."
    ],
    threshold=0.8
    )

    ## 4. EXACTITUD: Integridad de la lista y formato técnico.
    exactitud_metric = GEval(
    name="Exactitud",
    model=eval_model,
    evaluation_params=[
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.RETRIEVAL_CONTEXT
    ],
    evaluation_steps=[
        "Responde en español.",
        "Si el contexto contiene lista numerada, aplicar únicamente Flujo Eventos (A).",
         #"Si no contiene lista numerada, aplicar únicamente Flujo General/FIFA (B).",

        # Flujo Eventossre
        "1A. INTEGRIDAD: El output debe contener al menos un evento del contexto; faltar uno o mas no es fallo crítico.",
        "2A. FORMATO TÉCNICO: Debe incluir descripción; si además contiene '*¿Qué es?*' y/o el enlace a cartelera.cdmx.gob.mx, mejora la puntuación.",
        "3A. VERIFICACIÓN DE DATOS: URLs, fechas o direcciones pueden estar o no esto no es un fallo .",
        "4A. LIMPIEZA: Penalizar si aparecen placeholders como 'No disponible', 'No especificado' o campos técnicos.",
        
        "Si no contiene lista numerada, aplicar únicamente Flujo General/FIFA (B).",
        # Flujo General/FIFA
        "1B. SÍNTESIS: La respuesta debe ser clara, natural y coherente.",
        "2B. VERIFICACIÓN DE DATOS: URLs inventadas = alucinación crítica; fechas o direcciones distintas = error menor.",
        "3B. LIMPIEZA: Penalizar si aparecen placeholders como 'No disponible', 'No especificado' o campos técnicos.",

        #"La puntuación será 1.0 solo si cumple con su flujo correspondiente y no inventa información externa."
    ],
    threshold=0.8
    )




    return [relevancia_metric, tono_metric, concision_metric, exactitud_metric]

