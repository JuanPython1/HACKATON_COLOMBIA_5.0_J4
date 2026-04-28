from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wifi_ai_agents.utils.data_processor import WiFiDataProcessor
from wifi_ai_agents.agents.conversational_agent import ConversationalAgent
from wifi_ai_agents.agents.strategic_agent import StrategicAgent

app = FastAPI(title="WiFi AI Agents API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

data_path = os.path.join(os.path.dirname(__file__), "../Context/Zonas-WiFi-Inteligentes-main")
dp = WiFiDataProcessor(data_path)
dp.load_data()
conversational_agent = ConversationalAgent(dp)
strategic_agent = StrategicAgent(dp)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "appJ4.html"))

@app.get("/dashboard")
async def dashboard():
    return FileResponse(os.path.join(os.path.dirname(__file__), "dashboard.html"))

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    response = conversational_agent.process_query(request.query)
    return QueryResponse(response=response)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/map-data")
async def get_map_data():
    """Retorna datos de APs con coordenadas para el mapa"""
    coords = strategic_agent.get_ap_coordinates()
    ap_status = dp.get_ap_status_summary()
    priority_scores = dp.get_investment_priority_score()
    
    map_data = []
    for ap_name, coord in coords.items():
        ap_info = dp.aps_df[dp.aps_df['ap_name'] == ap_name]
        status = ap_info['status'].iloc[0] if not ap_info.empty else 'unknown'
        
        # Obtener métricas
        metrics = dp.get_ap_traffic_metrics(ap_name)
        
        # Obtener prioridad
        priority_row = priority_scores[priority_scores['ap_name'] == ap_name]
        priority = float(priority_row['priority_score'].iloc[0]) if not priority_row.empty else 0.0
        
        map_data.append({
            'name': ap_name,
            'lat': coord['lat'],
            'lng': coord['lng'],
            'zone': coord['zone'],
            'status': status,
            'clients': int(metrics['total_unique_clients']) if metrics else 0,
            'events': int(metrics['avg_events']) if metrics else 0,
            'disconnection_rate': round(metrics['avg_disconnection_rate'], 2) if metrics else 0,
            'priority': round(priority, 1)
        })
    
    return JSONResponse(content=map_data)

@app.get("/api/aps")
async def get_aps():
    """Retorna lista de APs con su estado"""
    return dp.aps_df.to_dict(orient='records')

@app.get("/api/kpi-data")
async def get_kpi_data():
    """Retorna KPIs calculados para el dashboard estratégico"""
    ap_status = dp.get_ap_status_summary()
    total_aps = len(dp.aps_df)
    online_aps = ap_status.get('online', 0)
    offline_aps = ap_status.get('offline', 0) + ap_status.get('dormant', 0)
    
    map_data_res = strategic_agent.get_ap_coordinates()
    total_clients = 0
    total_disconnection = 0
    count = 0
    
    for ap_name in map_data_res:
        metrics = dp.get_ap_traffic_metrics(ap_name)
        if metrics:
            total_clients += int(metrics['total_unique_clients'])
            total_disconnection += metrics['avg_disconnection_rate']
            count += 1
    
    avg_disconnection = (total_disconnection / count) if count > 0 else 0
    
    inclusion_index = round((online_aps / total_aps) * 10, 1) if total_aps > 0 else 0
    digital_gap = round((offline_aps / total_aps) * 100, 1) if total_aps > 0 else 0
    roi = round(1 + (1 - avg_disconnection) * 2.5, 1)
    
    return JSONResponse(content={
        'inclusion_index': inclusion_index,
        'inclusion_delta': '+0%',
        'total_clients': total_clients,
        'reach_delta': '+0%',
        'roi': roi,
        'roi_status': 'Estable' if roi > 3 else 'Bajo',
        'digital_gap': digital_gap,
        'gap_delta': f'{digital_gap}%',
        'total_aps': total_aps,
        'online_aps': online_aps,
        'offline_aps': offline_aps
    })
