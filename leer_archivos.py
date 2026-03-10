import os
os.environ["DEEPEVAL_DISABLE_TIMEOUTS"] = "True" # Desactiva el cronómetro
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel
from deepeval.models import GeminiModel
from metricas import create_custom_metrics
from preguntas import preguntar_chatbot   
from dotenv import load_dotenv
import streamlit as st
from main import obtener_metricas_pregunta
from graficos import obtener_icono
from graficos import obtener_interpretacion
from graficos import grafica_barras
from graficos import semaforo
from graficos import graficar_errores_preguntas


load_dotenv(".env.local")  

import streamlit as st
import pandas as pd

def mostrar():

    st.title("Evaluación por RONDAS ")

  
    col1, col2 = st.columns([3, 1])
    with col1:
        archivo_subido = st.file_uploader("Sube tu archivo (Excel o CSV)", type=['csv', 'xlsx'])
    with col2:
        rondas = st.number_input("Número de rondas", min_value=1, value=4, step=1)

    datos_cargados = None

    if archivo_subido is not None:
        try:
            
            if archivo_subido.name.endswith('.csv'):
                try:
                    datos_cargados = pd.read_csv(archivo_subido, encoding='utf-8')
                except UnicodeDecodeError:
                    datos_cargados = pd.read_csv(archivo_subido, encoding='latin1')
            else:
                datos_cargados = pd.read_excel(archivo_subido)
        
           
            st.success(f"Archivo cargado. {len(datos_cargados)} filas listas.")
        
            with st.expander("Vista previa de los datos", expanded=False):
                st.dataframe(datos_cargados.head())

            st.divider() 
            if st.button("Iniciar Evaluación", type="primary", use_container_width=True):
                st.info(f"Iniciando evaluación de {len(datos_cargados)} preguntas con {rondas} rondas cada una...")
            
                if 'preguntas' in datos_cargados.columns:

                    todos_los_resultados = []
                    for r in range(int(rondas)):
                        ronda_actual = r + 1
                        if ronda_actual > 1:
                            st.markdown("---")
                            st.markdown(f"INICIO DE RONDA {ronda_actual}")
                            st.markdown("---")
                        st.write(f"Procesando Ronda {ronda_actual}")
                        resultados_ronda = []
                        progreso = st.progress(0)
                        total = len(datos_cargados)

                        for i, pregunta in enumerate(datos_cargados['preguntas']):
                            try:
                                resultados_api = obtener_metricas_pregunta(pregunta)
                                for res in resultados_api:
                                    for met in res['metricas']:
                                        estado_emoji = "✅ PASÓ" if met['paso'] else "❌ FALLÓ"
                                        datos_fila = {
                                        'Ronda': ronda_actual,
                                        'pregunta': res['pregunta'],
                                        'respuesta': res['respuesta'],
                                        'metrica': met['metrica'], 
                                        'puntuacion': met['puntuacion'],
                                        'umbral': met['umbral'],
                                        'estado': estado_emoji,
                                        'razon': met['razon']
                                                    }
                                        resultados_ronda.append(datos_fila)
                                        todos_los_resultados.append(datos_fila)
                            except Exception as e:
                                
                                if '503' in str(e) or 'UNAVAILABLE'  in str(e):
                                    st.error(f'El servidor de google esta saturado :( Espere un momento...')
                                else:
                                    st.error(f'Se presento un error :[{e}] Reintentando....')
                            progreso.progress((i + 1) / total)

                        if resultados_ronda:
                            df_ronda_completa = pd.DataFrame(resultados_ronda)
                            metricas_disponibles = df_ronda_completa['metrica'].unique()
                            for nombre_metrica in metricas_disponibles:
                                df_filtrado = df_ronda_completa[df_ronda_completa['metrica'] == nombre_metrica]
                                st.subheader(f'RESULTADOS DE LA RONDA {ronda_actual} EN {nombre_metrica.upper()}')
                                st.dataframe(df_filtrado, use_container_width=True)
                    if todos_los_resultados:
                        st.divider()
                        st.header('RESUMEN GLOBAL DE TODAS LAS RONDAS')
                        df_final = pd.DataFrame(todos_los_resultados)
                        st.dataframe(df_final, use_container_width=True)
                        st.markdown('---')
                        semaforo(df_final)
                        st.markdown('---')
                        grafica_barras(df_final)
                        st.markdown('---')
                        graficar_errores_preguntas(df_final)


                #-----------------------------------------------------------------------------------------------------
                        
                else:
                    st.error("El archivo no contiene una columna llamada 'preguntas'.")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

