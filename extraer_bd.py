import os
import json
import psycopg2
import logging
from pathlib import Path
from dotenv import load_dotenv
from export_traces import get_langsmith_client, fetch_root_runs, fetch_retriever_runs, combine_runs_with_context

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv(".env.local")

def get_db_connection():
    """Conexión usando los nombres de variables que SÍ funcionan en tu .env"""
    load_dotenv(".env.local") 

    return psycopg2.connect(
        host=os.getenv("HOST", "").strip(),
        port=os.getenv("PORT", "").strip(),
        database=os.getenv("DATABASE", "").strip(),
        user=os.getenv("USER", "").strip(),
        password=os.getenv("PASSWORD", "").strip()
    )

def insertar_en_db(cursor, run):
    """Limpia los datos del run e inserta en la tabla historial_langsmith."""
    try:
       
        inputs = json.loads(run.get("inputs", "{}"))
        outputs = json.loads(run.get("outputs", "{}"))
        
       
        id_ls = run.get("id")
        start_time = run.get("start_time")
        end_time = run.get("end_time")
        cliente_ip = inputs.get("client_ip", "N/A")
        question = inputs.get("question", "N/A")
        respuesta = outputs.get("output", "")

       
        query = """
            INSERT INTO historial_langsmith (id_, start_time, end_time, cliente_ip, question, respuesta)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (id_ls, start_time, end_time, cliente_ip, question, respuesta))
        
    except Exception as e:
        logging.error(f"Error procesando el registro {run.get('id')}: {e}")

def actualizar_datos(project_name, start_date, end_date):
    """Función principal para extraer de LangSmith e insertar en la DB."""
    conn = None
    try:
        
        client = get_langsmith_client()
        date_filter = f'and(gt(start_time, "{start_date}"), lt(start_time, "{end_date}"))'
        
        root_runs = fetch_root_runs(client, project_name, date_filter)
        if not root_runs:
            logging.warning("No se encontraron datos en LangSmith.")
            return

        retriever_by_trace = fetch_retriever_runs(client, project_name, date_filter)
        flat_runs = combine_runs_with_context(root_runs, retriever_by_trace)

       
        conn = get_db_connection()
        cur = conn.cursor()
        
        logging.info(f"Insertando {len(flat_runs)} registros en la base de datos...")
        
        for run in flat_runs:
            insertar_en_db(cur, run)
        
        conn.commit()
        cur.close()
        logging.info("¡Sincronización completada con éxito!")

    except Exception as e:
        logging.error(f"Error en el proceso de actualización: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    
    actualizar_datos(
        project_name="testing-dev-martin", 
        start_date="2026-03-10T09:00:01", 
        end_date="2026-03-10T15:00:00"
    )