import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

class WiFiDataProcessor:
    def __init__(self, data_path="../Zonas-WiFi-Inteligentes-main"):
        self.data_path = data_path
        self.events_df = None
        self.clients_df = None
        self.aps_df = None
        self.metrics_df = None
        
    def load_data(self):
        """Carga todos los datasets"""
        self.events_df = pd.read_csv(f"{self.data_path}/network_events_curated.csv")
        self.clients_df = pd.read_csv(f"{self.data_path}/clients_curated.csv")
        self.aps_df = pd.read_csv(f"{self.data_path}/access_points_curated.csv")
        self.metrics_df = pd.read_csv(f"{self.data_path}/ap_hourly_metrics_curated.csv")
        
        # Convertir timestamps
        self.events_df['timestamp'] = pd.to_datetime(self.events_df['timestamp'])
        self.metrics_df['timestamp_hour'] = pd.to_datetime(self.metrics_df['timestamp_hour'])
        self.clients_df['last_seen'] = pd.to_datetime(self.clients_df['last_seen'])
        
        return self
    
    def get_ap_status_summary(self):
        """Resumen del estado de los APs"""
        return self.aps_df['status'].value_counts().to_dict()
    
    def get_events_by_ap(self, ap_name=None):
        """Eventos por AP, opcionalmente filtrado"""
        if ap_name:
            return self.events_df[self.events_df['ap_name'] == ap_name]
        return self.events_df.groupby('ap_name').size().sort_values(ascending=False)
    
    def get_disconnection_events(self):
        """Filtrar eventos de desconexión"""
        return self.events_df[
            (self.events_df['event_type'].str.contains('disassociation|deauthenticated', na=False)) |
            (self.events_df['event_detail'].str.contains('deauthenticated|left AP|expired', na=False))
        ]
    
    def get_high_disconnection_aps(self, threshold=1.0):
        """APs con tasa de desconexión alta"""
        return self.metrics_df[self.metrics_df['disconnection_rate'] > threshold]
    
    def get_hourly_patterns(self):
        """Patrones por hora del día"""
        self.metrics_df['hour'] = self.metrics_df['timestamp_hour'].dt.hour
        return self.metrics_df.groupby('hour').agg({
            'total_events': 'sum',
            'total_connections': 'sum',
            'total_disconnections': 'sum',
            'unique_clients': 'sum'
        }).sort_values('total_events', ascending=False)
    
    def get_ap_traffic_metrics(self, ap_name):
        """Métricas de tráfico para un AP específico"""
        ap_metrics = self.metrics_df[self.metrics_df['ap_name'] == ap_name]
        if ap_metrics.empty:
            return None
        return {
            'avg_events': ap_metrics['total_events'].mean(),
            'avg_connections': ap_metrics['total_connections'].mean(),
            'avg_disconnections': ap_metrics['total_disconnections'].mean(),
            'avg_disconnection_rate': ap_metrics['disconnection_rate'].mean(),
            'total_unique_clients': ap_metrics['unique_clients'].sum(),
            'anomaly_hours': len(ap_metrics[ap_metrics['disconnection_rate'] > 1.5])
        }
    
    def detect_anomalies_iqr(self, ap_name=None):
        """Detección de anomalías usando IQR"""
        if ap_name:
            data = self.metrics_df[self.metrics_df['ap_name'] == ap_name]['disconnection_rate'].dropna()
        else:
            data = self.metrics_df['disconnection_rate'].dropna()
        
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = self.metrics_df[
            (self.metrics_df['disconnection_rate'] < lower_bound) |
            (self.metrics_df['disconnection_rate'] > upper_bound)
        ]
        return anomalies
    
    def get_connectivity_issues(self):
        """Analizar historial de conectividad de APs"""
        issues = []
        for _, ap in self.aps_df.iterrows():
            history = ap['connectivity_history']
            if pd.isna(history):
                continue
            entries = history.split(',')
            status_changes = len(entries) // 3
            offline_events = len([e for e in entries if '0' in e or '2' in e or '5' in e])
            issues.append({
                'ap_name': ap['ap_name'],
                'status': ap['status'],
                'total_events': status_changes,
                'offline_events': offline_events,
                'stability': 'unstable' if offline_events > 5 else 'stable'
            })
        return pd.DataFrame(issues)
    
    def get_investment_priority_score(self):
        """Calcular score de prioridad para inversión"""
        ap_scores = []
        
        for _, ap in self.aps_df.iterrows():
            ap_name = ap['ap_name']
            ap_metrics = self.metrics_df[self.metrics_df['ap_name'] == ap_name]
            
            if ap_metrics.empty:
                continue
                
            # Factores: tasa de desconexión, volumen de clientes, estado actual
            avg_disc_rate = ap_metrics['disconnection_rate'].mean()
            total_clients = ap_metrics['unique_clients'].sum()
            total_events = ap_metrics['total_events'].sum()
            
            # Score: mayor desconexión + más clientes = mayor prioridad
            score = (avg_disc_rate * 0.4 + 
                    (total_clients / self.metrics_df['unique_clients'].sum() * 100) * 0.3 +
                    (total_events / self.metrics_df['total_events'].sum() * 100) * 0.3)
            
            ap_scores.append({
                'ap_name': ap_name,
                'status': ap['status'],
                'priority_score': round(score, 2),
                'avg_disconnection_rate': round(avg_disc_rate, 2),
                'total_clients': total_clients,
                'total_events': total_events
            })
        
        return pd.DataFrame(ap_scores).sort_values('priority_score', ascending=False)
