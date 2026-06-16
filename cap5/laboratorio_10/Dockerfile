# imagen base: Python 3.12 slim (sin herramientas de desarrollo, más liviana)
FROM python:3.12-slim

# directorio de trabajo dentro del contenedor
WORKDIR /app

# instalar dependencias del sistema que necesita sentence-transformers
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# copiar requirements ANTES que el código
# Docker cachea esta capa — si solo cambia el código, no reinstala las librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar el código y los documentos
COPY main.py .
COPY docs/ ./docs/

# crear carpeta para que ChromaDB persista la BD vectorial dentro del contenedor
RUN mkdir -p /app/chroma

# puerto que expone la aplicación
EXPOSE 8000

# comando para iniciar el servidor
# --host 0.0.0.0 es obligatorio para que sea accesible desde fuera del contenedor
# sin esto, el servidor escucha solo en localhost dentro del contenedor y no es alcanzable
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
