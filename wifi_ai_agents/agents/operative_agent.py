import pandas as pd
from datetime import datetime
import json

class OperativeAgent:
    """
    Agente Operativo: Detecta anomalías en tiempo real y genera
    órdenes de trabajo automáticas para mantenimiento.
    """
    
    def __init__(self, data_processor):
        self.dp = data_processor
        self.work_orders = []
        self.anomalies_detected = []
        
    def detect_real_time_anomalies(self):
        """
        Detecta anomalías actuales usando umbrales dinámicos.
        Retorna lista de alertas prioritarias (una por AP).
        """
        alerts = []
        
        # 1. Detectar APs offline/dormant (uno por AP)
        offline_aps = self.dp.aps_df[self.dp.aps_df['status'].isin(['offline', 'dormant'])]
        for _, ap in offline_aps.iterrows():
            alert = {
                'timestamp': datetime.now().isoformat(),
                'ap_name': ap['ap_name'],
                'severity': 'CRITICAL',
                'type': 'AP_OFFLINE',
                'description': f"AP {ap['ap_name']} está en estado {ap['status']}",
                'metrics': {'status': ap['status']}
            }
            alerts.append(alert)
        
        # 2. Detectar tasas de desconexión anómalas (agregado por AP)
        ap_avg_metrics = self.dp.metrics_df.groupby('ap_name').agg({
            'disconnection_rate': 'mean',
            'total_disconnections': 'sum',
            'total_connections': 'sum'
        }).reset_index()
        
        high_disc_aps = ap_avg_metrics[ap_avg_metrics['disconnection_rate'] > 1.5]
        
        for _, row in high_disc_aps.iterrows():
            # No duplicar si ya está offline
            if row['ap_name'] in [a['ap_name'] for a in alerts]:
                continue
            alert = {
                'timestamp': datetime.now().isoformat(),
                'ap_name': row['ap_name'],
                'severity': 'HIGH' if row['disconnection_rate'] > 2.0 else 'MEDIUM',
                'type': 'HIGH_DISCONNECTION_RATE',
                'description': f"AP {row['ap_name']} tiene tasa de desconexión promedio {row['disconnection_rate']:.2f}",
                'metrics': {
                    'disconnection_rate': round(row['disconnection_rate'], 2),
                    'total_disconnections': int(row['total_disconnections']),
                    'total_connections': int(row['total_connections'])
                }
            }
            alerts.append(alert)
        
        # 3. Detectar anomalías estadísticas (IQR) - agregado por AP
        anomalies = self.dp.detect_anomalies_iqr()
        anomalous_aps = anomalies.groupby('ap_name')['disconnection_rate'].mean().reset_index()
        
        for _, row in anomalous_aps.iterrows():
            # No duplicar
            if row['ap_name'] in [a['ap_name'] for a in alerts]:
                continue
            alert = {
                'timestamp': datetime.now().isoformat(),
                'ap_name': row['ap_name'],
                'severity': 'MEDIUM',
                'type': 'STATISTICAL_ANOMALY',
                'description': f"Comportamiento anómalo detectado en {row['ap_name']}",
                'metrics': {
                    'disconnection_rate': round(row['disconnection_rate'], 2)
                }
            }
            alerts.append(alert)
        
        self.anomalies_detected = alerts
        return alerts
    
    def generate_work_orders(self, alerts):
        """
        Genera órdenes de trabajo basadas en las alertas detectadas.
        """
        work_orders = []
        
        for alert in alerts:
            if alert['type'] == 'AP_OFFLINE':
                order = {
                    'order_id': f"WO-{len(work_orders)+1:04d}",
                    'timestamp': alert['timestamp'],
                    'ap_name': alert['ap_name'],
                    'priority': 'CRITICAL',
                    'action': 'SITE_VISIT_REQUIRED',
                    'description': f"Visita técnica urgente - AP {alert['ap_name']} offline",
                    'steps': [
                        'Verificar conexión eléctrica',
                        'Revisar cableado de red',
                        'Reiniciar equipo físicamente',
                        'Verificar configuración de red',
                        'Reportar estado al finalizar'
                    ],
                    'estimated_time_hours': 2.0,
                    'requires_technician': True
                }
                
            elif alert['type'] == 'HIGH_DISCONNECTION_RATE':
                order = {
                    'order_id': f"WO-{len(work_orders)+1:04d}",
                    'timestamp': alert['timestamp'],
                    'ap_name': alert['ap_name'],
                    'priority': alert['severity'],
                    'action': 'OPTIMIZATION_REQUIRED',
                    'description': f"Optimizar configuración - Tasa desconexión {alert['metrics']['disconnection_rate']:.2f}",
                    'steps': [
                        'Analizar logs de autenticación',
                        'Verificar interferencia de canal',
                        'Revisar configuración de potencia',
                        'Actualizar firmware si necesario',
                        'Monitorear por 24 horas'
                    ],
                    'estimated_time_hours': 1.5,
                    'requires_technician': False
                }
                
            elif alert['type'] == 'STATISTICAL_ANOMALY':
                order = {
                    'order_id': f"WO-{len(work_orders)+1:04d}",
                    'timestamp': alert['timestamp'],
                    'ap_name': alert['ap_name'],
                    'priority': 'LOW',
                    'action': 'MONITORING_INCREASED',
                    'description': f"Incrementar monitoreo en {alert['ap_name']}",
                    'steps': [
                        'Revisar métricas cada 15 minutos',
                        'Analizar patrones de tráfico',
                        'Verificar estabilidad de señal',
                        'Documentar comportamiento'
                    ],
                    'estimated_time_hours': 0.5,
                    'requires_technician': False
                }
            else:
                continue
                
            work_orders.append(order)
        
        self.work_orders = work_orders
        return work_orders
    
    def get_operative_summary(self):
        """Resumen operativo del estado actual"""
        alerts = self.detect_real_time_anomalies()
        work_orders = self.generate_work_orders(alerts)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_aps': len(self.dp.aps_df),
            'aps_online': len(self.dp.aps_df[self.dp.aps_df['status'] == 'online']),
            'aps_offline': len(self.dp.aps_df[self.dp.aps_df['status'] == 'offline']),
            'aps_dormant': len(self.dp.aps_df[self.dp.aps_df['status'] == 'dormant']),
            'total_alerts': len(alerts),
            'critical_alerts': len([a for a in alerts if a['severity'] == 'CRITICAL']),
            'work_orders_generated': len(work_orders),
            'critical_orders': len([wo for wo in work_orders if wo['priority'] == 'CRITICAL'])
        }
        
        return summary
    
    def export_work_orders(self, filename='work_orders.json'):
        """Exporta las órdenes de trabajo a JSON"""
        import os
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(self.work_orders, f, indent=2)
        return filepath
