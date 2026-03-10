from calendario_strem import obtener_datos_db

df = obtener_datos_db('2026-03-10T09:00:01','2026-03-10T15:00:00')
print(df.columns())