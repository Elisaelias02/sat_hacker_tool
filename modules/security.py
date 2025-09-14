import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    """Analizador de seguridad SPARTA simplificado."""
    
    SATELLITE_CATEGORIES = {
        'communication': 'Comunicaciones',
        'earth_observation': 'Observación Terrestre', 
        'navigation': 'Navegación',
        'weather': 'Meteorológico',
        'scientific': 'Científico',
        'military': 'Militar',
        'space_station': 'Estación Espacial'
    }
    
    RISK_COUNTRIES = {
        'high': ['RU', 'CN', 'KP', 'IR'],
        'medium': ['PK', 'IN', 'IL'],
        'low': ['US', 'CA', 'GB', 'FR', 'DE', 'JP', 'AU']
    }
    
    def analyze_satellite(self, satellite_data: Dict) -> Dict:
        """Analiza un satélite y genera evaluación SPARTA."""
        basic_info = satellite_data.get('basic_info', {})
        mission_info = satellite_data.get('mission_info', {})
        
        analysis = {
            'satellite_id': basic_info.get('norad_id'),
            'satellite_name': basic_info.get('name', ''),
            'country': self._determine_country(basic_info),
            'category': self._determine_category(basic_info, mission_info),
            'risk_level': 'low',
            'concerns': [],
            'recommendations': [],
            'confidence': self._calculate_confidence(satellite_data)
        }
        
        # Evaluar riesgo
        analysis['risk_level'] = self._assess_risk(analysis['country'])
        
        # Generar preocupaciones
        analysis['concerns'] = self._generate_concerns(
            analysis['category'], analysis['risk_level'], basic_info
        )
        
        # Generar recomendaciones
        analysis['recommendations'] = self._generate_recommendations(
            analysis['category'], analysis['risk_level']
        )
        
        return analysis
    
    def _determine_country(self, basic_info: Dict) -> str:
        """Determina país de origen."""
        return (basic_info.get('countries') or 
                basic_info.get('inferred_country') or 
                'UNKNOWN')
    
    def _determine_category(self, basic_info: Dict, mission_info: Dict) -> str:
        """Determina categoría del satélite."""
        # Prioridad a datos reales
        sat_type = mission_info.get('type', '').upper()
        if 'COMMUNICATION' in sat_type:
            return 'communication'
        elif 'EARTH' in sat_type or 'OBSERVATION' in sat_type:
            return 'earth_observation'
        elif 'NAVIGATION' in sat_type:
            return 'navigation'
        elif 'WEATHER' in sat_type:
            return 'weather'
        elif 'SCIENTIFIC' in sat_type:
            return 'scientific'
        elif 'MILITARY' in sat_type:
            return 'military'
        
        # Fallback a información inferida
        inferred_type = mission_info.get('inferred_type', '').lower()
        return inferred_type if inferred_type != 'unknown' else 'unknown'
    
    def _assess_risk(self, country: str) -> str:
        """Evalúa nivel de riesgo por país."""
        if any(c in country.upper() for c in self.RISK_COUNTRIES['high']):
            return 'high'
    def _assess_risk(self, country: str) -> str:
        """Evalúa nivel de riesgo por país."""
        if any(c in country.upper() for c in self.RISK_COUNTRIES['high']):
            return 'high'
        elif any(c in country.upper() for c in self.RISK_COUNTRIES['medium']):
            return 'medium'
        elif any(c in country.upper() for c in self.RISK_COUNTRIES['low']):
            return 'low'
        else:
            return 'medium'
    
    def _generate_concerns(self, category: str, risk_level: str, basic_info: Dict) -> List[str]:
        """Genera preocupaciones de seguridad."""
        concerns = []
        
        # Preocupaciones por categoría
        category_concerns = {
            'communication': ["Interceptación de comunicaciones", "Canal para exfiltración de datos"],
            'earth_observation': ["Capacidades de vigilancia", "Recolección de inteligencia geoespacial"],
            'navigation': ["Interferencia con sistemas críticos", "Spoofing de señales GNSS"],
            'military': ["Capacidades militares no declaradas", "Potencial para guerra espacial"],
            'weather': ["Recolección de datos meteorológicos sensibles"]
        }
        
        concerns.extend(category_concerns.get(category, []))
        
        # Preocupaciones por riesgo
        if risk_level == 'high':
            concerns.extend([
                "País de origen clasificado como alto riesgo",
                "Posible uso para actividades de inteligencia"
            ])
        
        # Preocupaciones por operador
        operator = basic_info.get('operator', '')
        if operator and any(word in operator.upper() for word in ['MILITARY', 'DEFENSE']):
            concerns.append("Operador militar identificado")
        
        return concerns
    
    def _generate_recommendations(self, category: str, risk_level: str) -> List[str]:
        """Genera recomendaciones de seguridad."""
        recommendations = []
        
        if risk_level == 'high':
            recommendations.extend([
                "Monitorear actividad satelital de cerca",
                "Implementar contramedidas si es necesario",
                "Evaluar dependencias críticas"
            ])
        
        category_recommendations = {
            'communication': ["Auditar tráfico de comunicaciones sensibles"],
            'earth_observation': ["Evaluar exposición de infraestructura crítica"],
            'navigation': ["Implementar sistemas redundantes"],
            'military': ["Análisis detallado de capacidades"]
        }
        
        recommendations.extend(category_recommendations.get(category, []))
        
        return recommendations
    
    def _calculate_confidence(self, satellite_data: Dict) -> float:
        """Calcula confianza del análisis."""
        score = 0.0
        
        # Puntos por fuentes
        sources = satellite_data.get('sources_used', [])
        score += len(sources) * 0.2  # Máximo 1.0 por 5 fuentes
        
        # Puntos por completitud
        if satellite_data.get('basic_info'):
            score += 0.3
        if satellite_data.get('mission_info'):
            score += 0.3
        if satellite_data.get('tle'):
            score += 0.2
        
        return min(score, 1.0)
    
    def generate_report(self, analysis: Dict) -> str:
        """Genera reporte SPARTA en texto."""
        lines = [
            "=" * 60,
            "ANÁLISIS DE SEGURIDAD SPARTA",
            "=" * 60,
            f"Satélite: {analysis['satellite_name']} (ID: {analysis['satellite_id']})",
            f"País: {analysis['country']}",
            f"Categoría: {self.SATELLITE_CATEGORIES.get(analysis['category'], 'Desconocido')}",
            f"Nivel de Riesgo: {analysis['risk_level'].upper()}",
            f"Confianza: {analysis['confidence']:.1%}",
            ""
        ]
        
        if analysis['concerns']:
            lines.append("PREOCUPACIONES DE SEGURIDAD:")
            for concern in analysis['concerns']:
                lines.append(f"  ⚠ {concern}")
            lines.append("")
        
        if analysis['recommendations']:
            lines.append("RECOMENDACIONES:")
            for rec in analysis['recommendations']:
                lines.append(f"  → {rec}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)
