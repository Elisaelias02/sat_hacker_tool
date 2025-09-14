import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SPARTAAnalyzer:
    """Analizador de inteligencia de seguridad basado en framework SPARTA."""
    
    # Taxonomía SPARTA simplificada para satélites
    SPARTA_TACTICS = {
        'reconnaissance': 'Reconocimiento',
        'resource_development': 'Desarrollo de Recursos',
        'initial_access': 'Acceso Inicial',
        'execution': 'Ejecución',
        'persistence': 'Persistencia',
        'privilege_escalation': 'Escalación de Privilegios',
        'defense_evasion': 'Evasión de Defensas',
        'credential_access': 'Acceso a Credenciales',
        'discovery': 'Descubrimiento',
        'lateral_movement': 'Movimiento Lateral',
        'collection': 'Recolección',
        'command_and_control': 'Comando y Control',
        'exfiltration': 'Exfiltración',
        'impact': 'Impacto'
    }
    
    SATELLITE_CATEGORIES = {
        'communication': 'Comunicaciones',
        'earth_observation': 'Observación Terrestre',
        'navigation': 'Navegación',
        'weather': 'Meteorológico',
        'scientific': 'Científico',
        'military': 'Militar',
        'dual_use': 'Doble Uso',
        'space_station': 'Estación Espacial',
        'technology_demo': 'Demostración Tecnológica',
        'debris': 'Basura Espacial',
        'unknown': 'Desconocido'
    }
    
    COUNTRY_RISK_LEVELS = {
        'high_risk': ['RU', 'CN', 'KP', 'IR'],  # Rusia, China, Corea del Norte, Irán
        'medium_risk': ['PK', 'IN', 'IL'],      # Pakistán, India, Israel
        'low_risk': ['US', 'CA', 'GB', 'FR', 'DE', 'JP', 'AU', 'NL', 'SE', 'NO']  # Aliados
    }
    
    def __init__(self):
        """Inicializa el analizador SPARTA."""
        self.risk_assessments = []
        logger.info("Analizador SPARTA inicializado")
    
    def analyze_satellite(self, satellite_data: Dict) -> Dict:
        """
        Analiza un satélite y genera evaluación de riesgos SPARTA.
        
        Args:
            satellite_data: Datos completos del satélite
            
        Returns:
            Diccionario con análisis de seguridad
        """
        analysis = {
            'satellite_id': None,
            'satellite_name': None,
            'country_of_origin': None,
            'satellite_category': 'unknown',
            'risk_level': 'low',
            'sparta_tactics': [],
            'security_concerns': [],
            'recommendations': [],
            'confidence_score': 0.0
        }
        
        try:
            # Extraer información básica
            spacetrack_info = satellite_data.get('spacetrack_info', {})
            if spacetrack_info:
                analysis['satellite_id'] = spacetrack_info.get('NORAD_CAT_ID')
                analysis['satellite_name'] = spacetrack_info.get('OBJECT_NAME', '').strip()
                analysis['country_of_origin'] = spacetrack_info.get('COUNTRY', '').strip()
                
                # Determinar categoría del satélite
                analysis['satellite_category'] = self._determine_satellite_category(spacetrack_info)
                
                # Evaluar riesgo basado en país de origen
                analysis['risk_level'] = self._assess_country_risk(analysis['country_of_origin'])
                
                # Mapear tácticas SPARTA
                analysis['sparta_tactics'] = self._map_sparta_tactics(
                    analysis['satellite_category'], 
                    analysis['country_of_origin']
                )
                
                # Generar preocupaciones de seguridad
                analysis['security_concerns'] = self._generate_security_concerns(
                    analysis['satellite_category'],
                    analysis['risk_level'],
                    spacetrack_info
                )
                
                # Generar recomendaciones
                analysis['recommendations'] = self._generate_recommendations(analysis)
                
                # Calcular puntuación de confianza
                analysis['confidence_score'] = self._calculate_confidence_score(satellite_data)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis SPARTA: {e}")
            analysis['security_concerns'].append(f"Error en análisis: {e}")
            return analysis
    
    def _determine_satellite_category(self, spacetrack_info: Dict) -> str:
        """Determina la categoría del satélite basado en su información."""
        object_name = spacetrack_info.get('OBJECT_NAME', '').upper()
        object_type = spacetrack_info.get('OBJECT_TYPE', '').upper()
        
        # Patrones para identificar categorías
        if any(keyword in object_name for keyword in ['STARLINK', 'ONEWEB', 'IRIDIUM', 'GLOBALSTAR']):
            return 'communication'
        elif any(keyword in object_name for keyword in ['LANDSAT', 'SENTINEL', 'WORLDVIEW', 'PLEIADES']):
            return 'earth_observation'
        elif any(keyword in object_name for keyword in ['GPS', 'GLONASS', 'GALILEO', 'BEIDOU']):
            return 'navigation'
        elif any(keyword in object_name for keyword in ['NOAA', 'GOES', 'METOP', 'WEATHER']):
            return 'weather'
        elif any(keyword in object_name for keyword in ['ISS', 'TIANGONG', 'STATION']):
            return 'space_station'
        elif any(keyword in object_name for keyword in ['MILITARY', 'DEFENSE', 'CLASSIFIED']):
            return 'military'
        elif any(keyword in object_name for keyword in ['SCIENCE', 'RESEARCH', 'EXPERIMENT']):
            return 'scientific'
        elif 'DEBRIS' in object_type or 'DEB' in object_name:
            return 'debris'
        else:
            return 'unknown'
    
    def _assess_country_risk(self, country_code: str) -> str:
        """Evalúa el nivel de riesgo basado en el país de origen."""
        if not country_code:
            return 'unknown'
        
        if country_code in self.COUNTRY_RISK_LEVELS['high_risk']:
            return 'high'
        elif country_code in self.COUNTRY_RISK_LEVELS['medium_risk']:
            return 'medium'
        elif country_code in self.COUNTRY_RISK_LEVELS['low_risk']:
            return 'low'
        else:
            return 'medium'  # Por defecto para países no clasificados
    
    def _map_sparta_tactics(self, category: str, country: str) -> List[str]:
        """Mapea tácticas SPARTA basadas en categoría y país."""
        tactics = []
        
        # Tácticas basadas en categoría del satélite
        category_tactics = {
            'communication': ['command_and_control', 'collection', 'exfiltration'],
            'earth_observation': ['reconnaissance', 'collection', 'discovery'],
            'navigation': ['discovery', 'lateral_movement', 'impact'],
            'weather': ['reconnaissance', 'collection'],
            'military': ['reconnaissance', 'command_and_control', 'impact', 'defense_evasion'],
            'dual_use': ['reconnaissance', 'command_and_control', 'collection', 'impact'],
            'space_station': ['persistence', 'command_and_control', 'collection'],
            'scientific': ['collection', 'discovery'],
            'technology_demo': ['resource_development', 'discovery'],
            'debris': ['impact', 'defense_evasion'],
            'unknown': ['discovery']
        }
        
        tactics.extend(category_tactics.get(category, []))
        
        # Tácticas adicionales para países de alto riesgo
        if country in self.COUNTRY_RISK_LEVELS['high_risk']:
            tactics.extend(['credential_access', 'privilege_escalation', 'lateral_movement'])
        
        return list(set(tactics))  # Eliminar duplicados
    
    def _generate_security_concerns(self, category: str, risk_level: str, 
                                  spacetrack_info: Dict) -> List[str]:
        """Genera lista de preocupaciones de seguridad."""
        concerns = []
        
        # Preocupaciones basadas en categoría
        category_concerns = {
            'communication': [
                "Interceptación potencial de comunicaciones",
                "Capacidad de relevo para comunicaciones militares",
                "Posible canal encubierto para exfiltración de datos"
            ],
            'earth_observation': [
                "Capacidades de vigilancia sobre territorio nacional",
                "Recolección de inteligencia geoespacial",
                "Monitoreo de infraestructura crítica"
            ],
            'navigation': [
                "Interferencia con sistemas de navegación críticos",
                "Spoofing de señales GNSS",
                "Dependencia de infraestructura extranjera"
            ],
            'military': [
                "Capacidades militares no declaradas",
                "Potencial para guerra espacial",
                "Tecnologías de doble uso"
            ],
            'dual_use': [
                "Aplicaciones militares de tecnología civil",
                "Transferencia de tecnología sensible",
                "Uso dual no transparente"
            ]
        }
        
        concerns.extend(category_concerns.get(category, []))
        
        # Preocupaciones adicionales por nivel de riesgo
        if risk_level == 'high':
            concerns.extend([
                "País de origen clasificado como alto riesgo",
                "Posible uso para actividades de inteligencia",
                "Falta de transparencia en misión declarada"
            ])
        
        # Preocupaciones basadas en datos específicos
        launch_year = spacetrack_info.get('LAUNCH_YEAR')
        if launch_year and int(launch_year) < 2000:
            concerns.append("Satélite antiguo con posibles vulnerabilidades de seguridad")
        
        return concerns
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Genera recomendaciones de seguridad."""
        recommendations = []
        
        risk_level = analysis['risk_level']
        category = analysis['satellite_category']
        
        # Recomendaciones generales por nivel de riesgo
        if risk_level == 'high':
            recommendations.extend([
                "Monitorear actividad satelital de cerca",
                "Implementar contramedidas de interferencia si es necesario",
                "Evaluar dependencias críticas de servicios relacionados"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "Mantener vigilancia rutinaria",
                "Verificar capacidades declaradas vs. observadas"
            ])
        
        # Recomendaciones específicas por categoría
        if category == 'communication':
            recommendations.append("Auditar tráfico de comunicaciones sensibles")
        elif category == 'earth_observation':
            recommendations.append("Evaluar exposición de infraestructura crítica")
        elif category == 'navigation':
            recommendations.append("Implementar sistemas de navegación redundantes")
        
        # Recomendaciones para tácticas SPARTA específicas
        sparta_tactics = analysis['sparta_tactics']
        if 'command_and_control' in sparta_tactics:
            recommendations.append("Monitorear patrones de comunicación anómalos")
        if 'reconnaissance' in sparta_tactics:
            recommendations.append("Implementar contramedidas de ocultación")
        
        return recommendations
    
    def _calculate_confidence_score(self, satellite_data: Dict) -> float:
        """Calcula puntuación de confianza del análisis."""
        score = 0.0
        max_score = 5.0
        
        # Disponibilidad de datos básicos
        if satellite_data.get('tle'):
            score += 1.0
        if satellite_data.get('spacetrack_info'):
            score += 2.0
        if satellite_data.get('additional_info'):
            score += 1.0
        
        # Completitud de información crítica
        spacetrack_info = satellite_data.get('spacetrack_info', {})
        if spacetrack_info.get('COUNTRY'):
            score += 0.5
        if spacetrack_info.get('OBJECT_NAME'):
            score += 0.5
        
        return min(score / max_score, 1.0)
    
    def generate_sparta_report(self, analysis: Dict) -> str:
        """Genera reporte SPARTA en formato de texto."""
        report_lines = []
        
        report_lines.append("=" * 60)
        report_lines.append("ANÁLISIS DE SEGURIDAD SPARTA")
        report_lines.append("=" * 60)
        
        # Información básica
        report_lines.append(f"Satélite: {analysis['satellite_name']} (ID: {analysis['satellite_id']})")
        report_lines.append(f"País de Origen: {analysis['country_of_origin']}")
        report_lines.append(f"Categoría: {self.SATELLITE_CATEGORIES.get(analysis['satellite_category'], 'Desconocido')}")
        report_lines.append(f"Nivel de Riesgo: {analysis['risk_level'].upper()}")
        report_lines.append(f"Confianza del Análisis: {analysis['confidence_score']:.1%}")
        report_lines.append("")
        
        # Tácticas SPARTA
        if analysis['sparta_tactics']:
            report_lines.append("TÁCTICAS SPARTA IDENTIFICADAS:")
            for tactic in analysis['sparta_tactics']:
                tactic_name = self.SPARTA_TACTICS.get(tactic, tactic)
                report_lines.append(f"  • {tactic_name}")
            report_lines.append("")
        
        # Preocupaciones de seguridad
        if analysis['security_concerns']:
            report_lines.append("PREOCUPACIONES DE SEGURIDAD:")
            for concern in analysis['security_concerns']:
                report_lines.append(f"  ⚠  {concern}")
            report_lines.append("")
        
        # Recomendaciones
        if analysis['recommendations']:
            report_lines.append("RECOMENDACIONES:")
            for recommendation in analysis['recommendations']:
                report_lines.append(f"  →  {recommendation}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
