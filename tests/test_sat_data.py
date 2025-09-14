import pytest
from unittest.mock import Mock, patch
from modules.sat_data import SatelliteDataRetriever, parse_tle

class TestSatelliteDataRetriever:
    """Tests para SatelliteDataRetriever."""
    
    def setup_method(self):
        """Configuración para cada test."""
        self.retriever = SatelliteDataRetriever()
    
    def test_parse_tle_valid(self):
        """Test parsing de TLE válido."""
        tle_string = """ISS (ZARYA)
1 25544U 98067A   24001.50000000  .00002182  00000-0  40864-4 0  9990
2 25544  51.6400 339.7900 0003835 356.8500 120.6800 15.48919103123456"""
        
        name, line1, line2 = parse_tle(tle_string)
        
        assert name == "ISS (ZARYA)"
        assert line1.startswith("1 25544U")
        assert line2.startswith("2 25544")
    
    def test_parse_tle_invalid(self):
        """Test parsing de TLE inválido."""
        with pytest.raises(ValueError):
            parse_tle("Invalid TLE")
    
    @patch('requests.Session.get')
    def test_get_tle_from_celestrak_success(self, mock_get):
        """Test recuperación exitosa de TLE desde Celestrak."""
        mock_response = Mock()
        mock_response.text = """ISS (ZARYA)
1 25544U 98067A   24001.50000000  .00002182  00000-0  40864-4 0  9990
2 25544  51.6400 339.7900 0003835 356.8500 120.6800 15.48919103123456"""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.retriever.get_tle_from_celestrak(satellite_id=25544)
        
        assert result is not None
        assert "ISS (ZARYA)" in result
        assert "1 25544U" in result
    
    @patch('requests.Session.get')
    def test_get_tle_from_celestrak_not_found(self, mock_get):
        """Test cuando no se encuentra TLE en Celestrak."""
        mock_response = Mock()
        mock_response.text = ""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.retriever.get_tle_from_celestrak(satellite_id=99999)
        
        assert result is None
