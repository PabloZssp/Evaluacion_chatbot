import streamlit as st
import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from main import obtener_metricas_pregunta
from graficos import grafica_barras
from graficos import semaforo
from graficos import graficar_errores_preguntas

st.set_page_config(layout="wide", page_title="Evaluador de Chatbot")
load_dotenv(".env.local")

def get_connection():
    return psycopg2.connect(
        host=os.getenv('HOST', "").strip(),
        port=os.getenv('PORT', "").strip(),
        database=os.getenv('DATABASE', "").strip(),
        user=os.getenv('USER', "").strip(),
        password=os.getenv('PASSWORD', "").strip()
    )

@st.cache_data(ttl=600) 
def obtener_rango_fechas_reales():
    """Obtiene la fecha más antigua y la más reciente con datos."""
    try:
        conn = get_connection()
        query = "SELECT MIN(SUBSTRING(start_time, 1, 10)::date), MAX(SUBSTRING(start_time, 1, 10)::date) FROM public.historial_langsmith"
        cur = conn.cursor()
        cur.execute(query)
        min_f, max_f = cur.fetchone()
        conn.close()
        return min_f or datetime.now().date(), max_f or datetime.now().date()
    except Exception as e:
        return datetime.now().date() - timedelta(days=30), datetime.now().date()

def obtener_datos_db(f_inicio, f_fin):
    try:
        conn = get_connection()
        query = """
            SELECT start_time as "Fecha", 
                   question as "Pregunta", 
                   respuesta as "Respuesta"
            FROM public.historial_langsmith 
            WHERE SUBSTRING(start_time, 1, 10)::date BETWEEN %s AND %s
            ORDER BY start_time DESC
        """
        df = pd.read_sql(query, conn, params=(f_inicio, f_fin))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return pd.DataFrame()

def mostrar():

    st.title("Filtro de Casos desde Base de Datos")

    fecha_min_db, fecha_max_db = obtener_rango_fechas_reales()

    col1, col2 = st.columns(2)

    with col1:
        f_inicio = st.date_input(
            "Fecha de inicio", 
            value=fecha_min_db, 
            min_value=fecha_min_db, 
            max_value=fecha_max_db
        )

    with col2:
        f_fin = st.date_input(
            "Fecha final", 
            value=fecha_max_db, 
            min_value=fecha_min_db, 
            max_value=fecha_max_db
        )


    df_filtrado = obtener_datos_db(f_inicio, f_fin)
    # ...
    datos_tabla = df_filtrado.to_dict('records') if not df_filtrado.empty else []

    st.metric("Total de preguntas a evaluar", len(datos_tabla))

    if not datos_tabla:
        st.warning("No se encontraron registros en el rango seleccionado.")
    else:
        st.dataframe(df_filtrado, use_container_width=True)

    rondas = 1 

    if st.button("Iniciar Evaluación", type="primary", use_container_width=True):
        st.info(f"Iniciando evaluación de {len(datos_tabla)} preguntas...")
    
        todos_los_resultados = []
    
        for r in range(int(rondas)):
            ronda_actual = r + 1
            st.write(f"Procesando Ronda {ronda_actual}")
            progreso = st.progress(0)
            total = len(datos_tabla)
            resultado_ronda = []
            for i, fila in enumerate(datos_tabla):
                try:
                    resultados_api = obtener_metricas_pregunta(fila['Pregunta'])
                
                    for res in resultados_api:
                        for met in res['metricas']:
                            datos_fila = {
                                'Ronda': ronda_actual,
                                'pregunta': res['pregunta'],
                                'respuesta': res['respuesta'],
                                'metrica': met['metrica'], 
                                'puntuacion': met['puntuacion'],
                                'estado': "✅ PASÓ" if met['paso'] else "❌ FALLÓ"
                            }
                            resultado_ronda.append(datos_fila)
                            todos_los_resultados.append(datos_fila)
                except Exception as e:

                    if '503' in str(e) or 'UNAVAILABLE'  in str(e):
                        st.error(f'El servidor de google esta saturado :( Espere un momento...')
                    else:
                        st.error(f'Se presento un error :[{e}] Reintentando....')
            
                progreso.progress((i + 1) / total)
            if resultado_ronda:
                df_ronda_completa = pd.DataFrame(resultado_ronda)
                metricas_disponibles = df_ronda_completa['metrica'].unique()
                for nombre_metrica in metricas_disponibles:
                    df_filtrado = df_ronda_completa[df_ronda_completa['metrica'] == nombre_metrica]
                    st.subheader(f'RESULTADOS DE LA RONDA {ronda_actual} en {nombre_metrica.upper()}')
                    st.dataframe(df_filtrado, use_container_width=True)

        if todos_los_resultados:
            st.divider()
            st.header('RESUMEN GLOBAL')
            df_final = pd.DataFrame(todos_los_resultados)
            st.dataframe(df_final, use_container_width=True)
            st.markdown('---')
            semaforo(df_final)
            st.markdown('---')
            grafica_barras(df_final)
            st.markdown('---') 
            graficar_errores_preguntas(df_final)       