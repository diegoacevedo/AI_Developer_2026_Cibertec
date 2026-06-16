"""
main.py — API FastAPI del proyecto integrador.

Expone un endpoint POST /preguntar que recibe una pregunta en lenguaje natural
y la procesa con el agente ReAct, que decide autónomamente entre:
  - consultar_ventas:   datos históricos de ventas (SQLite)
  - consultar_politica: política de BI de Andean Foods (RAG sobre .docx)
  - buscar_web:         contexto de mercado externo (Tavily)
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from tools.rag_tool import build_rag_pipeline
from agente import crear_agente, ejecutar_pregunta

load_dotenv()

assert os.getenv("ANTHROPIC_API_KEY"), "Falta ANTHROPIC_API_KEY en .env"
assert os.getenv("TAVILY_API_KEY"),    "Falta TAVILY_API_KEY en .env"

# estado global — se inicializa en el lifespan
_agente = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Se ejecuta al INICIAR el servidor.
    Construye el pipeline RAG y crea el agente una sola vez.
    """
    global _agente
    print("Iniciando pipeline RAG...")
    build_rag_pipeline()
    print("Creando agente...")
    _agente = crear_agente()
    print("Servidor listo.")
    yield


app = FastAPI(
    title="Asistente BI — Andean Foods",
    description=(
        "Agente de IA que responde preguntas sobre ventas históricas y "
        "estándares de Business Intelligence de Andean Foods."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


class RequestPregunta(BaseModel):
    pregunta: str = Field(..., min_length=5, max_length=500)


class ResponseRespuesta(BaseModel):
    pregunta: str
    respuesta: str


@app.get("/")
def raiz():
    """Health check."""
    return {
        "estado": "ok",
        "agente_listo": _agente is not None,
        "herramientas": ["consultar_ventas", "consultar_politica", "buscar_web"],
    }


@app.post("/preguntar", response_model=ResponseRespuesta)
def preguntar(request: RequestPregunta):
    """
    Procesa una pregunta en lenguaje natural con el agente ReAct.
    El agente decide autónomamente qué herramienta usar.
    """
    if _agente is None:
        raise HTTPException(status_code=503, detail="Agente no inicializado aún.")
    try:
        respuesta = ejecutar_pregunta(_agente, request.pregunta)
        return ResponseRespuesta(pregunta=request.pregunta, respuesta=respuesta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
