import pytest
from datetime import datetime
from modules.orbital import OrbitalCalculator

class TestOrbitalCalculator:
    """Tests para OrbitalCalculator."""
    
    def setup_method(self):
        """Configuración para cada test."""
        # TLE de ejemplo para ISS
        self.tle_line1 = "1 25544U 98067A   24001.50000000  .00002182  00000-0  40864-4 0  9990"
        self.tle_line2 = "2 25544  51.6400 339.7900 0003835 356.8500 120.6800 15.48919103123456"
        self.calculator = OrbitalCalculator(self.tle_line1, self.tle_line2)
    
    def test_initialization_success(self):
        """Test inicialización exitosa."""
        assert self.calculator.satellite is not None
        assert self.calculator.satellite.error == 0
    
    def test_initialization_invalid_tle(self):
        """Test inicialización con TLE inválido."""
        with pytest.raises(ValueError):
            OrbitalCalculator("invalid", "tle")
    
    def test_get_position_at_time(self):
        """Test cálculo de posición."""
        test_time = datetime(2024, 1, 1, 12, 0, 0)
        position = self.calculator.get_position_at_time(test_time)
        
        assert position is not None
        assert 'latitude' in position
        assert 'longitude' in position
        assert 'altitude_km' in position
        assert -90 <= position['latitude'] <= 90
        assert -180 <= position['longitude'] <= 180
        assert position['altitude_km'] > 0
    
    def test_get_orbital_elements(self):
        """Test extracción de elementos orbitales."""
        elements = self.calculator.get_orbital_elements()
        
        assert 'inclination_deg' in elements
        assert 'eccentricity' in elements
        assert 'mean_motion_rev_per_day' in elements
        assert elements['satellite_number'] == 25544
