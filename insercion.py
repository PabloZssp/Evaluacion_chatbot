import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env.local')

def crear_df_resultados(test_case, df_metricas: pd.DataFrame) -> pd.DataFrame:
    df_insert = df_metricas.rename(columns={
        "Respuesta": "respuesta", 
        "Métrica": "metrica", 
        "Puntuación": "puntuacion", 
        "Umbral": "umbral", 
        "Estado": "estado", 
        "Razón": "razon"
    }).copy()
    
    df_insert['pregunta'] = test_case.input
    df_insert['fecha'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cols = ['pregunta','respuesta','metrica', 'puntuacion', 'umbral', 'estado', 'razon', 'fecha']
    return df_insert[cols]

def insertar_metricas_db(df_insert: pd.DataFrame) -> bool:
    query = """
        INSERT INTO respuestas_table 
        (pregunta,respuesta, metrica, puntuacion, umbral, estado, razon, fecha) 
        VALUES (%s,%s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        df_clean = df_insert.astype(str).copy()
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8'))

        conn = psycopg2.connect(
            host=os.getenv('HOST').strip(),
            port=os.getenv('PORT').strip(),
            database=os.getenv('DATABASE').strip(), 
            user=os.getenv('USER').strip(),
            password=os.getenv('PASSWORD').strip()
        )
        
        with conn:
            with conn.cursor() as cursor:
                execute_batch(cursor, query, df_clean.values.tolist())
        conn.close()
        return True
    except Exception as e:
        
        print(f"Error en la conexión/inserción: {e}")
        return False