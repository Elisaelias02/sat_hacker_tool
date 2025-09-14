import pytest
from modules.security import SPARTAAnalyzer

class TestSPARTAAnalyzer:
    """Tests para SPARTAAnalyzer."""
    
    def setup_method(self):
        """Configuración para cada test."""
        self.analyzer = SPARTAAnalyzer()
    
    def test_analyze_satellite_communication(self):
        """Test análisis de satélite de comunicaciones."""
        satellite_data = {
            'spacetrack_info': {
                'NORAD_CAT_ID': '12345',
                'OBJECT_NAME': 'STARLINK-1234',
                'COUNTRY': 'US'
            }
        }
        
        analysis = self.analyzer.analyze_satellite(satellite_data)
        
        assert analysis['satellite_category'] == 'communication'
        assert analysis['risk_level'] == 'low'
        assert 'command_and_control' in analysis['sparta_tactics']
    
    def test_analyze_satellite_high_risk_country(self):
        """Test análisis de satélite de país de alto riesgo."""
        satellite_data = {
            'spacetrack_info': {
                'NORAD_CAT_ID': '54321',
                'OBJECT_NAME': 'MILITARY SAT',
                'COUNTRY': 'RU'
            }
        }
        
        analysis = self.analyzer.analyze_satellite(satellite_data)
        
        assert analysis['risk_level'] == 'high'
        assert len(analysis['security_concerns']) > 0
        assert len(analysis['recommendations']) > 0
    
    def test_determine_satellite_category(self):
        """Test determinación de categoría de satélite."""
        # Test satélite de comunicaciones
        spacetrack_info = {'OBJECT_NAME': 'STARLINK-1234', 'OBJECT_TYPE': 'PAYLOAD'}
        category = self.analyzer._determine_satellite_category(spacetrack_info)
        assert category == 'communication'
        
        # Test satélite de observación terrestre
        spacetrack_info = {'OBJECT_NAME': 'LANDSAT-8', 'OBJECT_TYPE': 'PAYLOAD'}
        category = self.analyzer._determine_satellite_category(spacetrack_info)
        assert category == 'earth_observation'
    
    def test_assess_country_risk(self):
        """Test evaluación de riesgo por país."""
        assert self.analyzer._assess_country_risk('RU') == 'high'
        assert self.analyzer._assess_country_risk('US') == 'low'
        assert self.analyzer._assess_country_risk('XX') == 'medium'
    
    def test_generate_sparta_report(self):
        """Test generación de reporte SPARTA."""
        analysis = {
            'satellite_id': '25544',
            'satellite_name': 'ISS',
            'country_of_origin': 'US',
            'satellite_category': 'space_station',
            'risk_level': 'low',
            'sparta_tactics': ['persistence', 'collection'],
            'security_concerns': ['Test concern'],
            'recommendations': ['Test recommendation'],
            'confidence_score': 0.9
        }
        
        report = self.analyzer.generate_sparta_report(analysis)
        
        assert 'ANÁLISIS DE SEGURIDAD SPARTA' in report
        assert 'ISS' in report
        assert 'Test concern' in report
        assert 'Test recommendation' in report
