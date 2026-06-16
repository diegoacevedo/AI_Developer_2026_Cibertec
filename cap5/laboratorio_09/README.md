# Laboratorio 09 — API FastAPI con streaming de tokens en tiempo real
### Python AI Developer 2026 · Capítulo 5: Deploy y producción

---

## Estructura del proyecto

```
lab08_fastapi_streaming/
├── main.py           ← la aplicación FastAPI (endpoints + lógica)
├── schemas.py        ← modelos Pydantic de request/response
├── cliente_prueba.py ← script para probar todos los endpoints
├── .env              ← variables de entorno (crear tú mismo, no subir a git)
└── README.md         ← este archivo
```

---

## Setup

**1. Instalar dependencias**

```bash
uv add fastapi uvicorn httpx anthropic python-dotenv
```

**2. Crear el archivo `.env`** en esta carpeta:

```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Levantar el servidor

```bash
# desde la carpeta lab08_fastapi_streaming/
uvicorn main:app --reload
```

El flag `--reload` activa recarga automática al guardar cambios en el código.

El servidor arranca en `http://localhost:8000`.

---

## Probar la API

**Opción A — Documentación interactiva (recomendado para explorar)**

Abrir en el browser: `http://localhost:8000/docs`

FastAPI genera automáticamente una interfaz Swagger donde puedes probar todos los endpoints sin escribir código.

**Opción B — Script de pruebas**

Con el servidor corriendo, en otra terminal:

```bash
python cliente_prueba.py
```

El script prueba los cuatro casos principales y muestra los resultados.

**Opción C — curl desde terminal**

```bash
# health check
curl http://localhost:8000/

# chat completo
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "¿Qué es FastAPI?", "max_tokens": 100}'

# streaming (los tokens llegan token por token)
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "¿Qué es FastAPI?", "max_tokens": 100}'
```

---

## Los dos endpoints

### `POST /chat` — respuesta completa

El cliente espera hasta recibir toda la respuesta del LLM.

Request:
```json
{
  "mensaje": "texto de la pregunta",
  "historial": [],
  "temperatura": 0.7,
  "max_tokens": 500
}
```

Response:
```json
{
  "respuesta": "texto de la respuesta",
  "tokens_usados": 123
}
```

### `POST /chat/stream` — streaming de tokens

Usa Server-Sent Events (SSE). El servidor mantiene la conexión abierta y envía
cada token apenas el LLM lo genera. El cliente recibe el primer token en ~200ms
en lugar de esperar 3-5 segundos la respuesta completa.

El mismo request que `/chat`. La response es un stream de líneas con formato:
```
data: token1

data: token2

data: [DONE]
```

---

## Por qué importa el streaming

| Métrica              | Sin streaming | Con streaming |
|----------------------|---------------|---------------|
| Tiempo al 1er token  | 3-5 segundos  | ~200ms        |
| Tiempo total         | 3-5 segundos  | 3-5 segundos  |
| Experiencia usuario  | Espera en blanco | Ve tokens llegar |

El tiempo total es el mismo — la diferencia es cuándo el usuario ve la primera respuesta.

---

## Preguntas de reflexión

Responder en celdas Markdown en el notebook de entrega:

1. ¿Cuánto tardó el primer token en el endpoint de streaming vs el tiempo total
   del endpoint sin streaming en tu ejecución?

2. ¿Qué ventaja da Pydantic sobre validar los datos manualmente con `if/else`?

3. La API guarda el `ANTHROPIC_API_KEY` en un `.env`.
   ¿Qué pasaría si este archivo se sube a GitHub? ¿Cómo lo evitarías?

---

*Laboratorio 08 — Python AI Developer 2026 · IES Cibertec*
