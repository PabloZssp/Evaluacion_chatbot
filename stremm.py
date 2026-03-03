import os
import streamlit as st
import pandas as pd
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.models import GeminiModel
from datetime import datetime
from insercion import insertar_metricas_db, crear_df_resultados

os.environ["DEEPEVAL_DISABLE_TIMEOUTS"] = "True"
st.set_page_config(page_title="Evaluador de Chatbot", layout="wide")


st.sidebar.title('Navegar')
pagina = st.sidebar.radio('Ir a', ['Inicio', 'graficos', 'metricas','Cargar archivos'])

try:
    from metricas import create_custom_metrics
    from preguntas import preguntar_chatbot
    # Importar tus funciones de DB aquí también
    # from insercion import crear_df_resultados, insertar_metricas_db 
    st.sidebar.success("➥ Archivos locales cargados correctamente")
except Exception as e:
    st.error(f"✖ Error al importar archivos locales: {e}")
    st.stop()


@st.cache_resource
def load_evaluator():
    
    model = GeminiModel(model="gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY"))
    return create_custom_metrics(model)

if pagina == 'graficos':
    import graficos
    graficos.semaforo_strem()
    
    

elif pagina == 'Inicio':
    metrics = load_evaluator()

    st.title("☳ Evaluación con Deepeval")
    st.write("Presiona el botón para evaluar y guardar los resultados.")
    
    pregunta = st.text_input("Introduce tu pregunta aquí:")

    if st.button("🚀 Iniciar Evaluación", type="primary"):
        if pregunta.strip():
            status_placeholder = st.empty()
        
        with status_placeholder.container():
            st.warning("⏳ Procesando evaluación...")
            
            # 1. Obtener respuesta del chatbot
            #pregunta = "¿Cual es el edificio mas alto de la cdmx?"
            actual_output = preguntar_chatbot(pregunta)

    #------------------------------------------------------------

            
            
            
            test_case_simple = LLMTestCase(
                input=pregunta,
                actual_output=actual_output,
                expected_output="¡Claro! La Ciudad de México ofrece...",
                retrieval_context=["Riqueza gastronómica de CDMX", "Barrios tradicionales"]
            )

            
            evaluation_run = evaluate([test_case_simple], metrics)
            
            
            if hasattr(evaluation_run, 'test_results'):
                results_to_process = evaluation_run.test_results
            else:
                results_to_process = evaluation_run 

        status_placeholder.empty()

        
        filas = []
        for r in results_to_process:
            respuesta_chat = getattr(r, 'actual_output', actual_output)
            if hasattr(r, 'metrics_data'):
                for m in r.metrics_data:
                    filas.append({
                        "Respuesta": respuesta_chat,
                        "Métrica": m.name,
                        "Puntuación": m.score,
                        "Umbral": m.threshold,
                        "Estado": "✅ PASÓ" if m.success else "❌ FALLÓ",
                        "Razón": m.reason
                    })
        
        if filas:
            df_visualizacion = pd.DataFrame(filas)
            
            
            st.subheader("📝 Respuesta del Chatbot")
            st.info(actual_output)
            
            st.markdown("### 📊 Reporte de Evaluación")
            for index, row in df_visualizacion.iterrows():
                with st.expander(f"{row['Estado']} Métrica: {row['Métrica']}", expanded=True):
                    c1, c2, c3 = st.columns([1, 1, 2])
                    with c1:
                        delta_val = round(row['Puntuación'] - row['Umbral'], 2)
                        st.metric(label="Puntaje", value=f"{row['Puntuación']:.2f}", delta=f"{delta_val} vs umbral")
                    with c2:
                        st.write("**Umbral**")
                        st.write(f"{row['Umbral']}")
                    with c3:
                        st.write("**Análisis**")
                        st.caption(row['Razón'])

            # GUARDAR EN DB
            with st.spinner("💾 Guardando en base de datos..."):
                
                df_para_db = crear_df_resultados(test_case_simple, df_visualizacion)
                exito = insertar_metricas_db(df_para_db)
                st.success("✅ Resultados procesados")
                


elif pagina == 'metricas':
    st.title("Configuración de Métricas")
    
    


elif pagina == 'Cargar archivos':
    import leer_archivos
    leer_archivos.mostrar()


    