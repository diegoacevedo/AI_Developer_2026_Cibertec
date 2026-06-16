"""
agente.py — el agente ReAct central del proyecto integrador.
Recibe una pregunta y decide autónomamente qué herramienta usar.
"""
import os
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from tools.sql_tool import consultar_ventas
from tools.rag_tool import consultar_politica
from tools.web_tool import buscar_web


def crear_agente():
    """
    Crea y devuelve el agente ReAct con las 3 herramientas disponibles.
    Se llama una vez al iniciar la app (via lifespan de FastAPI).
    """
    llm = ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0,
        max_tokens=1500,
    )

    tools = [consultar_ventas, consultar_politica, buscar_web]

    agente = create_react_agent(
        llm,
        tools,
        prompt=(
            "Eres un asistente analítico de Andean Foods especializado en ventas y estándares de BI. "
            "Tienes acceso a tres herramientas:\n"
            "- consultar_ventas: para preguntas sobre datos históricos de ventas (montos, canales, divisiones, periodos)\n"
            "- consultar_politica: para preguntas sobre lineamientos, metodología y estándares de BI de la empresa\n"
            "- buscar_web: para información de mercado externo, precios o contexto del sector\n\n"
            "Usa la herramienta correcta para cada pregunta. "
            "Si la pregunta combina datos internos y contexto externo, usa más de una herramienta. "
            "Si puedes responder con tu conocimiento propio, hazlo directamente sin usar herramientas. "
            "Responde siempre en español de forma clara y concisa."
        ),
    )

    return agente


def ejecutar_pregunta(agente, pregunta: str) -> str:
    """
    Ejecuta el agente con una pregunta y devuelve la respuesta final.
    """
    resultado = agente.invoke({"messages": [{"role": "user", "content": pregunta}]})

    # extraer el último mensaje del agente como respuesta final
    for msg in reversed(resultado["messages"]):
        if type(msg).__name__ == "AIMessage" and not getattr(msg, "tool_calls", None):
            # content puede ser lista (versiones recientes de langchain-anthropic)
            if isinstance(msg.content, list):
                for bloque in msg.content:
                    if isinstance(bloque, dict) and bloque.get("type") == "text":
                        return bloque["text"]
                    elif isinstance(bloque, str):
                        return bloque
            return msg.content

    return "No se pudo obtener una respuesta."
