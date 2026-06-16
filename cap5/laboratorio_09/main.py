import os
import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from schemas import RequestChat, ResponseChat

load_dotenv()

app = FastAPI(
    title="Chat API con streaming",
    description="API de chat con Claude Haiku. Soporta respuesta completa y streaming de tokens.",
    version="1.0.0",
)

# el cliente se crea una vez al iniciar la app, no en cada request
cliente = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODELO = "claude-haiku-4-5-20251001"


@app.get("/")
def raiz():
    """Health check — verifica que la API está corriendo."""
    return {"estado": "ok", "modelo": MODELO}


@app.post("/chat", response_model=ResponseChat)
def chat_completo(request: RequestChat):
    """
    Endpoint de chat sin streaming.
    El cliente espera hasta recibir la respuesta completa.
    Útil para casos donde se necesita procesar la respuesta completa antes de mostrarla.
    """
    mensajes = [
        {"role": m.role, "content": m.content}
        for m in request.historial
    ]
    mensajes.append({"role": "user", "content": request.mensaje})

    try:
        respuesta = cliente.messages.create(
            model=MODELO,
            messages=mensajes,
            max_tokens=request.max_tokens,
            temperature=request.temperatura,
        )
        return ResponseChat(
            respuesta=respuesta.content[0].text,
            tokens_usados=respuesta.usage.input_tokens + respuesta.usage.output_tokens,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
def chat_stream(request: RequestChat):
    """
    Endpoint de chat con streaming de tokens.
    Usa Server-Sent Events (SSE): el servidor mantiene la conexión abierta
    y envía cada token apenas el LLM lo genera.
    El cliente recibe el primer token en ~200ms en vez de esperar 3-5 segundos.
    """
    mensajes = [
        {"role": m.role, "content": m.content}
        for m in request.historial
    ]
    mensajes.append({"role": "user", "content": request.mensaje})

    def generador_tokens():
        """
        Generador que emite tokens en formato SSE.
        Formato de cada evento: data: <token>\n\n
        Señal de fin de stream: data: [DONE]\n\n
        """
        try:
            with cliente.messages.stream(
                model=MODELO,
                messages=mensajes,
                max_tokens=request.max_tokens,
                temperature=request.temperatura,
            ) as stream:
                for token in stream.text_stream:
                    yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: ERROR: {e}\n\n"

    return StreamingResponse(
        generador_tokens(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            # desactiva el buffering de proxies nginx — necesario para que
            # los tokens lleguen inmediatamente y no en bloques
            "X-Accel-Buffering": "no",
        },
    )
