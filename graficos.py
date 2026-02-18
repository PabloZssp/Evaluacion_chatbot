import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import plotly.express as px
import streamlit as st


# Asegúrate de que la ruta sea correcta según dónde estés ejecutando el script
load_dotenv('.env.local')

def obtener_historial_metricas() -> pd.DataFrame:
    try:
        # Usamos .get(key, "") para que si es None, devuelva un string vacío y el .strip() funcione
        conn = psycopg2.connect(
            host=os.getenv('HOST', "").strip(),
            port=os.getenv('PORT', "").strip(),
            database=os.getenv('DATABASE', "").strip(),
            user=os.getenv('USER', "").strip(),
            password=os.getenv('PASSWORD', "").strip()
        )
        
        query = "SELECT * FROM public.respuestas_table ORDER BY fecha DESC"
        
        # Leemos directamente a DataFrame
        df_resultados = pd.read_sql(query, conn)
        
        conn.close()
        return df_resultados
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return pd.DataFrame()

# Ejecución
def mostrar():
    a = obtener_historial_metricas()
    
    st.title("Panel de Monitoreo de Métricas")
    
    # 1. Filtro lateral para elegir la métrica
    metricas_disponibles = a['metrica'].unique()
    metrica_seleccionada = st.sidebar.selectbox("Selecciona la métrica a visualizar:", metricas_disponibles)
    
    # 2. Filtrar el DataFrame
    df_filtrado = a[a['metrica'] == metrica_seleccionada].reset_index()
    
    # 3. Mostrar métricas clave en la parte superior (KPIs)
    col1, col2, col3 = st.columns(3)
    promedio = df_filtrado['puntuacion'].mean()
    ultimo_estado = df_filtrado['estado'].iloc[-1]
    
    col1.metric("Promedio Puntuación", f"{promedio:.2f}")
    col2.metric("Último Estado", ultimo_estado)
    col3.metric("Total Pruebas", len(df_filtrado))

    # 4. Crear la Gráfica con Plotly
    fig = px.line(
        df_filtrado, 
        x=df_filtrado.index, 
        y='puntuacion',
        title=f"Evolución Histórica: {metrica_seleccionada}",
        labels={'index': 'Número de Ejecución', 'puntuacion': 'Score'},
        markers=True
    )
    
    # Añadir una línea roja para el umbral (threshold)
    fig.add_hline(y=df_filtrado['umbral'].iloc[0], line_dash="dash", line_color="red", annotation_text="Umbral Mínimo")
    
    # Ajustar rango del eje Y de 0 a 1
    fig.update_yaxes(range=[0, 1.1])
    
    st.plotly_chart(fig, use_container_width=True)

    # 5. Mostrar la tabla detallada debajo
    st.subheader("Datos Detallados")
    st.dataframe(df_filtrado[['metrica', 'puntuacion', 'umbral', 'estado']])