# imagen base liviana
FROM python:3.12-slim

WORKDIR /app

# dependencias del sistema para sentence-transformers y docx2txt
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# dependencias Python — van primero para aprovechar el caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# código fuente
COPY main.py .
COPY agente.py .
COPY tools/ ./tools/

# datos y documentos
COPY data/ ./data/
COPY rag/docs/ ./rag/docs/

# carpeta para ChromaDB (se genera al arrancar)
RUN mkdir -p /app/rag/chroma

EXPOSE 8000

# --host 0.0.0.0 es obligatorio para ser accesible desde fuera del contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
