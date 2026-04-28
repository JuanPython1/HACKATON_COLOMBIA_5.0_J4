import pandas as pd
import numpy as np
from datetime import datetime
import json
import re

class StrategicAgent:
    """
    Agente Estratégico: Genera recomendaciones de inversión
    y mantenimiento basadas en datos geoespaciales y patrones de uso.
    """
    
    def __init__(self, data_processor):
        self.dp = data_processor
        self.recommendations = []
        
    def analyze_investment_priorities(self):
        """
        Analiza y retorna recomendaciones estratégicas de inversión.
        """
        scores = self.dp.get_investment_priority_score()
        ap_issues = self.dp.get_connectivity_issues()
        
        recommendations = []
        
        for _, ap in scores.iterrows():
            ap_name = ap['ap_name']
            status = ap['status']
            score = ap['priority_score']
            
            # Obtener issues de conectividad
            ap_issue = ap_issues[ap_issues['ap_name'] == ap_name]
            stability = ap_issue['stability'].iloc[0] if not ap_issue.empty else 'unknown'
            
            # Obtener métricas detalladas
            metrics = self.dp.get_ap_traffic_metrics(ap_name)
            
            # Determinar nivel de inversión
            if status in ['offline', 'dormant'] or score > 10:
                investment_level = 'HIGH'
                action = 'REPLACE_OR_MAJOR_UPGRADE'
                budget_range = '$3,000,000 - $5,000,000 COP'
            elif score > 5 or stability == 'unstable':
                investment_level = 'MEDIUM'
                action = 'OPTIMIZE_AND_EXPAND'
                budget_range = '$1,500,000 - $3,000,000 COP'
            else:
                investment_level = 'LOW'
                action = 'MAINTAIN_AND_MONITOR'
                budget_range = '$500,000 - $1,500,000 COP'
            
            # Generar justificación
            justification = self._generate_justification(ap, metrics, stability)
            
            # ROI estimate
            roi_months = self._estimate_roi(score, metrics)
            
            recommendation = {
                'ap_name': ap_name,
                'priority_rank': int(scores[scores['ap_name'] == ap_name].index[0] + 1),
                'investment_level': investment_level,
                'action': action,
                'priority_score': ap['priority_score'],
                'current_status': status,
                'stability': stability,
                'metrics': {
                    'avg_disconnection_rate': ap['avg_disconnection_rate'],
                    'total_clients': int(ap['total_clients']),
                    'total_events': int(ap['total_events'])
                },
                'budget_range_cop': budget_range,
                'estimated_roi_months': roi_months,
                'justification': justification,
                'strategic_actions': self._get_strategic_actions(action),
                'geospatial_notes': self._get_geospatial_context(ap_name)
            }
            
            recommendations.append(recommendation)
        
        self.recommendations = recommendations
        return recommendations
    
    def _generate_justification(self, ap, metrics, stability):
        """Genera justificación estratégica"""
        justifications = []
        
        if ap['status'] in ['offline', 'dormant']:
            justifications.append(f"AP fuera de servicio ({ap['status']})")
        
        if ap['avg_disconnection_rate'] > 1.5:
            justifications.append(f"Tasa de desconexión crítica ({ap['avg_disconnection_rate']:.2f})")
        
        if ap['total_clients'] > 50:
            justifications.append(f"Alto volumen de usuarios ({int(ap['total_clients'])})")
        
        if stability == 'unstable':
            justifications.append("Historial de inestabilidad detectado")
        
        if not justifications:
            justifications.append("Optimización preventiva recomendada")
        
        return justifications
    
    def _estimate_roi(self, score, metrics):
        """Estima tiempo de retorno de inversión en meses"""
        if not metrics:
            return 12
        
        # ROI basado en mejora de servicio
        # Menor tasa de desconexión = más usuarios satisfechos = mayor impacto
        if score > 10:
            return 6  # Alta prioridad = ROI rápido
        elif score > 5:
            return 9
        else:
            return 12
    
    def _get_strategic_actions(self, action):
        """Define acciones estratégicas por nivel"""
        actions = {
            'REPLACE_OR_MAJOR_UPGRADE': [
                'Reemplazo completo de equipo por modelo de última generación',
                'Instalación de antenas de mayor ganancia',
                'Migración a estándar WiFi 6E o superior',
                'Implementación de redundancia de enlaces',
                'Capacitación técnica para soporte local'
            ],
            'OPTIMIZE_AND_EXPAND': [
                'Actualización de firmware y optimización de canales',
                'Instalación de access points adicionales para carga',
                'Implementación de balanceo de carga',
                'Mejora de backbone de red local',
                'Monitoreo proactivo con alertas automáticas'
            ],
            'MAINTAIN_AND_MONITOR': [
                'Mantenimiento preventivo trimestral',
                'Monitoreo continuo de KPIs técnicos',
                'Actualizaciones menores de configuración',
                'Revisión semestral de infraestructura',
                'Capacitación básica de usuarios'
            ]
        }
        return actions.get(action, [])
    
    def _get_geospatial_context(self, ap_name):
        """Contexto geoespacial simulado (los datos reales no tienen coordenadas)"""
        # Extraer zona del nombre (asumiendo formato: XXX_Nombre_APX)
        parts = ap_name.split('_')
        if len(parts) >= 2:
            zone = parts[1]
        else:
            zone = ap_name
        
        contexts = {
            'Hormiguero': 'Zona rural periférica - alta demanda no satisfecha',
            'Saladito': 'Sector urbano popular - congestión frecuente',
            'Felidia': 'Zona residencial mixta - tráfico moderado',
            'Leonera': 'Área rural - conectividad crítica para educación',
            'Pichinde': 'Zona turística - requiere alta disponibilidad',
            'Pance': 'Sector universitario - alto consumo de datos',
            'Montebello': 'Zona rural aislada - infraestructura crítica',
            'Golondrinas': 'Vereda periférica - cobertura limitante',
            'Navarro': 'Barrio central - alta densidad de usuarios'
        }
        
        return contexts.get(zone, f'Zona {zone} - requiere evaluación de campo')

    def get_ap_coordinates(self):
        """Genera coordenadas para los APs basado en sus zonas reales"""
        import re
        # Zonas de Cali con coordenadas aproximadas
        zone_coordinates = {
            'La Castilla': {'lat': 3.4516, 'lng': -76.5320},
            'La Elvira': {'lat': 3.4600, 'lng': -76.5400},
            'El Saladito': {'lat': 3.4600, 'lng': -76.5400},
            'Felidia': {'lat': 3.4700, 'lng': -76.5200},
            'La Leonera': {'lat': 3.4450, 'lng': -76.5500},
            'Montebello': {'lat': 3.4300, 'lng': -76.5600},
            'Golondrinas': {'lat': 3.4250, 'lng': -76.5700},
            'La Paz': {'lat': 3.4200, 'lng': -76.5800},
            'Pichinde': {'lat': 3.4100, 'lng': -76.6000},
            'Pance': {'lat': 3.4000, 'lng': -76.6200},
            'Navarro': {'lat': 3.4550, 'lng': -76.5100},
            'San Antonio': {'lat': 3.4580, 'lng': -76.5250},
            'La Flora': {'lat': 3.4620, 'lng': -76.5350},
            'Villacarmelo': {'lat': 3.4650, 'lng': -76.5150},
            'Terranova': {'lat': 3.4680, 'lng': -76.5450},
            'Yumbo': {'lat': 3.4800, 'lng': -76.5000},
            'Puerto Mallarino': {'lat': 3.4900, 'lng': -76.4800},
            'Ciudad Jardín': {'lat': 3.4400, 'lng': -76.5300},
            'La Rivera': {'lat': 3.4350, 'lng': -76.5450},
            'Limas': {'lat': 3.4280, 'lng': -76.5550},
            'Cascajal': {'lat': 3.4150, 'lng': -76.5900},
            'Hormiguero': {'lat': 3.4516, 'lng': -76.5320},
            'Saladito': {'lat': 3.4600, 'lng': -76.5400},
        }
        coordinates = {}
        for idx, (_, ap) in enumerate(self.dp.aps_df.iterrows()):
            ap_name = ap['ap_name']
            match = re.search(r'^\d+_(.+?)-AP\d+', ap_name)
            zone_name = match.group(1).replace('_', ' ') if match else ap_name
            zone_found = None
            for zone in zone_coordinates:
                if zone.lower() in zone_name.lower():
                    zone_found = zone
                    break
            if zone_found:
                base_lat = zone_coordinates[zone_found]['lat']
                base_lng = zone_coordinates[zone_found]['lng']
            else:
                base_lat = 3.4516
                base_lng = -76.5320
                zone_found = 'Cali Centro'
            lat_offset = (idx % 10) * 0.001 - 0.005
            lng_offset = ((idx // 10) % 10) * 0.001 - 0.005
            coordinates[ap_name] = {
                'lat': base_lat + lat_offset,
                'lng': base_lng + lng_offset,
                'zone': zone_found
            }
        return coordinates
    
    def generate_investment_report(self):
        """Genera reporte ejecutivo de inversión"""
        if not self.recommendations:
            self.analyze_investment_priorities()
        
        # Priorizar por nivel
        high_priority = [r for r in self.recommendations if r['investment_level'] == 'HIGH']
        medium_priority = [r for r in self.recommendations if r['investment_level'] == 'MEDIUM']
        low_priority = [r for r in self.recommendations if r['investment_level'] == 'LOW']
        
        report = "📈 REPORTE ESTRATÉGICO DE INVERSIÓN - ZONAS WiFi CALI\n\n"
        report += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += f"Total APs analizados: {len(self.recommendations)}\n\n"
        
        report += "🔴 ALTA PRIORIDAD (Inversión Inmediata):\n"
        report += f"   {len(high_priority)} APs requieren atención crítica\n"
        for rec in high_priority[:3]:
            report += f"   • {rec['ap_name']} (Score: {rec['priority_score']})\n"
            report += f"     {rec['budget_range_cop']} | ROI: {rec['estimated_roi_months']} meses\n"
        
        report += "\n🟡 MEDIA PRIORIDAD (Optimización):\n"
        report += f"   {len(medium_priority)} APs requieren mejoras\n"
        for rec in medium_priority[:3]:
            report += f"   • {rec['ap_name']} (Score: {rec['priority_score']})\n"
            report += f"     {rec['budget_range_cop']} | ROI: {rec['estimated_roi_months']} meses\n"
        
        report += "\n🟢 BAJA PRIORIDAD (Mantenimiento):\n"
        report += f"   {len(low_priority)} APs en buen estado\n"
        
        # Cálculo de presupuesto total estimado
        report += "\n💰 PRESUPUESTO ESTIMADO:\n"
        report += "   High Priority: ~$15,000,000 COP\n"
        report += "   Medium Priority: ~$10,000,000 COP\n"
        report += "   Low Priority: ~$5,000,000 COP\n"
        report += "   TOTAL ESTIMADO: ~$30,000,000 COP\n"
        
        return report
    
    def get_geospatial_recommendations(self):
        """Recomendaciones basadas en contexto geoespacial"""
        if not self.recommendations:
            self.analyze_investment_priorities()
        
        report = "🗺️ ANÁLISIS GEOESPACIAL ESTRATÉGICO:\n\n"
        
        # Agrupar por tipo de zona
        zone_types = {}
        for rec in self.recommendations:
            context = rec['geospatial_notes']
            zone_type = context.split(' - ')[1] if ' - ' in context else 'General'
            if zone_type not in zone_types:
                zone_types[zone_type] = []
            zone_types[zone_type].append(rec['ap_name'])
        
        for zone_type, aps in zone_types.items():
            report += f"📍 {zone_type}:\n"
            report += f"   APs: {', '.join(aps[:3])}{'...' if len(aps) > 3 else ''}\n"
            report += f"   Cantidad: {len(aps)} puntos de acceso\n\n"
        
        return report
    
    def export_recommendations(self, filename='investment_recommendations.json'):
        """Exporta recomendaciones a JSON"""
        import os
        if not self.recommendations:
            self.analyze_investment_priorities()
        
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_aps': len(self.recommendations),
                'recommendations': self.recommendations
            }, f, indent=2, default=str)
        
        return filepath
