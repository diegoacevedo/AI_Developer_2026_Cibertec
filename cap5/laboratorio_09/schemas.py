from pydantic import BaseModel, Field


class MensajeChat(BaseModel):
    """Un mensaje individual en la conversación."""
    role: str    # "user" o "assistant"
    content: str


class RequestChat(BaseModel):
    """Request para el endpoint de chat."""
    mensaje: str = Field(..., min_length=1, max_length=2000)
    historial: list[MensajeChat] = []
    temperatura: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=500, ge=1, le=2000)


class ResponseChat(BaseModel):
    """Response del endpoint de chat sin streaming."""
    respuesta: str
    tokens_usados: int
