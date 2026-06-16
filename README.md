# Python AI Developer 2026
### por Diego Acevedo Yamashiro

---

## Descripción

Curso práctico de desarrollo de aplicaciones con Inteligencia Artificial usando Python. El alumno pasa de entender cómo funcionan los LLMs hasta desplegar un sistema de IA completo en producción.

---

## Estructura del curso

| Capítulo | Tema | Labs |
|---|---|---|
| 1 | LLMs y ecosistema Python | Lab 01, Lab 02 |
| 2 | Prompt Engineering & Fine-tuning | Lab 03, Lab 04 |
| 3 | RAG — Retrieval-Augmented Generation | Lab 05, Lab 06 |
| 4 | Agentes de IA y orquestación | Lab 07, Lab 08 |
| 5 | Deploy y producción | Lab 09, Lab 10 |
| PF | Proyecto Final integrador | — |

---

## Stack tecnológico

```
LLMs:        Anthropic Claude, Llama 3 via Groq/HuggingFace
Agentes:     LangChain, LangGraph
RAG:         ChromaDB, sentence-transformers, LangChain
Fine-tuning: HuggingFace transformers, PEFT, TRL, LoRA
API:         FastAPI, Uvicorn, Pydantic
Deploy:      Docker, Docker Compose
Herramientas: uv, Python 3.12, Jupyter, VS Code
```

---

## Setup inicial

**1. Clonar el repositorio**
```bash
git clone <url-del-repo>
cd ai-developer-2026
```

**2. Crear el entorno virtual con uv**
```bash
uv init
uv venv
```

**3. Crear el archivo `.env`**
```bash
cp .env.example .env
# completar con las API keys
```

**4. Variables de entorno requeridas**
```
ANTHROPIC_API_KEY=sk-ant-...   # console.anthropic.com
HF_TOKEN=hf_...                # huggingface.co/settings/tokens
TAVILY_API_KEY=tvly-...        # tavily.com (gratuito)
```

---

## Estructura de carpetas

```
ai-developer-2026/
├── cap01/
│   ├── laboratorio 01.ipynb
│   ├── laboratorio 02.ipynb
│   └── tarea01/
├── cap02/
│   ├── laboratorio 03.ipynb
│   ├── laboratorio 04.ipynb
│   └── tarea02/
├── cap03/
│   ├── laboratorio 05.ipynb
│   ├── laboratorio 06.ipynb
│   └── tarea03/
├── cap04/
│   ├── laboratorio 07.ipynb
│   ├── laboratorio 08.ipynb
│   └── tarea04/
├── cap05/
│   ├── laboratorio 09/
│   ├── laboratorio 10/
│   └── tarea05/
├── proyecto_final/
├── .env.example
├── .gitignore
└── README.md
```

---

## Costo estimado del curso

| Servicio | Costo |
|---|---|
| Anthropic Claude Haiku | ~$5 USD total |
| OpenAI GPT mini | ~$5 USD total |
| HuggingFace Inference API | Gratuito |
| Groq (Llama) | Gratuito |
| Tavily Search | Gratuito (1000 búsquedas/mes) |
| Google Colab (Cap 2) | Gratuito |

---

## .gitignore recomendado

```
.env
__pycache__/
*.pyc
.venv/
chroma*/
*.db
```

---

*Python AI Developer 2026*
