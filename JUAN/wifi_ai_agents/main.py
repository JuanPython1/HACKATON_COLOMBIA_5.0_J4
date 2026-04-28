import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processor import WiFiDataProcessor
from agents.operative_agent import OperativeAgent
from agents.conversational_agent import ConversationalAgent
from agents.strategic_agent import StrategicAgent
from datetime import datetime

class WiFiAIAgentSystem:
    """
    Sistema principal que orquesta los tres agentes de IA
    para optimizar las Zonas WiFi de Cali.
    """
    
    def __init__(self, data_path="../Context/Zonas-WiFi-Inteligentes-main"):
        print("🚀 Inicializando Sistema de Agentes de IA para Zonas WiFi...\n")
        
        # Inicializar procesador de datos
        self.data_processor = WiFiDataProcessor(data_path)
        self.data_processor.load_data()
        print("✅ Datos cargados exitosamente")
        print(f"   • {len(self.data_processor.events_df)} eventos")
        print(f"   • {len(self.data_processor.clients_df)} clientes")
        print(f"   • {len(self.data_processor.aps_df)} puntos de acceso")
        print(f"   • {len(self.data_processor.metrics_df)} registros horarios\n")
        
        # Inicializar agentes
        self.operative_agent = OperativeAgent(self.data_processor)
        self.conversational_agent = ConversationalAgent(self.data_processor)
        self.strategic_agent = StrategicAgent(self.data_processor)
        
        print("✅ Tres agentes de IA inicializados:")
        print("   • Agente Operativo (detección de anomalías)")
        print("   • Agente Conversacional (Q&A técnico)")
        print("   • Agente Estratégico (recomendaciones de inversión)\n")
    
    def run_operative_analysis(self):
        """Ejecuta el análisis del Agente Operativo"""
        print("=" * 60)
        print("🔧 AGENTE OPERATIVO - DETECCIÓN DE ANOMALÍAS")
        print("=" * 60 + "\n")
        
        # Obtener resumen operativo
        summary = self.operative_agent.get_operative_summary()
        print(f"📊 Resumen Operativo:")
        print(f"   • Total APs: {summary['total_aps']}")
        print(f"   • Online: {summary['aps_online']}")
        print(f"   • Offline: {summary['aps_offline']}")
        print(f"   • Dormant: {summary['aps_dormant']}")
        print(f"   • Alertas totales: {summary['total_alerts']}")
        print(f"   • Alertas críticas: {summary['critical_alerts']}\n")
        
        # Detectar alertas
        alerts = self.operative_agent.detect_real_time_anomalies()
        print(f"⚠️  ALERTAS DETECTADAS: {len(alerts)}\n")
        
        for i, alert in enumerate(alerts[:5], 1):
            print(f"{i}. [{alert['severity']}] {alert['type']}")
            print(f"   AP: {alert['ap_name']}")
            print(f"   {alert['description']}\n")
        
        # Generar órdenes de trabajo
        work_orders = self.operative_agent.generate_work_orders(alerts)
        print(f"📋 ÓRDENES DE TRABAJO GENERADAS: {len(work_orders)}\n")
        
        for wo in work_orders[:3]:
            print(f"   • {wo['order_id']} - {wo['priority']}")
            print(f"     {wo['description']}")
            print(f"     Tiempo estimado: {wo['estimated_time_hours']} hrs\n")
        
        # Exportar
        exported = self.operative_agent.export_work_orders()
        print(f"💾 Órdenes exportadas a: {exported}\n")
        
        return alerts, work_orders
    
    def run_conversational_demo(self):
        """Demuestra el Agente Conversacional con preguntas de ejemplo"""
        print("=" * 60)
        print("💬 AGENTE CONVERSACIONAL - Q&A TÉCNICO")
        print("=" * 60 + "\n")
        
        questions = [
            "¿Qué AP presentan más inestabilidad?",
            "¿Qué zonas concentran más clientes y tráfico?",
            "¿En qué horas aumenta la autenticación o la desconexión?",
            "¿Qué señales permiten anticipar fallas o congestión?",
            "¿Cómo priorizar mantenimiento o inversión usando estos datos?"
        ]
        
        for q in questions:
            print(f"❓ Pregunta: {q}")
            print("-" * 50)
            answer = self.conversational_agent.process_query(q)
            print(answer)
            print("\n" + "=" * 60 + "\n")
    
    def run_strategic_analysis(self):
        """Ejecuta el análisis del Agente Estratégico"""
        print("=" * 60)
        print("💰 AGENTE ESTRATÉGICO - RECOMENDACIONES DE INVERSIÓN")
        print("=" * 60 + "\n")
        
        # Análisis de prioridades
        recommendations = self.strategic_agent.analyze_investment_priorities()
        print(f"📈 ANÁLISIS DE PRIORIZACIÓN: {len(recommendations)} APs evaluados\n")
        
        # Top 5 recomendaciones
        print("Top 5 APs prioritarios para inversión:\n")
        for rec in recommendations[:5]:
            print(f"{rec['priority_rank']}. {rec['ap_name']}")
            print(f"   Nivel: {rec['investment_level']} | Score: {rec['priority_score']}")
            print(f"   Acción: {rec['action']}")
            print(f"   Presupuesto: {rec['budget_range_cop']}")
            print(f"   ROI estimado: {rec['estimated_roi_months']} meses")
            print(f"   Justificación: {', '.join(rec['justification'][:2])}\n")
        
        # Reporte de inversión
        report = self.strategic_agent.generate_investment_report()
        print(report)
        
        # Análisis geoespacial
        geo_report = self.strategic_agent.get_geospatial_recommendations()
        print("\n" + geo_report)
        
        # Exportar
        exported = self.strategic_agent.export_recommendations()
        print(f"\n💾 Recomendaciones exportadas a: {exported}\n")
        
        return recommendations
    
    def interactive_query(self):
        """Modo interactivo para consultas conversacionales"""
        print("=" * 60)
        print("💬 MODO INTERACTIVO - Consultas Técnicas")
        print("=" * 60)
        print("Escribe 'salir' para terminar\n")
        
        while True:
            query = input("🔍 Tu consulta: ")
            if query.lower() in ['salir', 'exit', 'quit']:
                break
            
            answer = self.conversational_agent.process_query(query)
            print("\n" + answer + "\n")
    
    def run_full_demo(self):
        """Ejecuta demostración completa del sistema"""
        print("\n" + "🤖" * 30)
        print("   SISTEMA DE AGENTES DE IA - ZONAS WiFi CALI")
        print("🤖" * 30 + "\n")
        
        # 1. Agente Operativo
        print("\n[1/3] EJECUTANDO AGENTE OPERATIVO...\n")
        self.run_operative_analysis()
        
        # 2. Agente Conversacional
        print("\n[2/3] EJECUTANDO AGENTE CONVERSACIONAL...\n")
        self.run_conversational_demo()
        
        # 3. Agente Estratégico
        print("\n[3/3] EJECUTANDO AGENTE ESTRATÉGICO...\n")
        self.run_strategic_analysis()
        
        print("=" * 60)
        print("✅ DEMOSTRACIÓN COMPLETADA")
        print("=" * 60)
        print("\n📦 Entregables generados:")
        print("   • data/work_orders.json")
        print("   • data/investment_recommendations.json")
        print("\n🎯 Sistema listo para presentación ante el jurado!\n")


if __name__ == "__main__":
    system = WiFiAIAgentSystem()
    system.run_full_demo()
