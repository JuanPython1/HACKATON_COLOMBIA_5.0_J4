from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processor import WiFiDataProcessor
from agents.conversational_agent import ConversationalAgent
from agents.strategic_agent import StrategicAgent

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
    
    map_data = []
    for ap_name, coord in coords.items():
        ap_info = dp.aps_df[dp.aps_df['ap_name'] == ap_name]
        status = ap_info['status'].iloc[0] if not ap_info.empty else 'unknown'
        
        # Obtener métricas
        metrics = dp.get_ap_traffic_metrics(ap_name)
        
        map_data.append({
            'name': ap_name,
            'lat': coord['lat'],
            'lng': coord['lng'],
            'zone': coord['zone'],
            'status': status,
            'clients': int(metrics['total_unique_clients']) if metrics else 0,
            'events': int(metrics['total_events']) if metrics else 0,
            'disconnection_rate': round(metrics['avg_disconnection_rate'], 2) if metrics else 0
        })
    
    return JSONResponse(content=map_data)

@app.get("/api/aps")
async def get_aps():
    """Retorna lista de APs con su estado"""
    return dp.aps_df.to_dict(orient='records')
