import re
from datetime import datetime

class ConversationalAgent:
    """
    Agente Conversacional: Responde preguntas en lenguaje natural
    sobre el rendimiento técnico de las zonas WiFi.
    """
    
    def __init__(self, data_processor):
        self.dp = data_processor
        self.intents = {
            'unstable_aps': ['inestable', 'inestabilidad', 'desconexión', 'desconexiones', 'fallas', 'falla', 'unstable', 'disconnection'],
            'top_zones': ['zonas', 'concentran', 'clientes', 'tráfico', 'top', 'zones', 'clients', 'traffic'],
            'peak_hours': ['horas', 'pico', 'aumenta', 'autenticación', 'desconexión', 'peak', 'hours'],
            'failure_signals': ['señales', 'anticipar', 'fallas', 'congestión', 'signals', 'predict', 'failure'],
            'investment': ['inversión', 'mantenimiento', 'priorizar', 'inversion', 'investment', 'maintenance'],
            'ap_status': ['estado', 'status', 'online', 'offline', 'dormant', 'ap'],
            'general': ['resumen', 'general', 'summary']
        }
    
    def process_query(self, query):
        """
        Procesa una consulta en lenguaje natural y retorna una respuesta.
        """
        query_lower = query.lower()
        intent = self._identify_intent(query_lower)
        
        if intent == 'unstable_aps':
            return self._answer_unstable_aps()
        elif intent == 'top_zones':
            return self._answer_top_zones()
        elif intent == 'peak_hours':
            return self._answer_peak_hours()
        elif intent == 'failure_signals':
            return self._answer_failure_signals()
        elif intent == 'investment':
            return self._answer_investment_priority()
        elif intent == 'ap_status':
            return self._answer_ap_status(query_lower)
        elif intent == 'general':
            return self._answer_general_summary()
        else:
            return self._answer_unknown(query)
    
    def _identify_intent(self, query):
        """Identifica la intención de la consulta basada en palabras clave"""
        matches = {}
        for intent, keywords in self.intents.items():
            score = sum(1 for kw in keywords if kw in query)
            if score > 0:
                matches[intent] = score
        
        if matches:
            return max(matches, key=matches.get)
        return 'unknown'
    
    def _answer_unstable_aps(self):
        """Responde: ¿Qué AP presentan más inestabilidad o desconexiones?"""
        high_disc = self.dp.get_high_disconnection_aps(threshold=1.0)
        anomalies = self.dp.detect_anomalies_iqr()
        
        response = "📊 ANÁLISIS DE ESTABILIDAD DE APs:\n\n"
        
        # APs con alta tasa de desconexión
        response += "🔴 APs con tasa de desconexión > 1.0:\n"
        if not high_disc.empty:
            for _, row in high_disc.sort_values('disconnection_rate', ascending=False).head(5).iterrows():
                response += f"  • {row['ap_name']}: {row['disconnection_rate']:.2f} tasa de desconexión "
                response += f"({row['total_disconnections']} desconexiones / {row['total_connections']} conexiones)\n"
        else:
            response += "  No se encontraron APs con tasa > 1.0\n"
        
        # APs offline/dormant
        offline = self.dp.aps_df[~self.dp.aps_df['status'].isin(['online'])]
        if not offline.empty:
            response += "\n🔴 APs fuera de servicio:\n"
            for _, ap in offline.iterrows():
                response += f"  • {ap['ap_name']}: estado {ap['status']}\n"
        
        return response
    
    def _answer_top_zones(self):
        """Responde: ¿Qué zonas concentran más clientes y tráfico?"""
        # Extraer zona del nombre del AP (primeros 3 dígitos + nombre)
        ap_traffic = self.dp.metrics_df.groupby('ap_name').agg({
            'unique_clients': 'sum',
            'total_events': 'sum'
        }).reset_index()
        
        # Extraer zona (asumiendo formato: XXX_Nombre_APX)
        ap_traffic['zone'] = ap_traffic['ap_name'].apply(lambda x: x.split('_')[1] if '_' in x else x)
        zone_traffic = ap_traffic.groupby('zone').agg({
            'unique_clients': 'sum',
            'total_events': 'sum'
        }).sort_values('unique_clients', ascending=False)
        
        response = "📍 ZONAS CON MAYOR CONCENTRACIÓN:\n\n"
        response += "Top 5 zonas por clientes únicos:\n"
        for zone, row in zone_traffic.head(5).iterrows():
            response += f"  • {zone}: {int(row['unique_clients'])} clientes, {int(row['total_events'])} eventos\n"
        
        return response
    
    def _answer_peak_hours(self):
        """Responde: ¿En qué horas aumenta la autenticación o desconexión?"""
        hourly = self.dp.get_hourly_patterns()
        
        response = "⏰ PATRONES POR HORA:\n\n"
        response += "Horas con más eventos:\n"
        for hour, row in hourly.head(5).iterrows():
            response += f"  • {hour}:00 hrs: {int(row['total_events'])} eventos "
            response += f"({int(row['total_connections'])} conexiones, {int(row['total_disconnections'])} desconexiones)\n"
        
        # Hora pico de conexión
        peak_conn = hourly['total_connections'].idxmax()
        peak_disc = hourly['total_disconnections'].idxmax()
        
        response += f"\n🔹 Hora pico de conexiones: {peak_conn}:00 hrs"
        response += f"\n🔹 Hora pico de desconexiones: {peak_disc}:00 hrs"
        
        return response
    
    def _answer_failure_signals(self):
        """Responde: ¿Qué señales permiten anticipar fallas o congestión?"""
        response = "⚠️ SEÑALES DE ALERTA ANTICIPADA:\n\n"
        
        # 1. Tasas de desconexión crecientes
        response += "1. Tasas de desconexión > 1.5:\n"
        high = self.dp.get_high_disconnection_aps(1.5)
        if not high.empty:
            for _, row in high.head(3).iterrows():
                response += f"   • {row['ap_name']}: {row['disconnection_rate']:.2f}\n"
        else:
            response += "   No hay tasas críticas actualmente\n"
        
        # 2. APs con historial inestable
        issues = self.dp.get_connectivity_issues()
        unstable = issues[issues['stability'] == 'unstable']
        if not unstable.empty:
            response += "\n2. APs con historial inestable:\n"
            for _, row in unstable.head(3).iterrows():
                response += f"   • {row['ap_name']}: {row['offline_events']} eventos offline\n"
        
        # 3. Señales técnicas de eventos
        disc_events = self.dp.get_disconnection_events()
        response += f"\n3. Eventos de desconexión recientes: {len(disc_events)}\n"
        response += "   Causas comunes: 'client not responding', 'deauthenticated', 'previous auth expired'\n"
        
        return response
    
    def _answer_investment_priority(self):
        """Responde: ¿Cómo priorizar mantenimiento o inversión?"""
        scores = self.dp.get_investment_priority_score()
        
        response = "💰 PRIORIZACIÓN DE INVERSIÓN:\n\n"
        response += "Top 5 APs prioritarios para inversión:\n"
        
        for _, row in scores.head(5).iterrows():
            response += f"  • {row['ap_name']}:\n"
            response += f"    Score: {row['priority_score']}/100 | "
            response += f"Estado: {row['status']} | "
            response += f"Tasa desc: {row['avg_disconnection_rate']:.2f}\n"
        
        return response
    
    def _answer_ap_status(self, query):
        """Responde sobre estado de APs específicos"""
        # Buscar si mencionan un AP específico
        ap_names = self.dp.aps_df['ap_name'].tolist()
        mentioned_ap = None
        
        for ap in ap_names:
            if ap.lower() in query:
                mentioned_ap = ap
                break
        
        if mentioned_ap:
            metrics = self.dp.get_ap_traffic_metrics(mentioned_ap)
            ap_info = self.dp.aps_df[self.dp.aps_df['ap_name'] == mentioned_ap].iloc[0]
            
            response = f"📡 ESTADO DE {mentioned_ap}:\n\n"
            response += f"  • Estado general: {ap_info['status']}\n"
            if metrics:
                response += f"  • Promedio eventos/hora: {metrics['avg_events']:.1f}\n"
                response += f"  • Tasa desconexión promedio: {metrics['avg_disconnection_rate']:.2f}\n"
                response += f"  • Total clientes únicos: {int(metrics['total_unique_clients'])}\n"
                response += f"  • Horas con anomalías: {metrics['anomaly_hours']}\n"
            return response
        else:
            # Resumen general de estados
            status = self.dp.get_ap_status_summary()
            response = "📡 RESUMEN DE ESTADOS DE APs:\n\n"
            for status_val, count in status.items():
                response += f"  • {status_val}: {count} APs\n"
            return response
    
    def _answer_general_summary(self):
        """Resumen general del sistema"""
        status = self.dp.get_ap_status_summary()
        total_events = len(self.dp.events_df)
        total_clients = len(self.dp.clients_df)
        
        response = "📊 RESUMEN GENERAL DE ZONAS WiFi:\n\n"
        response += f"  • Total de APs: {len(self.dp.aps_df)}\n"
        response += f"  • APs Online: {status.get('online', 0)}\n"
        response += f"  • APs Offline: {status.get('offline', 0)}\n"
        response += f"  • APs Dormant: {status.get('dormant', 0)}\n"
        response += f"  • Total eventos registrados: {total_events}\n"
        response += f"  • Total clientes únicos: {total_clients}\n"
        
        return response
    
    def _answer_unknown(self, query):
        """Respuesta para consultas no reconocidas"""
        return f"""❓ No pude interpretar tu consulta: "{query}"

Preguntas que puedo responder:
  • ¿Qué AP presentan más inestabilidad?
  • ¿Qué zonas concentran más clientes?
  • ¿En qué horas aumenta la autenticación?
  • ¿Qué señales permiten anticipar fallas?
  • ¿Cómo priorizar mantenimiento?
  • ¿Cuál es el estado de [AP]?
  • Dame un resumen general"""
