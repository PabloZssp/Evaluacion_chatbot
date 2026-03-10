import json
import os

from dotenv import load_dotenv
from metricas import create_custom_metrics

from deepeval import evaluate
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase
import streamlit as st
import pandas as pd
from graficos import semaforo, grafica_barras, graficar_errores_preguntas

import json
from datetime import datetime
from main import obtener_metricas_pregunta
import streamlit as st
import json
import pandas as pd
from datetime import datetime

load_dotenv(".env.local")

# Configuración de página (opcional, para que la tabla se vea más ancha)
st.set_page_config(layout="wide")

# 1. Cargar datos y extraer fechas disponibles
with open("runs_export_with_context.json", encoding="utf-8") as f:
    runs = json.load(f)

fechas_disponibles = []
for run in runs:
    st_time = run.get("start_time")
    if st_time:
        try:
            dt = datetime.strptime(st_time[:10], "%Y-%m-%d").date()
            fechas_disponibles.append(dt)
        except:
            continue

min_fecha = min(fechas_disponibles) if fechas_disponibles else datetime.now().date()
max_fecha = max(fechas_disponibles) if fechas_disponibles else datetime.now().date()

# 2. Interfaz de Streamlit
st.title("Filtro de Casos")

col1, col2 = st.columns(2)

with col1:
    f_inicio = st.date_input("Fecha de inicio", value=min_fecha, min_value=min_fecha, max_value=max_fecha)

with col2:
    f_fin = st.date_input("Fecha final", value=max_fecha, min_value=min_fecha, max_value=max_fecha)

# 3. Lógica de filtrado y recolección de datos
datos_tabla = []

for run in runs:
    start_time_str = run.get("start_time")
    if not start_time_str:
        continue
    
    try:
        fecha_run = datetime.strptime(start_time_str[:10], "%Y-%m-%d").date()
        
        if f_inicio <= fecha_run <= f_fin:
            inputs = run.get("inputs") or {}
            outputs = run.get("outputs") or {}
            
            pregunta = inputs.get("question", "")
            respuesta = outputs.get("output") or outputs.get("answer", "")
            
            # Solo agregamos si hay contenido
            if pregunta and respuesta:
                datos_tabla.append({
                    "Fecha": start_time_str[:16], # Mostramos fecha y hora (sin segundos)
                    "Pregunta": pregunta,
                    "Respuesta": respuesta
                })
    except:
        continue

# 4. Mostrar métrica y Dataframe
st.metric("Total de preguntas a evaluar", len(datos_tabla))

if datos_tabla:
    df = pd.DataFrame(datos_tabla)
    # Mostramos la tabla. use_container_width hace que ocupe todo el ancho
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No se encontraron datos para el rango seleccionado.")


# --- COLOCAR DEBAJO DEL DATAFRAME ---

# Definimos el número de rondas (puedes cambiarlo por un st.number_input si prefieres)
rondas = 1 

if st.button("Iniciar Evaluación", type="primary", use_container_width=True):
    # Usamos len(datos_tabla) que son los datos ya filtrados por fecha
    st.info(f"Iniciando evaluación de {len(datos_tabla)} preguntas con {rondas} rondas cada una...")

    todos_los_resultados = []
    
    # Iteramos por las rondas
    for r in range(int(rondas)):
        ronda_actual = r + 1
        if ronda_actual > 1:
            st.markdown("---")
            st.markdown(f"**INICIO DE RONDA {ronda_actual}**")
            st.markdown("---")
            
        st.write(f"Procesando Ronda {ronda_actual}")
        resultados_ronda = []
        progreso = st.progress(0)
        total = len(datos_tabla)

        # Iteramos sobre la lista datos_tabla generada en tu paso anterior
        for i, fila in enumerate(datos_tabla):
            try:
                # Extraemos la pregunta de la fila actual
                pregunta_evaluar = fila['Pregunta']
                
                # Llamada a tu función de métricas
                resultados_api = obtener_metricas_pregunta(pregunta_evaluar)
                
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
                if '503' in str(e) or 'UNAVAILABLE' in str(e):
                    st.error(f'El servidor de Google está saturado :( Esperando...')
                else:
                    st.error(f'Error en pregunta: {e}. Reintentando...')
            
            progreso.progress((i + 1) / total)

        # Al finalizar la ronda, mostramos sus tablas específicas
        if resultados_ronda:
            df_ronda_completa = pd.DataFrame(resultados_ronda)
            metricas_disponibles = df_ronda_completa['metrica'].unique()
            for nombre_metrica in metricas_disponibles:
                df_filtrado = df_ronda_completa[df_ronda_completa['metrica'] == nombre_metrica]
                st.subheader(f'RESULTADOS DE LA RONDA {ronda_actual} EN {nombre_metrica.upper()}')
                st.dataframe(df_filtrado, use_container_width=True)

    # Resumen final si hubo resultados
    if todos_los_resultados:
        st.divider()
        st.header('RESUMEN GLOBAL DE TODAS LAS RONDAS')
        df_final = pd.DataFrame(todos_los_resultados)
        st.dataframe(df_final, use_container_width=True)
        
        # Aquí puedes llamar a tus funciones de gráficas
        # semaforo(df_final)
        # grafica_barras(df_final)