# frontend/app.py
import streamlit as st
import httpx

st.title("Asistente BI — Andean Foods")

if "historial" not in st.session_state:
    st.session_state.historial = []

# mostrar historial de conversación
for msg in st.session_state.historial:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# input del usuario
if pregunta := st.chat_input("Escribe tu pregunta..."):
    st.session_state.historial.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.write(pregunta)

    # llamar a la API FastAPI
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            r = httpx.post(
                "http://localhost:8000/preguntar",
                json={"pregunta": pregunta},
                timeout=60,
            )
            respuesta = r.json()["respuesta"]
        st.write(respuesta)
    st.session_state.historial.append({"role": "assistant", "content": respuesta})