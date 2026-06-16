"""
tools/rag_tool.py — herramienta RAG sobre la Política de Business Intelligence de Andean Foods.

Carga el documento Word de la política, lo divide en chunks, lo indexa en ChromaDB
y expone una función de búsqueda semántica que el agente puede invocar.

El pipeline se inicializa una sola vez (build_rag_pipeline) y luego
la herramienta usa el retriever ya construido en cada llamada.
"""
import os
import glob
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import Docx2txtLoader

# directorio de documentos y de persistencia de ChromaDB
DOCS_DIR   = os.path.join(os.path.dirname(__file__), "..", "rag", "docs")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "rag", "chroma")

# retriever global — se asigna al llamar build_rag_pipeline()
_retriever = None


def build_rag_pipeline():
    """
    Carga los documentos .docx de rag/docs/, genera embeddings e indexa en ChromaDB.
    Debe llamarse una vez al iniciar la aplicación.
    """
    global _retriever

    print("RAG: cargando documentos...")
    documentos = []
    for ruta in glob.glob(os.path.join(DOCS_DIR, "*.docx")):
        loader = Docx2txtLoader(ruta)
        docs = loader.load()
        # guardar el nombre del archivo en metadata para trazabilidad
        for doc in docs:
            doc.metadata["fuente"] = os.path.basename(ruta)
        documentos.extend(docs)
    print(f"  {len(documentos)} documento(s) cargado(s)")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(documentos)
    print(f"  {len(chunks)} chunks generados")

    print("RAG: generando embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )

    _retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    print("RAG: pipeline listo")


@tool
def consultar_politica(pregunta: str) -> str:
    """
    Busca información en la Política de Business Intelligence de Andean Foods.
    Usar para preguntas sobre:
    - Metodología de desarrollo de dashboards (CRISP-DM)
    - Lineamientos de diseño: colores, tipografía, logotipo, estructura del lienzo
    - Arquitectura de datos: orígenes, ETL, normalización, modelos dimensionales
    - Buenas prácticas: tabla de tiempos, tabla de medidas, nomenclatura
    - Estándares de Power BI: dim_tiempo, medidas DAX, SharePoint
    """
    if _retriever is None:
        return "El pipeline RAG no está inicializado. Llamar a build_rag_pipeline() primero."

    docs = _retriever.invoke(pregunta)
    if not docs:
        return "No se encontró información relevante en la política de BI."

    # concatenar los chunks recuperados con su fuente
    contexto = "\n\n---\n\n".join(
        f"[{doc.metadata.get('fuente', 'documento')}]\n{doc.page_content}"
        for doc in docs
    )
    return contexto
