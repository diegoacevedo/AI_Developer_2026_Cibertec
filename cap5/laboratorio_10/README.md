# Laboratorio  — Dockerizar la app RAG del Capítulo 3
### Python AI Developer 2026 · Capítulo 5: Deploy y producción

---

## Estructura del proyecto

```
lab09_docker_rag/
├── main.py           ← API FastAPI con el pipeline RAG completo
├── requirements.txt  ← dependencias Python con versiones fijas
├── Dockerfile        ← instrucciones para construir la imagen
├── .dockerignore     ← archivos a excluir de la imagen
├── README.md         ← este archivo
└── docs/             ← documentos de TechCorp (indexados al arrancar)
    ├── manual_servidores.txt
    ├── manual_seguridad.txt
    ├── manual_deploy.txt
    ├── manual_monitoreo.txt
    └── manual_rrhh.txt
```

---

## Prerequisito

Tener Docker Desktop instalado y corriendo.
Verificar con: `docker --version`

---

## Paso 1 — Construir la imagen

Desde la carpeta `lab09_docker_rag/`:

```bash
docker build -t rag-techcorp:latest .
```

**Qué hace este comando:**
- Lee el `Dockerfile` línea por línea
- Descarga la imagen base `python:3.12-slim`
- Instala las librerías del `requirements.txt`
- Copia el código y los documentos dentro de la imagen

**Tiempo estimado:** 5-10 minutos la primera vez (descarga librerías de ML).
Las builds siguientes son rápidas porque Docker cachea las capas.

Verificar que la imagen se creó:

```bash
docker images rag-techcorp
```

---

## Paso 2 — Correr el contenedor

```bash
docker run -d -p 8001:8000 -e ANTHROPIC_API_KEY=tu_api_key_aqui --name rag-techcorp rag-techcorp:latest
```

**Explicación de los flags:**
- `-d` — modo detached, corre en background
- `-p 8001:8000` — mapea el puerto 8001 del host al 8000 del contenedor
- `-e ANTHROPIC_API_KEY=...` — pasa la API key como variable de entorno (nunca en la imagen)
- `--name rag-techcorp` — nombre del contenedor para referenciarlo fácilmente

**Nota:** el contenedor tarda ~30 segundos en estar listo porque carga los embeddings al arrancar.

---

## Paso 3 — Verificar que arrancó correctamente

Ver los logs del contenedor:

```bash
docker logs rag-techcorp
```

Deberías ver algo como:
```
Cargando documentos...
  5 documentos cargados
  23 chunks generados
Cargando modelo de embedding...
Pipeline RAG listo
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Paso 4 — Probar la API

**Health check:**

```bash
curl http://localhost:8001/
```

Respuesta esperada:
```json
{"estado": "ok", "pipeline": "RAG TechCorp", "pipeline_listo": true}
```

**Documentación interactiva** (en el browser):

```
http://localhost:8001/docs
```

**Hacer una pregunta al RAG:**

```bash
curl -X POST http://localhost:8001/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿En qué días se pueden hacer deploys a producción?\"}"
```

```bash
curl -X POST http://localhost:8001/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿Cuántos caracteres debe tener una contraseña?\"}"
```

```bash
curl -X POST http://localhost:8001/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿Cuántos días de vacaciones tienen los empleados?\"}"
```

```bash
curl -X POST http://localhost:8001/preguntar -H "Content-Type: application/json" -d "{\"pregunta\": \"¿Cuál es el salario de los ingenieros?\"}"
```

La última pregunta no está en ningún documento — el modelo debe responder que no encuentra la información.

---

## Paso 5 — Comandos de gestión del contenedor

```bash
# ver contenedores corriendo
docker ps

# ver uso de CPU y memoria del contenedor
docker stats rag-techcorp --no-stream

# detener el contenedor
docker stop rag-techcorp

# eliminar el contenedor (la imagen sigue disponible)
docker rm rag-techcorp

# volver a correrlo
docker run -d -p 8001:8000 -e ANTHROPIC_API_KEY=... --name rag-techcorp rag-techcorp:latest

# eliminar la imagen
docker rmi rag-techcorp:latest
```

---

## Por qué este orden en el Dockerfile importa

```dockerfile
# CORRECTO — dependencias primero
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .          # si cambias el código, Docker reutiliza la capa de pip
```

```dockerfile
# INCORRECTO — todo junto
COPY . .
RUN pip install -r requirements.txt   # reinstala TODO cada vez que cambias el código
```

Docker construye las imágenes en capas y cachea cada una. Si copias el código antes de instalar las dependencias, cualquier cambio en el código invalida el caché de pip y reinstala todo desde cero.

---

## Por qué la API key NO va en la imagen

Si incluyes la API key en el Dockerfile o en el código:
- Queda grabada en la imagen permanentemente
- Cualquiera que descargue la imagen puede extraerla
- Si subes la imagen a Docker Hub (público), la key queda expuesta

La práctica correcta es pasarla en tiempo de ejecución con `-e`:
```bash
docker run -e ANTHROPIC_API_KEY=sk-ant-... rag-techcorp:latest
```

Así la imagen es genérica y reutilizable — la key solo existe en el contenedor en ejecución.

---

## Preguntas de reflexión

1. ¿Qué pasaría si eliminas el contenedor con `docker rm` y lo vuelves a crear?
   ¿Se pierde la BD vectorial de ChromaDB?

2. ¿Qué ventaja tiene Docker para desplegar esta app en un servidor cloud vs
   copiar los archivos directamente?

3. El `requirements.txt` tiene versiones fijas (ej: `fastapi==0.115.0`).
   ¿Por qué es importante fijar versiones en producción?

---

*Laboratorio 09 — Python AI Developer 2026 · IES Cibertec*
