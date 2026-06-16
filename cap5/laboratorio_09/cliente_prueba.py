"""
cliente_prueba.py — script para probar la API desde terminal.
Ejecutar DESPUÉS de que el servidor esté corriendo con:
    uvicorn main:app --reload

Uso:
    python cliente_prueba.py
"""

import time
import httpx

BASE_URL = "http://localhost:8000"


def test_health_check():
    r = httpx.get(f"{BASE_URL}/")
    print(f"Health check: {r.status_code} → {r.json()}")
    print()


def test_chat_completo():
    """Prueba el endpoint sin streaming — mide tiempo total."""
    print("=== /chat (sin streaming) ===")
    inicio = time.time()

    r = httpx.post(
        f"{BASE_URL}/chat",
        json={
            "mensaje": "Explica qué es una API REST en 3 oraciones.",
            "temperatura": 0.5,
            "max_tokens": 200,
        },
        timeout=30,
    )

    tiempo = time.time() - inicio
    data = r.json()
    print(f"Tiempo hasta respuesta completa: {tiempo:.2f}s")
    print(f"Tokens usados: {data['tokens_usados']}")
    print(f"Respuesta: {data['respuesta']}")
    print()


def test_chat_streaming():
    """Prueba el endpoint con streaming — mide tiempo al primer token."""
    print("=== /chat/stream (con streaming) ===")
    inicio = time.time()
    primer_token_t = None
    tokens = 0

    print("Respuesta (llega token por token):")
    print("-" * 40)

    with httpx.stream(
        "POST",
        f"{BASE_URL}/chat/stream",
        json={
            "mensaje": "Explica qué es una API REST en 3 oraciones.",
            "temperatura": 0.5,
            "max_tokens": 200,
        },
        timeout=60,
    ) as r:
        for linea in r.iter_lines():
            if not linea or not linea.startswith("data:"):
                continue
            token = linea[6:]
            if token == "[DONE]":
                break
            if primer_token_t is None:
                primer_token_t = time.time() - inicio
            tokens += 1
            print(token, end="", flush=True)

    print()
    print("-" * 40)
    print(f"Tiempo al PRIMER token: {primer_token_t:.3f}s")
    print(f"Tiempo TOTAL:           {time.time() - inicio:.2f}s")
    print(f"Tokens recibidos:       {tokens}")
    print()


def test_multi_turno():
    """Prueba conversación multi-turno con historial."""
    print("=== Conversación multi-turno ===")

    r1 = httpx.post(
        f"{BASE_URL}/chat",
        json={"mensaje": "Mi nombre es Diego y trabajo en análisis de datos.", "max_tokens": 80},
        timeout=30,
    )
    respuesta1 = r1.json()["respuesta"]
    print(f"Turno 1 → {respuesta1}")

    r2 = httpx.post(
        f"{BASE_URL}/chat",
        json={
            "mensaje": "¿Cómo me llamo y en qué trabajo?",
            "historial": [
                {"role": "user",      "content": "Mi nombre es Diego y trabajo en análisis de datos."},
                {"role": "assistant", "content": respuesta1},
            ],
            "max_tokens": 80,
        },
        timeout=30,
    )
    print(f"Turno 2 → {r2.json()['respuesta']}")
    print()


def test_validacion():
    """Prueba que Pydantic rechaza requests inválidos."""
    print("=== Validación de requests ===")
    casos = [
        ({"mensaje": ""},                          "mensaje vacío"),
        ({"mensaje": "hola", "temperatura": 2.0}, "temperatura > 1.0"),
        ({"mensaje": "hola", "max_tokens": -1},   "max_tokens negativo"),
    ]
    for payload, descripcion in casos:
        r = httpx.post(f"{BASE_URL}/chat", json=payload, timeout=10)
        print(f"  {descripcion}: status={r.status_code} ({'OK' if r.status_code == 422 else 'FALLO'})")
    print()


if __name__ == "__main__":
    test_health_check()
    test_chat_completo()
    test_chat_streaming()
    test_multi_turno()
    test_validacion()
