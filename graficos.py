import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go



load_dotenv('.env.local')

def obtener_historial_metricas() -> pd.DataFrame:
    try:
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


#borrar no se ocupa
# Ejecución-----------------------------------------------------
def grafica_monitoreo(df:pd.DataFrame):
    st.title("Panel de Monitoreo de Métricas")
    metricas_disponibles = df['metrica'].unique()
    metrica_seleccionada = st.sidebar.selectbox("Selecciona la métrica a visualizar:", metricas_disponibles)
    # 2. Filtrar el DataFrame
    df_filtrado = df[df['metrica'] == metrica_seleccionada].reset_index()
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


#-------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------
df_total = obtener_historial_metricas()

#print((df_total.loc[(df_total['metrica'] == 'Concisión [GEval]') & (df_total['estado'] =='✅ PASÓ')].shape[0]/df_total.index.stop)*100)
#funciones globales
#funciones basicas
def obtener_icono(porcentaje):
    if porcentaje >= 80:
        return "🟢"
    elif porcentaje >= 70:
        return "🟡"
    else:
        return "🔴"
        
def obtener_interpretacion(porcentaje):
    if porcentaje >= 80:
        return 'Cumple criterio mínimo de aceptación de forma satisfactoria'
    elif porcentaje >= 70:
        return 'Aceptable, requiere ajuste'
    else:
        return 'No cumple, acción prioritaria'

#grafica de barras
def grafica_monitoreo(df:pd.DataFrame):
    st.title("Panel de Monitoreo de Métricas")
    metricas_disponibles = df['metrica'].unique()
    metrica_seleccionada = st.sidebar.selectbox("Selecciona la métrica a visualizar:", metricas_disponibles)
    # Filtrar el DataFrame
    df_filtrado = df[df['metrica'] == metrica_seleccionada].reset_index()
    # Mostrar métricas clave en la parte superior (KPIs)
    col1, col2, col3 = st.columns(3)
    promedio = df_filtrado['puntuacion'].mean()
    ultimo_estado = df_filtrado['estado'].iloc[-1]
    
    col1.metric("Promedio Puntuación", f"{promedio:.2f}")
    col2.metric("Último Estado", ultimo_estado)
    col3.metric("Total Pruebas", len(df_filtrado))

    # Crear la Gráfica con Plotly
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

    # Mostrar la tabla detallada debajo
    st.subheader("Datos Detallados")
    st.dataframe(df_filtrado[['metrica', 'puntuacion', 'umbral', 'estado']])

#semaforo
def semaforo(df:pd.DataFrame):
    metricas = ['Answer Relevancy', 'Concisión [GEval]','Exactitud [GEval]','Tono [GEval]']
    total_filas = len(df)
    for metrica in metricas:
        conteo_positivo = df.loc[(df['metrica'] == metrica) & (df['estado'] == '✅ PASÓ')].shape[0]
        conteo_negativo = df.loc[(df['metrica'] == metrica) & (df['estado'] == '❌ FALLÓ')].shape[0]
        #valor = (conteo / total_filas) * 100
        def operacion(conteo):
            return (conteo / df.loc[df['metrica'] == metrica].shape[0]) * 100
        if metrica == 'Answer Relevancy':
            porcentaje_answer = operacion(conteo_positivo)
            porcentaje_answer_negativo = operacion(conteo_negativo)
        elif metrica == 'Concisión [GEval]':
            porcentaje_consicion = operacion(conteo_positivo)
            porcentaje_consicion_negativo = operacion(conteo_negativo)
        elif metrica == 'Exactitud [GEval]':
            porcentaje_exactitud = operacion(conteo_positivo)
            porcentaje_exactitud_negativo = operacion(conteo_negativo)
        elif metrica == 'Tono [GEval]':
            porcentaje_tono = operacion(conteo_positivo)
            porcentaje_tono_negativo = operacion(conteo_negativo) 
    df_semaforo = pd.DataFrame({
    "Metrica": ['Answer Relevancy', 'Concisión [GEval]','Exactitud [GEval]','Tono [GEval]'],
    "Correctas": [round(porcentaje_answer,2),round(porcentaje_consicion,2), round(porcentaje_exactitud,2), round(porcentaje_tono,2)],
    "Semaforo": [obtener_icono(porcentaje_answer),obtener_icono(porcentaje_consicion), obtener_icono(porcentaje_exactitud), obtener_icono(porcentaje_tono)],
    "Interpretacion":[obtener_interpretacion(porcentaje_answer), obtener_interpretacion(porcentaje_consicion),obtener_interpretacion(porcentaje_exactitud), obtener_interpretacion(porcentaje_tono)]
                            })
    st.dataframe(df_semaforo)





def semaforo_strem():
    st.title('Semeforo General')
    st.markdown('---')
    semaforo(df_total)  

    st.markdown('---')
    st.title('GRAFICA GENERAL')
    #grafica_total(porcentaje_answer, porcentaje_consicion, porcentaje_exactitud, porcentaje_tono, porcentaje_answer_negativo, porcentaje_consicion_negativo, porcentaje_exactitud_negativo, porcentaje_tono_negativo)
    grafica_barras(df_total)
    st.markdown('---')
    mostrar_v2()
#-----------------------------------------------------------------------------------------------------------------------------

def grafica_barras(df:pd.DataFrame):
    metricas = ['Answer Relevancy', 'Concisión [GEval]','Exactitud [GEval]','Tono [GEval]']
    total_filas = len(df)
    for metrica in metricas:
        conteo_positivo = df.loc[(df['metrica'] == metrica) & (df['estado'] == '✅ PASÓ')].shape[0]
        conteo_negativo = df.loc[(df['metrica'] == metrica) & (df['estado'] == '❌ FALLÓ')].shape[0]
        #valor = (conteo / total_filas) * 100
        def operacion(conteo):
            return (conteo / df.loc[df['metrica'] == metrica].shape[0]) * 100
        if metrica == 'Answer Relevancy':
            porcentaje_answer = operacion(conteo_positivo)
            porcentaje_answer_negativo = operacion(conteo_negativo)
        elif metrica == 'Concisión [GEval]':
            porcentaje_consicion = operacion(conteo_positivo)
            porcentaje_consicion_negativo = operacion(conteo_negativo)
        elif metrica == 'Exactitud [GEval]':
            porcentaje_exactitud = operacion(conteo_positivo)
            porcentaje_exactitud_negativo = operacion(conteo_negativo)
        elif metrica == 'Tono [GEval]':
            porcentaje_tono = operacion(conteo_positivo)
            porcentaje_tono_negativo = operacion(conteo_negativo) 
    correctas = [porcentaje_answer, porcentaje_consicion,porcentaje_exactitud, porcentaje_tono]
    incorrectas = [porcentaje_answer_negativo, porcentaje_consicion_negativo,porcentaje_exactitud_negativo, porcentaje_tono_negativo]
    #creamos figura
    fig = go.Figure()

    #barra de correctas
    fig.add_trace(go.Bar(x=metricas, y= correctas, name='% Correctas', marker_color="#2fa168",text=[f"{v}" for v in correctas], textposition='outside'))
    #barra de incorrectas
    fig.add_trace(go.Bar(x=metricas, y= incorrectas, name='%Incorrectas', marker_color='#d35d5d',text=[f"{v}" for v in incorrectas], textposition='outside'))
    

    # Diseño del gráfico
    fig.update_layout(
    title='TOTAL DE CORRECTAS Y INCORRECTAS POR MÉTRICA',
    barmode='group', # Agrupa las barras una al lado de la otra
    yaxis=dict(title='Porcentaje', range=[0, 110]), # Rango hasta 110 para que quepan los textos
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor='black'
                )

    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True)
#----------------------------------------------------------------------------------------------------------------------------    

def graficar_errores_preguntas(df):
    st.markdown("### Top Preguntas con Mayor Índice de Error")
    
    # Mapa de colores por métrica
    colores_map = {
        'Answer Relevancy': '#70d6da',  
        'Concisión [GEval]': "#084166",
        'Exactitud [GEval]': "#2fa717",        
        'Tono [GEval]': '#0a9396'               
    }

    # Leyenda manual superior
    cols_leyenda = st.columns(len(colores_map))
    for i, (metrica, color) in enumerate(colores_map.items()):
        cols_leyenda[i].markdown(f'<span style="color:{color};">●</span> **{metrica}**', unsafe_allow_html=True)

    # Filtrado y selección de las preguntas más problemáticas
    df_fallos = df[df['estado'].str.contains('❌', na=False)].copy()
    
    if df_fallos.empty:
        st.info("No hay errores detectados para graficar.")
        return

    # Contamos cuántos errores tiene cada pregunta en total
    conteo_errores = df_fallos['pregunta'].value_counts()
    
    # Seleccionamos solo las TOP 5 preguntas con más errores
    top_5_preguntas = conteo_errores.head(5).index.tolist()
    
    # Filtramos el dataframe original para quedarnos solo con los fallos de esas 5 preguntas
    df_top_fallos = df_fallos[df_fallos['pregunta'].isin(top_5_preguntas)]

    # Agrupamos por pregunta y métrica para el gráfico
    df_plot = df_top_fallos.groupby(['pregunta', 'metrica']).size().reset_index(name='conteo')

    # Construcción del gráfico Donut
    fig = go.Figure(data=[go.Pie(
        labels=df_plot['pregunta'],
        values=df_plot['conteo'],
        hole=0.6,
        domain={'x': [0.4, 1], 'y': [0, 1]}, 
        marker=dict(
            # Asignamos el color basado en la métrica que falló
            colors=[colores_map.get(m, '#white') for m in df_plot['metrica']],
            line=dict(color='#1e1e1e', width=2)
        ),
        hovertemplate="<b>Pregunta:</b> %{label}<br><b>Fallos:</b> %{value}<br><b>Métrica:</b> %{customdata}<extra></extra>",
        customdata=df_plot['metrica'],
        textinfo='percent',
        textposition='inside'
    )])

    #------------------------------------------------
    fig.update_layout(
        height=400,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=0, 
            font=dict(size=11, color="white"),
        )
    )

    st.plotly_chart(fig, use_container_width=True)

def mostrar_v2():
    graficar_errores_preguntas(df_total)

