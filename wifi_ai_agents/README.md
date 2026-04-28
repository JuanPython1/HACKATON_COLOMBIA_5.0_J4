# 🤖 Sistema de Agentes de IA para Zonas WiFi Inteligentes

## Resumen del Proyecto

Sistema desarrollado para el Hackathon Colombia 5.0 que implementa tres agentes de IA autónomos para optimizar la conectividad pública en Cali.

## Estructura del Sistema

```
wifi_ai_agents/
├── main.py                    # Orquestador principal del sistema
├── agents/
│   ├── operative_agent.py     # Agente 1: Detección de anomalías y órdenes de trabajo
│   ├── conversational_agent.py # Agente 2: Q&A en lenguaje natural
│   └── strategic_agent.py     # Agente 3: Recomendaciones de inversión
├── utils/
│   └── data_processor.py     # Procesamiento y análisis de datos
├── data/
│   ├── work_orders.json      # Órdenes de trabajo generadas
│   └── investment_recommendations.json  # Recomendaciones de inversión
├── dashboard.html            # Dashboard visual para el jurado
└── requirements.txt         # Dependencias (pandas, numpy)
```

## Los 3 Agentes de IA

### 1. 🔧 Agente Operativo
**Función:** Detección de anomalías y creación de órdenes de trabajo automáticas.

**Capacidades:**
- Detecta APs offline/dormant en tiempo real
- Identifica tasas de desconexión anómalas (>1.5)
- Detecta anomalías estadísticas usando método IQR
- Genera órdenes de trabajo con prioridad CRÍTICA/MEDIA/BAJA
- Exporta órdenes a JSON para sistemas de gestión

**Salida:** 22 alertas detectadas, 6 críticas (APs offline/dormant)

### 2. 💬 Agente Conversacional
**Función:** Responde preguntas en lenguaje natural sobre rendimiento técnico.

**Preguntas que puede responder:**
- ¿Qué AP presentan más inestabilidad?
- ¿Qué zonas concentran más clientes y tráfico?
- ¿En qué horas aumenta la autenticación o desconexión?
- ¿Qué señales permiten anticipar fallas?
- ¿Cómo priorizar mantenimiento usando estos datos?
- ¿Cuál es el estado de [AP específico]?

**Tecnología:** Procesamiento de lenguaje natural basado en intents y palabras clave

### 3. 💰 Agente Estratégico
**Función:** Recomendaciones de inversión y mantenimiento basadas en datos.

**Análisis realizado:**
- Score de prioridad basado en: tasa de desconexión (40%), volumen de clientes (30%), eventos (30%)
- Clasificación en 3 niveles: ALTA/MEDIA/BAJA prioridad
- Contexto geoespacial simulado por zona
- Estimación de ROI (6-12 meses)
- Presupuesto estimado por nivel de inversión

**Resultado:** 23 APs evaluados, presupuesto total estimado: $30,000,000 COP

## Datos Utilizados

- **network_events_curated.csv:** 5,500 eventos de red (Mar 20 - Abr 28, 2026)
- **clients_curated.csv:** 752 clientes únicos
- **access_points_curated.csv:** 23 puntos de acceso (17 online, 3 offline, 3 dormant)
- **ap_hourly_metrics_curated.csv:** 1,253 registros horarios agregados

## Hallazgos Clave

1. **APs Críticos Offline:** 067_Montebello-AP1, 068_Golondrinas-AP1, 069_La Paz-AP1
2. **Mayor Tráfico:** 072_Hormiguero_AP1 (639 clientes, 2,278 eventos)
3. **Hora Pico:** 21:00 hrs (985 eventos, pico de desconexiones)
4. **Tasa de Desconexión Crítica:** 072_Hormiguero_AP1 (1.74 promedio)

## Cómo Ejecutar

```bash
cd wifi_ai_agents
source venv/bin/activate
python main.py
```

## Entregables para el Jurado

1. **Solución Tecnológica:** Sistema funcional con 3 agentes de IA implementados en Python
2. **Dashboard:** Archivo `dashboard.html` con visualización de resultados
3. **Datos Exportados:** 
   - `data/work_orders.json` - Órdenes de trabajo
   - `data/investment_recommendations.json` - Recomendaciones de inversión

## Impacto Esperado

- **Reducción de tiempo de detección:** De días a minutos
- **Optimización de recursos:** Inversión dirigida por datos ($30M COP estimado)
- **Mejora en servicio:** Reducción de tasas de desconexión mediante mantenimiento preventivo
- **Escalabilidad:** Arquitectura de agentes permite agregar nuevas capacidades

## Tecnologías Utilizadas

- **Python 3:** Lenguaje principal
- **Pandas/NumPy:** Procesamiento y análisis de datos
- **Algoritmos propios:** Detección de anomalías IQR, scoring de prioridad, procesamiento de lenguaje natural
- **HTML/CSS:** Dashboard visual

## Duración del Hackathon

Sistema desarrollado en tiempo real durante el Hackathon Colombia 5.0 - Cali 2026.
