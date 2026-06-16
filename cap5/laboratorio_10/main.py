import os
import glob
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# pipeline RAG — se inicializa una vez al arrancar el servidor
# y se reutiliza en cada request (los embeddings y la BD no se recargan)
pipeline_rag = None


def construir_pipeline():
    """
    Carga los documentos de /app/docs/, genera embeddings y construye
    el pipeline RAG completo. Se ejecuta una sola vez al iniciar.
    """
    print("Cargando documentos...")
    todos_los_docs = []
    for ruta in sorted(glob.glob("/app/docs/*.txt")):
        nombre = ruta.split("/")[-1]
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        todos_los_docs.append(Document(page_content=contenido, metadata={"fuente": nombre}))
    print(f"  {len(todos_los_docs)} documentos cargados")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(todos_los_docs)
    print(f"  {len(chunks)} chunks generados")
    # all-MiniLM-L6-v2 se descarga automáticamente la primera vez
    # en builds posteriores usa el caché de la imagen
    print("Cargando modelo de embedding...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="/app/chroma")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        temperature=0.1,
        max_tokens=500)

    prompt = ChatPromptTemplate.from_template("""
Eres un asistente técnico de TechCorp. Responde usando ÚNICAMENTE el contexto dado.
Si la respuesta no está en el contexto, di: "No encuentro esa información en el manual."

Contexto:
{contexto}

Pregunta: {pregunta}
Respuesta:
""")

    pipeline = (
        {
            "contexto": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
            "pregunta": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("Pipeline RAG listo")
    return pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    # se ejecuta al INICIAR el servidor — construye el pipeline una sola vez
    global pipeline_rag
    pipeline_rag = construir_pipeline()
    yield
    # se ejecuta al APAGAR el servidor — aquí iría limpieza si fuera necesaria


app = FastAPI(
    title="RAG API — TechCorp",
    description="Asistente técnico de TechCorp basado en RAG sobre manuales internos.",
    version="1.0.0",
    lifespan=lifespan,
)


class RequestPregunta(BaseModel):
    pregunta: str


class ResponseRespuesta(BaseModel):
    pregunta: str
    respuesta: str


@app.get("/")
def raiz():
    """Health check — verifica que la API y el pipeline están listos."""
    return {
        "estado": "ok",
        "pipeline": "RAG TechCorp",
        "pipeline_listo": pipeline_rag is not None,
    }


@app.post("/preguntar", response_model=ResponseRespuesta)
def preguntar(request: RequestPregunta):
    """
    Responde preguntas sobre los manuales internos de TechCorp usando RAG.
    El modelo solo responde con información de los documentos indexados.
    """
    if pipeline_rag is None:
        raise HTTPException(status_code=503, detail="Pipeline no inicializado aún.")
    try:
        respuesta = pipeline_rag.invoke(request.pregunta)
        return ResponseRespuesta(pregunta=request.pregunta, respuesta=respuesta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
