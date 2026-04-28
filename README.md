# CaliWiFi Inclusivo - Cyber-Ops Dashboard

Dashboard de monitoreo y análisis inteligente para zonas WiFi de Cali, con agentes de IA para operaciones, conversación y estrategia.

## Requisitos

- Python 3.8+
- pip

## Instalación y ejecución

```bash
# 1. Entrar a la carpeta del proyecto
cd wifi_ai_agents

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar servidor API (desde la carpeta wifi_ai_agents)
python -m uvicorn api:app --port 8000
```

## Acceso al Dashboard

Abre en el navegador:
```
http://127.0.0.1:8000
```

## Agentes Disponibles

### 1. Agente Operacional
- Monitoreo en tiempo real de Access Points (APs)
- Tabla con tasas de desconexión, estados y número de clientes
- Alertas automáticas para zonas críticas
- Generación de órdenes de mantenimiento

### 2. Agente Conversacional
Chatbot técnico que responde consultas como:
- "¿Qué AP presentan más inestabilidad?"
- "¿Qué zonas concentran más clientes?"
- "¿En qué horas aumenta la desconexión?"
- "¿Qué señales permiten anticipar fallas?"
- "¿Cómo priorizar mantenimiento?"

### 3. Agente Estratégico
- Mapa de equidad digital con coordenadas por zona
- KPIs en tiempo real (Índice de Inclusión, Alcance Digital, ROI, Brecha Digital)
- Ranking de prioridad de inversión
- Recomendaciones estratégicas automáticas

## Estructura del Proyecto

```
wifi_ai_agents/
├── api.py                      # API FastAPI con endpoints REST
├── appJ4.html                 # Dashboard frontend (HTML/JS/CSS)
├── agents/
│   ├── conversational_agent.py # Agente conversacional
│   └── strategic_agent.py     # Agente estratégico
├── utils/
│   └── data_processor.py      # Procesador de datos CSV
└── requirements.txt           # Dependencias Python
```

## Fuente de Datos

Los datos se cargan automáticamente desde:
```
Context/Zonas-WiFi-Inteligentes-main/
├── access_points_curated.csv
├── network_events_curated.csv
├── clients_curated.csv
└── ap_hourly_metrics_curated.csv
```

## Endpoints de la API

- `GET /` - Dashboard principal
- `GET /health` - Estado de la API
- `POST /chat` - Consultas al agente conversacional
- `GET /api/map-data` - Datos para el mapa y tablas
- `GET /api/kpi-data` - KPIs para el agente estratégico
- `GET /api/aps` - Lista completa de APs
