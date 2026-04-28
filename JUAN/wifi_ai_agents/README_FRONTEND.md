# WiFi AI Agents - Frontend Chatbot

Interfaz web conversacional para el sistema de agentes de IA de Zonas WiFi Inteligentes.

## Requisitos

- Python 3.8+
- Los archivos CSV en `../Context/Zonas-WiFi-Inteligentes-main/`

## Instalación

```bash
cd wifi_ai_agents
pip install -r requirements.txt
```

## Ejecución

```bash
python -m uvicorn api:app --reload --port 8000
```

Luego abre en el navegador:
```
http://localhost:8000
```

## Preguntas Guía Disponibles

El chatbot responde las 5 preguntas del hackathon:

1. **¿Qué AP presentan más inestabilidad o desconexiones?**
2. **¿Qué zonas concentran más clientes y tráfico?**
3. **¿En qué horas aumenta la autenticación o la desconexión?**
4. **¿Qué señales permiten anticipar fallas o congestión?**
5. **¿Cómo priorizar mantenimiento o inversión usando estos datos?**

También puedes preguntar por el estado de un AP específico o pedir un resumen general.

## Archivos

- `api.py` - Servidor FastAPI que expone el endpoint `/chat`
- `chat.html` - Interfaz web del chatbot
- `agents/conversational_agent.py` - Lógica del agente conversacional

## Endpoints API

- `GET /` - Sirve la interfaz web del chatbot
- `POST /chat` - Procesa consultas conversacionales
  ```json
  {"query": "¿Qué AP presentan más inestabilidad?"}
  ```
- `GET /health` - Estado del servidor
