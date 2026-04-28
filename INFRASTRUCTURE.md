# Infraestructura del Proyecto - CaliWiFi Inclusivo

## Visión General

Sistema de monitoreo y análisis inteligente para zonas WiFi de Cali, compuesto por una API backend con agentes de IA integrados y un dashboard frontend servido directamente por la API.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     Usuario (Navegador)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Server (api.py) - Puerto 8000          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────┐  │
│  │ Conversational  │  │ Strategic      │  │ Operative │  │
│  │ Agent           │  │ Agent          │  │ Agent     │  │
│  └─────────────────┘  └─────────────────┘  └───────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          Dashboard (appJ4.html)                      │    │
│  │     Servido directamente por FastAPI                │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Fuente de Datos (CSV Files)                    │
│  Context/Zonas-WiFi-Inteligentes-main/                     │
│  ├── access_points_curated.csv                             │
│  ├── network_events_curated.csv                            │
│  ├── clients_curated.csv                                   │
│  └── ap_hourly_metrics_curated.csv                         │
└─────────────────────────────────────────────────────────────┘
```

## Backend

### Tecnología
- **Lenguaje**: Python 3.8+
- **Framework**: FastAPI
- **Servidor ASGI**: Uvicorn
- **Archivo principal**: `wifi_ai_agents/api.py`

### Endpoints REST
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Dashboard principal (HTML) |
| GET | `/health` | Estado de la API |
| POST | `/chat` | Consultas al agente conversacional |
| GET | `/api/map-data` | Datos para el mapa y tablas |
| GET | `/api/kpi-data` | KPIs para el agente estratégico |
| GET | `/api/aps` | Lista completa de APs |

### Ejecución
```bash
cd wifi_ai_agents
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn api:app --port 8000
```

## Agentes de IA

### 1. Agente Operacional (`agents/operative_agent.py`)
- Monitoreo en tiempo real de Access Points (APs)
- Tabla con tasas de desconexión, estados y número de clientes
- Alertas automáticas para zonas críticas
- Generación de órdenes de mantenimiento

### 2. Agente Conversacional (`agents/conversational_agent.py`)
Chatbot técnico que responde consultas como:
- "¿Qué AP presentan más inestabilidad?"
- "¿Qué zonas concentran más clientes?"
- "¿En qué horas aumenta la desconexión?"
- "¿Qué señales permiten anticipar fallas?"
- "¿Cómo priorizar mantenimiento?"

### 3. Agente Estratégico (`agents/strategic_agent.py`)
- Mapa de equidad digital con coordenadas por zona
- KPIs en tiempo real (Índice de Inclusión, Alcance Digital, ROI, Brecha Digital)
- Ranking de prioridad de inversión
- Recomendaciones estratégicas automáticas

## Frontend

- **Tipo**: Single Page Application servida por FastAPI
- **Archivo**: `wifi_ai_agents/appJ4.html`
- **Tecnologías**: HTML, JavaScript, CSS (vanilla)
- **Acceso**: `http://127.0.0.1:8000`

## Fuente de Datos

Los datos se cargan automáticamente desde archivos CSV ubicados en:
```
Context/Zonas-WiFi-Inteligentes-main/
├── access_points_curated.csv      # Información de puntos de acceso
├── network_events_curated.csv     # Eventos de red
├── clients_curated.csv            # Datos de clientes
└── ap_hourly_metrics_curated.csv  # Métricas horarias por AP
```

## Estructura de Carpetas

```
HACKATON_COLOMBIA_5.0_J4/
├── Context/
│   └── Zonas-WiFi-Inteligentes-main/
│       ├── access_points_curated.csv
│       ├── network_events_curated.csv
│       ├── clients_curated.csv
│       └── ap_hourly_metrics_curated.csv
├── wifi_ai_agents/
│   ├── api.py                      # API FastAPI
│   ├── appJ4.html                 # Dashboard frontend
│   ├── requirements.txt           # Dependencias Python
│   ├── agents/
│   │   ├── conversational_agent.py
│   │   ├── operative_agent.py
│   │   └── strategic_agent.py
│   └── utils/
│       └── data_processor.py      # Procesador de datos CSV
├── README.md
└── INFRASTRUCTURE.md              # Este archivo
```

## Dependencias

Ver `wifi_ai_agents/requirements.txt` para la lista completa de dependencias Python.
