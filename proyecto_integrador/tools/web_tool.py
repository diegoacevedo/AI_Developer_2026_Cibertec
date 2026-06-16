import os
from langchain_core.tools import tool
from langchain_tavily import TavilySearch


@tool
def buscar_web(query: str) -> str:
    """
    Busca información actual en internet sobre mercados, precios de commodities,
    tendencias del sector alimenticio, noticias de la industria o cualquier
    contexto externo que no esté en la base de datos interna ni en la política de BI.
    """
    cliente = TavilySearch(
        max_results=3,
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
    )
    resultado = cliente.invoke(query)
    return str(resultado)