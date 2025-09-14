import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def parse_tle(tle_string: str) -> Tuple[str, str, str]:
    """
    Parse un string TLE en sus tres líneas componentes.
    
    Args:
        tle_string: String con el TLE completo
        
    Returns:
        Tupla con (nombre, línea1, línea2)
    """
    lines = tle_string.strip().split('\n')
    if len(lines) >= 3:
        return lines[0].strip(), lines[1].strip(), lines[2].strip()
    else:
        raise ValueError("TLE debe contener al menos 3 líneas")

def extract_norad_from_tle(tle_line1: str) -> int:
    """Extrae el NORAD ID de la primera línea del TLE."""
    try:
        return int(tle_line1[2:7])
    except:
        return 0

def infer_satellite_info(satellite_name: str) -> dict:
    """Infiere información del satélite basado en su nombre."""
    name_upper = satellite_name.upper()
    info = {
        'inferred_country': 'UNKNOWN',
        'inferred_type': 'UNKNOWN',
        'inferred_purpose': 'UNKNOWN'
    }
    
    # Patrones de países
    country_patterns = {
        'INTERNATIONAL': ['ISS', 'DRAGON', 'CYGNUS'],
        'US': ['STARLINK', 'GPS', 'NOAA', 'GOES', 'LANDSAT'],
        'RU': ['COSMOS', 'GLONASS'],
        'CN': ['BEIDOU'],
        'EU': ['GALILEO', 'SENTINEL']
    }
    
    for country, patterns in country_patterns.items():
        if any(pattern in name_upper for pattern in patterns):
            info['inferred_country'] = country
            break
    
    # Patrones de tipo/propósito
    type_patterns = {
        ('COMMUNICATION', 'Internet/Communications constellation'): ['STARLINK', 'ONEWEB', 'IRIDIUM'],
        ('NAVIGATION', 'Global Navigation Satellite System'): ['GPS', 'GLONASS', 'GALILEO', 'BEIDOU'],
        ('WEATHER', 'Weather monitoring and forecasting'): ['NOAA', 'GOES', 'METOP'],
        ('EARTH_OBSERVATION', 'Earth observation and remote sensing'): ['LANDSAT', 'SENTINEL', 'WORLDVIEW'],
        ('SPACE_STATION', 'International Space Station'): ['ISS'],
        ('MILITARY', 'Military/Intelligence satellite'): ['COSMOS']
    }
    
    for (sat_type, purpose), patterns in type_patterns.items():
        if any(pattern in name_upper for pattern in patterns):
            info['inferred_type'] = sat_type
            info['inferred_purpose'] = purpose
            break
    
    return info

def safe_float_conversion(value: str, default: float = 0.0) -> float:
    """Convierte string a float de forma segura."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int_conversion(value: str, default: int = 0) -> int:
    """Convierte string a int de forma segura."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
