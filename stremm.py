import os
os.environ["DEEPEVAL_DISABLE_TIMEOUTS"] = "True" # Desactiva el cronómetro
import streamlit as st
import pandas as pd
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.models import GeminiModel
import ollama
from datetime import datetime


import streamlit as st
# ... resto de tus imports
# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Evaluador de Chatbot", layout="wide")
st.title("☳ Evaluación con Deepeval: PABLO TIENE SARAMPIÓN")

# --- WRAPPER DE OLLAMA ---
#class OllamaWrapper(DeepEvalBaseLLM):
#    def __init__(self, model_name):
#        self.model_name = model_name
#    def load_model(self): return self.model_name
#    def generate(self, prompt: str) -> str:
#        return ollama.generate(model=self.model_name, prompt=prompt)['response']
#    async def a_generate(self, prompt: str) -> str: return self.generate(prompt)
#    def get_model_name(self): return self.model_name

# --- INTENTO DE IMPORTACIÓN CON ERROR VISIBLE ---
try:
    from metricas import create_custom_metrics
    from preguntas import preguntar_chatbot
    st.sidebar.success("➥ Archivos locales cargados")
except Exception as e:
    st.error(f"✖ Error al importar archivos locales: {e}")
    st.stop() # Detiene la ejecución para que veas el error

# --- CARGA DE EVALUADOR ---
@st.cache_resource
def load_evaluator():
    #eval_model = GeminiModel(model="gemini-2.5-flash",api_key=os.getenv("GOOGLE_API_KEY"))
    model = GeminiModel(model="gemini-2.5-flash",api_key=os.getenv("GOOGLE_API_KEY"))
    return create_custom_metrics(model)

metrics = load_evaluator()

# --- INTERFAZ PRINCIPAL ---
st.write("Presiona el botón para evaluar la respuesta del chatbot según las directrices culturales.")

if st.button("🚀 Iniciar Evaluación", type="primary"):
    # Creamos un contenedor vacío para ir llenando
    status_placeholder = st.empty()
    
    with status_placeholder.container():
        st.warning("⏳ Procesando... Esto puede tardar unos segundos según tu CPU.")
        
        # 1. Obtener respuesta
        actual_output = preguntar_chatbot("¿Cuáles son los mejores museos de la CDMX?")
        
        # 2. Crear caso de prueba
        test_case_simple = LLMTestCase(
            input="¿Cuáles son los mejores museos de la CDMX?",
            actual_output=actual_output,
            expected_output="""¡Claro! La Ciudad de México es vibrante y ofrece muchísimas experiencias. Aquí te doy algunas ideas para que disfrutes al máximo:
        * Museo Nacional de Antropología...
        """,
            retrieval_context=["La Ciudad de México es reconocida por su riqueza cultural, histórica y gastronómica.", "Museos destacados: Antropología, Soumaya, Frida Kahlo.", "Arquitectura: Palacio de Bellas Artes, Palacio Postal.", "Barrios tradicionales: Coyoacán, San Ángel."]
        )

        # 3. Evaluar
        #results = evaluate([test_case_simple], metrics)
        #results = evaluate([test_case_simple], metrics)
        # Si results es una tupla, DeepEval suele devolver (TestResults, ...)
        # Para asegurar que 'results' sea la lista que esperas:
        #if isinstance(results, tuple):
            #results = results[0]
        
    # Limpiamos el aviso de carga
    #status_placeholder.empty()

    # --- PROCESAR TABLA ---
    #filas = []
    #for r in results:
    #    for m in r.metrics_data:
    #        filas.append({
    #            "Métrica": m.name,
    #            "Puntuación": m.score,
    #            #"Estado": "✅" if m.success else "❌",
    #            "Estado": m.success,
    #            "Razón": m.reason
    #        })

        # 3. Evaluar
        # Capturamos el objeto de resultados completo
        evaluation_run = evaluate([test_case_simple], metrics)
        
        # DeepEval suele devolver un objeto que contiene 'test_results'
        # Verificamos si es el objeto de resultados o una lista
        if hasattr(evaluation_run, 'test_results'):
            results_to_process = evaluation_run.test_results
        elif isinstance(evaluation_run, list):
            results_to_process = evaluation_run
        else:
            # Si es una tupla (común en algunas versiones), el primer elemento son los resultados
            results_to_process = evaluation_run[0] if isinstance(evaluation_run, tuple) else []

    # Limpiamos el aviso de carga
    status_placeholder.empty()

    # --- PROCESAR TABLA ---
    filas = []
    # Ahora iteramos sobre la lista segura de resultados
    for r in results_to_process:
        # Verificamos que r tenga métricas antes de iterar
        if hasattr(r, 'metrics_data'):
            for m in r.metrics_data:
                filas.append({
                    "Métrica": m.name,
                    "Puntuación": m.score,
                    "Umbral": m.threshold,
                    "Estado": "✅ PASÓ" if m.success else "❌ FALLÓ",
                    "Razón": m.reason
                })
    df = pd.DataFrame(filas)

    # --- MOSTRAR RESULTADOS ---
    st.subheader("📝 Respuesta del Chatbot")
    st.info(actual_output)

    st.subheader("📊 Tabla de Métricas")
    st.dataframe(df)
    #st.dataframe(df, use_container_width=True, hide_index=True)

    #----------------------------------------------------
    def obtener_fecha_actual() -> str:
        """
        Devuelve la fecha actual en formato string (YYYY-MM-DD)
        Returns:
        str: Fecha en formato 'YYYY-MM-DD'
        """
        return datetime.now().strftime('%Y-%m-%d')
    fecha_df_insert = obtener_fecha_actual()
    
    df_insert = pd.DataFrame({
        'pregunta': test_case_simple.input,
        'metrica': df["Métrica"],
        'puntuacion': df["Puntuación"],
        'umbral': df["Umbral"],
        'estado': df["Estado"],
        'razon': df["Razón"],
        'fecha': fecha_df_insert
    })