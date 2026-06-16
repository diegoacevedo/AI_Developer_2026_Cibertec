"""
tools/sql_tool.py — herramienta para consultar la base de datos de ventas históricas.

La BD contiene ventas mensuales de Andean Foods con las siguientes columnas:
  - canal:    canal de venta (LIMA, PROVINCIA, MODERNO, FOOD SERVICE, OTROS)
  - division: línea de negocio (000-HARINAS INDUSTRIALES, 001-ALIMENTOS, 002-CONFITES, 003-MASCOTAS)
  - periodo:  mes en formato YYYY-MM (ej: 2024-01). Rango disponible: 2023-01 a 2026-06
  - venta:    monto de ventas en soles como texto con comas (ej: "270,850")

El campo 'venta' debe convertirse con: CAST(REPLACE(venta,',','') AS REAL)
"""
import sqlite3
import os
import pandas as pd
from langchain_core.tools import tool


# ruta de la BD — relativa al directorio donde se ejecuta la app
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ventas_hist.db")


@tool
def consultar_ventas(query_sql: str) -> str:
    """
    Ejecuta una consulta SQL sobre la base de datos de ventas históricas de Andean Foods.

    La tabla se llama 'ventas' y tiene estas columnas:
      - canal TEXT:    'LIMA', 'PROVINCIA', 'MODERNO', 'FOOD SERVICE', 'OTROS'
      - division TEXT: '000-HARINAS INDUSTRIALES', '001-ALIMENTOS', '002-CONFITES', '003-MASCOTAS'
      - periodo TEXT:  formato 'YYYY-MM', rango 2023-01 a 2026-06
      - venta TEXT:    monto en soles con comas (ej: '270,850')

    Para operar con montos usar: CAST(REPLACE(venta,',','') AS REAL)
    Ejemplo: SELECT canal, SUM(CAST(REPLACE(venta,',','') AS REAL)) as total FROM ventas GROUP BY canal

    Solo se permiten consultas SELECT.
    """
    if not query_sql.strip().upper().startswith("SELECT"):
        return "Solo se permiten consultas SELECT."
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(query_sql, conn)
        conn.close()
        if df.empty:
            return "La consulta no devolvió resultados."
        return df.to_string(index=False)
    except Exception as e:
        return f"Error en la consulta SQL: {e}"
