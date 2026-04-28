# Paquete de datos – Hackathon Zonas WiFi Inteligentes

## Contenido
- `network_events_curated.csv`
- `clients_curated.csv`
- `access_points_curated.csv`
- `ap_hourly_metrics_curated.csv`
- `data_dictionary.csv`
- `baseline_dashboard.html`

## Descripción general
Este paquete reúne datos anonimizados de una red de Zonas WiFi públicas basados en exportes de Cisco Meraki. El objetivo es permitir a los equipos construir prototipos de monitoreo, analítica, alertas, visualización y modelos de predicción o detección de anomalías.

## Supuestos y transformaciones
- El archivo original de eventos no incluía año en la marca de tiempo. Se normalizó asumiendo **2026**.
- Las MAC de clientes fueron anonimizadas mediante hash para generar `client_id`.
- El campo `Usage` de clientes fue convertido a MB en `usage_mb`.
- Se generó una tabla derivada por hora (`ap_hourly_metrics_curated.csv`) para acelerar el trabajo de los equipos.

## Resumen rápido del paquete
- Eventos: 5,500
- Clientes: 752
- Puntos de acceso: 23
- Estados de AP: {'online': 17, 'dormant': 3, 'offline': 3}
- Rango temporal de eventos: 2026-03-20 a 2026-04-28
- Top 5 AP por eventos: 072_Hormiguero_AP1, 059_El Saladito-AP1, 060_Felidia-AP2, 060_Felidia-AP1, 061_La Leonera-AP1

## Preguntas guía sugeridas
1. ¿Qué AP presentan más inestabilidad o desconexiones?
2. ¿Qué zonas concentran más clientes y tráfico?
3. ¿En qué horas aumenta la autenticación o la desconexión?
4. ¿Qué señales permiten anticipar fallas o congestión?
5. ¿Cómo priorizar mantenimiento o inversión usando estos datos?

## Limitaciones
- No se incluyen coordenadas exactas ni contexto sociodemográfico.
- El historial de conectividad de AP se conserva como texto exportado.
- La muestra representa una ventana parcial del comportamiento real de la red.
