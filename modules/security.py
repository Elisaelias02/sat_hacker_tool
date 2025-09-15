"""
Módulo de evaluación de riesgos satelitales - VERSIÓN CORREGIDA
Inspirado en conceptos del framework SPARTA pero implementando análisis heurístico automatizado.
"""

import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class SatelliteRiskAnalyzer:
    """
    Analizador de riesgos satelitales usando evaluación heurística automatizada.
    
    IMPORTANTE: Este sistema realiza análisis automatizado basado en heurísticas
    y datos públicos. NO es un análisis de TTPs documentadas como SPARTA/MITRE.
    Es una herramienta de screening inicial que requiere validación humana
    para evaluaciones críticas de seguridad.
    
    Inspirado en conceptos del framework SPARTA adaptados al dominio espacial.
    """
    
    SATELLITE_CATEGORIES = {
        'communication': 'Comunicaciones',
        'earth_observation': 'Observación Terrestre', 
        'navigation': 'Navegación',
        'weather': 'Meteorológico',
        'scientific': 'Científico',
        'military': 'Militar',
        'space_station': 'Estación Espacial',
        'unknown': 'Desconocido'
    }
    
    # Clasificación heurística de riesgo por país (basada en políticas espaciales públicas)
    RISK_COUNTRIES = {
        'high': ['RU', 'CN', 'KP', 'IR'],      # Países con políticas espaciales agresivas
        'medium': ['PK', 'IN', 'IL', 'BR'],    # Países con capacidades espaciales en desarrollo
        'low': ['US', 'CA', 'GB', 'FR', 'DE', 'JP', 'AU', 'NL', 'SE', 'NO']  # Aliados tradicionales
    }
    
    def __init__(self):
        """Inicializa el analizador de riesgos."""
        logger.info("SatelliteRiskAnalyzer inicializado")
        logger.info("NOTA: Este es un sistema de evaluación heurística, no análisis de TTPs documentadas")
    
    def analyze_satellite(self, satellite_data: Dict) -> Dict:
        """
        Realiza evaluación automatizada de riesgos usando heurísticas.
        
        Args:
            satellite_data: Datos del satélite obtenidos de múltiples fuentes
            
        Returns:
            Diccionario con evaluación de riesgos heurística
            
        IMPORTANTE: Este análisis es automatizado y debe ser validado
        por analistas especializados para casos críticos.
        """
        basic_info = satellite_data.get('basic_info', {})
        mission_info = satellite_data.get('mission_info', {})
        
        analysis = {
            'analysis_type': 'automated_heuristic_assessment',
            'framework_inspiration': 'SPARTA concepts adapted for space domain',
            'disclaimer': 'Initial screening - requires human validation for critical assessments',
            'timestamp': datetime.utcnow().isoformat(),
            'satellite_id': basic_info.get('norad_id'),
            'satellite_name': basic_info.get('name', ''),
            'country': self._determine_country(basic_info),
            'category': self._determine_category(basic_info, mission_info),
            'risk_level': 'unknown',
            'risk_factors': [],
            'potential_concerns': [],
            'general_recommendations': [],
            'confidence_score': self._calculate_confidence(satellite_data),
            'data_sources': satellite_data.get('sources_used', [])
        }
        
        # Evaluación heurística de riesgo
        analysis['risk_level'] = self._assess_risk_heuristic(analysis['country'])
        analysis['risk_factors'] = self._identify_risk_factors(
            analysis['category'], analysis['country'], basic_info
        )
        
        # Generar preocupaciones potenciales (no confirmadas)
        analysis['potential_concerns'] = self._generate_potential_concerns(
            analysis['category'], analysis['risk_level'], basic_info
        )
        
        # Generar recomendaciones generales
        analysis['general_recommendations'] = self._generate_general_recommendations(
            analysis['category'], analysis['risk_level']
        )
        
        return analysis
    
    def _determine_country(self, basic_info: Dict) -> str:
        """Determina país de origen basado en datos disponibles."""
        return (basic_info.get('countries') or 
                basic_info.get('inferred_country') or 
                'UNKNOWN')
    
    def _determine_category(self, basic_info: Dict, mission_info: Dict) -> str:
        """Determina categoría del satélite basado en información disponible."""
        # Prioridad a datos reales de fuentes oficiales
        sat_type = mission_info.get('type', '').upper()
        if 'COMMUNICATION' in sat_type:
            return 'communication'
        elif 'EARTH' in sat_type or 'OBSERVATION' in sat_type:
            return 'earth_observation'
        elif 'NAVIGATION' in sat_type:
            return 'navigation'
        elif 'WEATHER' in sat_type or 'METEOROLOGY' in sat_type:
            return 'weather'
        elif 'SCIENTIFIC' in sat_type or 'RESEARCH' in sat_type:
            return 'scientific'
        elif 'MILITARY' in sat_type or 'DEFENSE' in sat_type:
            return 'military'
        elif 'STATION' in sat_type:
            return 'space_station'
        
        # Fallback a información inferida del nombre
        inferred_type = mission_info.get('inferred_type', '').lower()
        return inferred_type if inferred_type != 'unknown' else 'unknown'
    
    def _assess_risk_heuristic(self, country: str) -> str:
        """
        Evaluación heurística de riesgo basada en país de origen.
        
        NOTA: Esta es una clasificación simplificada basada en políticas
        espaciales públicas conocidas. No constituye una evaluación
        de inteligencia formal.
        """
        country_upper = country.upper()
        
        if any(c in country_upper for c in self.RISK_COUNTRIES['high']):
            return 'high'
        elif any(c in country_upper for c in self.RISK_COUNTRIES['medium']):
            return 'medium'
        elif any(c in country_upper for c in self.RISK_COUNTRIES['low']):
            return 'low'
        else:
            return 'medium'  # Default para países no clasificados
    
    def _identify_risk_factors(self, category: str, country: str, basic_info: Dict) -> List[str]:
        """Identifica factores de riesgo basados en características observables."""
        risk_factors = []
        
        # Factores por categoría
        if category == 'military':
            risk_factors.append("Satélite de propósito militar declarado")
        elif category == 'earth_observation':
            risk_factors.append("Capacidades de observación terrestre")
        elif category == 'communication':
            risk_factors.append("Capacidades de comunicaciones")
        elif category == 'navigation':
            risk_factors.append("Infraestructura de navegación crítica")
        
        # Factores por país
        if country.upper() in self.RISK_COUNTRIES['high']:
            risk_factors.append("País con políticas espaciales agresivas conocidas")
        
        # Factores por operador
        operator = basic_info.get('operator', '')
        if operator and any(word in operator.upper() for word in ['MILITARY', 'DEFENSE', 'ARMY', 'NAVY']):
            risk_factors.append("Operador militar o de defensa identificado")
        
        # Factores por estado
        status = basic_info.get('status', '')
        if 'OPERATIONAL' in status.upper() or 'ACTIVE' in status.upper():
            risk_factors.append("Satélite operacionalmente activo")
        
        return risk_factors
    
    def _generate_potential_concerns(self, category: str, risk_level: str, basic_info: Dict) -> List[str]:
        """
        Genera lista de preocupaciones potenciales basadas en capacidades inferidas.
        
        NOTA: Estas son preocupaciones teóricas basadas en capacidades típicas
        del tipo de satélite, no en inteligencia específica verificada.
        """
        concerns = []
        
        # Preocupaciones por categoría (basadas en capacidades típicas)
        category_concerns = {
            'communication': [
                "Potencial para interceptación de comunicaciones",
                "Posible uso como canal de comunicación encubierto",
                "Capacidad de relevo para comunicaciones sensibles"
            ],
            'earth_observation': [
                "Capacidades de vigilancia sobre territorio nacional",
                "Potencial recolección de inteligencia geoespacial",
                "Monitoreo de infraestructura crítica desde el espacio"
            ],
            'navigation': [
                "Riesgo de interferencia con sistemas de navegación críticos",
                "Potencial para spoofing de señales GNSS",
                "Dependencia de infraestructura de navegación extranjera"
            ],
            'military': [
                "Capacidades militares espaciales no transparentes",
                "Potencial para operaciones de guerra espacial",
                "Tecnologías de doble uso no declaradas"
            ],
            'weather': [
                "Recolección de datos meteorológicos con posibles aplicaciones militares"
            ],
            'space_station': [
                "Plataforma para actividades espaciales múltiples",
                "Capacidad de servicing de otros satélites"
            ]
        }
        
        concerns.extend(category_concerns.get(category, []))
        
        # Preocupaciones adicionales por nivel de riesgo heurístico
        if risk_level == 'high':
            concerns.extend([
                "País de origen con historial de actividades espaciales agresivas",
                "Potencial uso para actividades de inteligencia no declaradas",
                "Falta de transparencia en capacidades y misión declarada"
            ])
        elif risk_level == 'medium':
            concerns.extend([
                "Capacidades espaciales en desarrollo con transparencia limitada"
            ])
        
        # Agregar disclaimer
        if concerns:
            concerns.insert(0, "NOTA: Estas son preocupaciones teóricas basadas en capacidades típicas")
        
        return concerns
    
    def _generate_general_recommendations(self, category: str, risk_level: str) -> List[str]:
        """Genera recomendaciones generales de seguridad."""
        recommendations = []
        
        # Recomendaciones por nivel de riesgo
        if risk_level == 'high':
            recommendations.extend([
                "Monitorear actividad satelital mediante fuentes abiertas",
                "Evaluar dependencias críticas de servicios relacionados",
                "Considerar implementación de sistemas redundantes"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "Mantener vigilancia rutinaria de actividades",
                "Verificar capacidades declaradas versus observadas"
            ])
        else:  # low risk
            recommendations.extend([
                "Monitoreo rutinario según protocolos estándar"
            ])
        
        # Recomendaciones por categoría
        category_recommendations = {
            'communication': [
                "Auditar patrones de tráfico de comunicaciones sensibles",
                "Implementar protocolos de comunicación seguros"
            ],
            'earth_observation': [
                "Evaluar exposición de infraestructura crítica a observación",
                "Implementar contramedidas de ocultación si es necesario"
            ],
            'navigation': [
                "Implementar sistemas de navegación alternativos/redundantes",
                "Monitorear integridad de señales GNSS"
            ],
            'military': [
                "Realizar análisis detallado de capacidades mediante OSINT",
                "Coordinar con agencias de inteligencia especializadas"
            ]
        }
        
        recommendations.extend(category_recommendations.get(category, []))
        
        # Recomendación general importante
        recommendations.append(
            "IMPORTANTE: Validar este análisis con analistas de inteligencia especializados"
        )
        
        return recommendations
    
    def _calculate_confidence(self, satellite_data: Dict) -> float:
        """
        Calcula nivel de confianza del análisis basado en calidad y cantidad de datos.
        
        Factores que afectan la confianza:
        - Número de fuentes de datos
        - Completitud de información básica
        - Disponibilidad de información de misión
        - Calidad de datos orbitales
        """
        score = 0.0
        
        # Puntos por número de fuentes (max 0.4)
        sources = satellite_data.get('sources_used', [])
        score += min(len(sources) * 0.1, 0.4)
        
        # Puntos por completitud de datos básicos (max 0.3)
        basic_info = satellite_data.get('basic_info', {})
        if basic_info.get('norad_id'):
            score += 0.1
        if basic_info.get('name'):
            score += 0.1
        if basic_info.get('countries') or basic_info.get('operator'):
            score += 0.1
        
        # Puntos por información de misión (max 0.2)
        mission_info = satellite_data.get('mission_info', {})
        if mission_info.get('type') or mission_info.get('description'):
            score += 0.2
        
        # Puntos por datos orbitales (max 0.1)
        if satellite_data.get('tle'):
            score += 0.1
        
        return min(score, 1.0)
    
    def generate_assessment_report(self, analysis: Dict) -> str:
        """
        Genera reporte de evaluación de riesgos en formato texto.
        
        NOTA: Cambiado de 'generate_report' para ser más específico
        sobre el tipo de análisis que se está realizando.
        """
        lines = [
            "=" * 60,
            "EVALUACIÓN AUTOMATIZADA DE RIESGOS SATELITALES",
            "=" * 60,
            "TIPO DE ANÁLISIS: Heurístico automatizado",
            "INSPIRADO EN: Conceptos del framework SPARTA",
            "LIMITACIÓN: Requiere validación por analistas especializados",
            "",
            f"Satélite: {analysis['satellite_name']} (ID: {analysis['satellite_id']})",
            f"País de Origen: {analysis['country']}",
            f"Categoría: {self.SATELLITE_CATEGORIES.get(analysis['category'], 'Desconocido')}",
            f"Nivel de Riesgo Heurístico: {analysis['risk_level'].upper()}",
            f"Confianza del Análisis: {analysis['confidence_score']:.1%}",
            f"Fuentes de Datos: {', '.join(analysis['data_sources'])}",
            ""
        ]
        
        # Factores de riesgo identificados
        if analysis['risk_factors']:
            lines.append("FACTORES DE RIESGO IDENTIFICADOS:")
            for factor in analysis['risk_factors']:
                lines.append(f"  • {factor}")
            lines.append("")
        
        # Preocupaciones potenciales
        if analysis['potential_concerns']:
            lines.append("PREOCUPACIONES POTENCIALES:")
            for concern in analysis['potential_concerns']:
                lines.append(f"  ⚠  {concern}")
            lines.append("")
        
        # Recomendaciones generales
        if analysis['general_recommendations']:
            lines.append("RECOMENDACIONES GENERALES:")
            for rec in analysis['general_recommendations']:
                lines.append(f"  →  {rec}")
            lines.append("")
        
        # Disclaimer final
        lines.extend([
            "DISCLAIMER IMPORTANTE:",
            "Este análisis es una evaluación heurística automatizada basada",
            "en datos públicos y no constituye una evaluación formal de",
            "inteligencia. Para decisiones críticas de seguridad nacional,",
            "consulte con analistas especializados en inteligencia espacial.",
            "=" * 60
        ])
        
        return "\n".join(lines)


# Clase de compatibilidad (para no romper código existente)
class SecurityAnalyzer(SatelliteRiskAnalyzer):
    """
    Clase de compatibilidad para mantener interfaz existente.
    
    DEPRECATED: Use SatelliteRiskAnalyzer para nuevas implementaciones.
    """
    
    def __init__(self):
        super().__init__()
        logger.warning("SecurityAnalyzer está deprecated. Use SatelliteRiskAnalyzer.")
    
    def analyze_satellite(self, satellite_data: Dict) -> Dict:
        """Método de compatibilidad."""
        analysis = super().analyze_satellite(satellite_data)
        
        # Mapear a formato anterior para compatibilidad
        return {
            'satellite_id': analysis['satellite_id'],
            'satellite_name': analysis['satellite_name'],
            'country': analysis['country'],
            'category': analysis['category'],
            'risk_level': analysis['risk_level'],
            'concerns': analysis['potential_concerns'],
            'recommendations': analysis['general_recommendations'],
            'confidence': analysis['confidence_score']
        }
    
    def generate_report(self, analysis: Dict) -> str:
        """Método de compatibilidad."""
        # Si recibimos análisis en formato nuevo, convertir
        if 'potential_concerns' in analysis:
            return self.generate_assessment_report(analysis)
        
        # Si recibimos análisis en formato anterior, usar formato anterior
        lines = [
            "=" * 60,
            "EVALUACIÓN AUTOMATIZADA DE RIESGOS SATELITALES", 
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
