# Proyecto Integrador — Asistente BI Andean Foods
### Python AI Developer 2026 · Capítulo final

---

## ¿Qué hace este proyecto?

Un agente de IA que responde preguntas en lenguaje natural sobre el negocio de Andean Foods,
decidiendo autónomamente qué herramienta usar en cada caso:

| Tipo de pregunta | Herramienta |
|---|---|
| "¿Cuánto vendió LIMA en 2024?" | `consultar_ventas` → SQLite |
| "¿Cuál es la metodología de BI de la empresa?" | `consultar_politica` → RAG sobre .docx |
| "¿Cómo está el mercado de harinas industriales?" | `buscar_web` → Tavily |
| "¿Qué división tuvo más ventas y cuál es su contexto de mercado?" | SQL + Web |
| "¿Qué es un modelo dimensional?" | Conocimiento propio (sin herramienta) |

---

## Estructura del proyecto

```
proyecto_integrador/
├── main.py              ← API FastAPI (punto de entrada)
├── agente.py            ← agente ReAct con las 3 herramientas
├── tools/
│   ├── __init__.py
│   ├── sql_tool.py      ← consulta BD de ventas (SQLite)
│   ├── rag_tool.py      ← búsqueda en política de BI (RAG + ChromaDB)
│   └── web_tool.py      ← búsqueda web (Tavily)
├── rag/
│   ├── docs/            ← documentos .docx indexados por RAG
│   │   └── Política_de_Business_Intelligence_AndeanFoods.docx
│   └── chroma/          ← BD vectorial (generada al arrancar, no subir a git)
├── data/
│   └── ventas_hist.db   ← BD SQLite con ventas 2023-2026
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example         ← plantilla de variables de entorno
└── README.md
```

---

## Setup local

**1. Instalar dependencias**

```bash
uv add fastapi uvicorn anthropic langchain langchain-core langchain-anthropic \
       langchain-chroma langchain-huggingface langchain-text-splitters \
       langchain-community chromadb sentence-transformers pydantic \
       tavily-python docx2txt langgraph pandas python-dotenv
```

**2. Crear el archivo `.env`**

```bash
cp .env.example .env
# editar .env con tus API keys reales
```

**3. Levantar el servidor**

```bash
uvicorn main:app --reload
```

El servidor tarda ~30 segundos en arrancar la primera vez porque:
- Carga el documento Word y lo divide en chunks
- Genera embeddings con `all-MiniLM-L6-v2`
- Indexa en ChromaDB

Las siguientes ejecuciones son más rápidas porque ChromaDB persiste en `rag/chroma/`.

---

## Probar la API

**Documentación interactiva:**
```
http://localhost:8000/docs
```

**Health check:**
```bash
curl http://localhost:8000/
```

**Preguntas de ejemplo:**

```bash
# datos de ventas internos
curl -X POST http://localhost:8000/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿Cuál fue la división con mayor venta en 2024?\"}"

curl -X POST http://localhost:8000/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿Cómo evolucionaron las ventas de CONFITES por canal en 2023?\"}"

curl -X POST http://localhost:8000/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"Compara las ventas de LIMA vs PROVINCIA en el primer semestre de 2025\"}"

# política de BI interna
curl -X POST http://localhost:8000/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿Cuál es la metodología recomendada para desarrollar un dashboard?\"}"

curl -X POST http://localhost:8000/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿Qué colores están permitidos en los reportes de Power BI?\"}"

curl -X POST http://localhost:8000/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿Qué es una tabla de medidas y por qué es importante?\"}"

# contexto externo (web)
curl -X POST http://localhost:8000/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿Cómo está el mercado de harinas industriales en Perú actualmente?\"}"

# combinadas (SQL + web)
curl -X POST http://localhost:8000/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿Cuánto vendió la división de MASCOTAS en 2024 y cuál es la tendencia del sector?\"}"
```

---

## Deploy con Docker

**Construir la imagen:**
```bash
docker build -t asistente-bi-andeanfoods:latest .
```

**Correr el contenedor:**
```bash
docker run -d \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e TAVILY_API_KEY=tvly-... \
  --name asistente-bi \
  asistente-bi-andeanfoods:latest
```

**Ver logs:**
```bash
docker logs asistente-bi
```

**Detener:**
```bash
docker stop asistente-bi && docker rm asistente-bi
```

---

## Datos disponibles en la BD

| Dimensión | Valores |
|---|---|
| canal | LIMA, PROVINCIA, MODERNO, FOOD SERVICE, OTROS |
| division | 000-HARINAS INDUSTRIALES, 001-ALIMENTOS, 002-CONFITES, 003-MASCOTAS |
| periodo | 2023-01 a 2026-06 (42 meses) |
| venta | monto en soles (texto con comas, ej: "270,850") |

**Nota sobre el campo venta:** al hacer consultas SQL usar:
```sql
CAST(REPLACE(venta,',','') AS REAL)
```

---

## Agregar nuevos documentos al RAG

Solo copiar el archivo `.docx` a `rag/docs/` y reiniciar el servidor.
El pipeline carga automáticamente todos los `.docx` que encuentre en esa carpeta.

---

*Python AI Developer 2026 · IES Cibertec · Proyecto Integrador*
