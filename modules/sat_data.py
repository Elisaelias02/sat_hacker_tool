import requests
import logging
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import json
import time
import os
from dotenv import load_dotenv

# Cargar variables de entorno AQUÍ directamente
load_dotenv()

logger = logging.getLogger(__name__)

# URLs y constantes
CELESTRAK_BASE_URL = "https://celestrak.org"
SPACETRACK_BASE_URL = "https://www.space-track.org"

CELESTRAK_TLE_URLS = {
    "all": f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?GROUP=active&FORMAT=tle",
    "stations": f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle",
    "visual": f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?GROUP=visual&FORMAT=tle",
    "weather": f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle",
    "noaa": f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?GROUP=noaa&FORMAT=tle",
    "goes": f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?GROUP=goes&FORMAT=tle",
    "resource": f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?GROUP=resource&FORMAT=tle",
    "cubesat": f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?GROUP=cubesat&FORMAT=tle",
    "other": f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?GROUP=other&FORMAT=tle"
}

class SatelliteDataRetriever:
    """Clase para recuperar datos satelitales desde múltiples fuentes."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SatIntel/1.0 (Educational Purpose)'
        })
        self._spacetrack_authenticated = False
        
        # Obtener credenciales directamente aquí
        self.spacetrack_username = os.getenv("SPACETRACK_USERNAME")
        self.spacetrack_password = os.getenv("SPACETRACK_PASSWORD")
        
        # Debug
        logger.info(f"Username loaded: {bool(self.spacetrack_username)}")
        logger.info(f"Password loaded: {bool(self.spacetrack_password)}")
    
    def get_tle_from_celestrak(self, satellite_id: int = None, 
                              satellite_name: str = None) -> Optional[str]:
        """
        Recupera TLE desde Celestrak.
        
        Args:
            satellite_id: NORAD ID del satélite
            satellite_name: Nombre del satélite
            
        Returns:
            String con el TLE en formato de 3 líneas o None si no se encuentra
        """
        try:
            if satellite_id:
                url = f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?CATNR={satellite_id}&FORMAT=tle"
            elif satellite_name:
                url = f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?NAME={satellite_name}&FORMAT=tle"
            else:
                raise ValueError("Debe proporcionar satellite_id o satellite_name")
            
            logger.info(f"Recuperando TLE desde Celestrak: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            tle_data = response.text.strip()
            if len(tle_data.split('\n')) >= 3:
                return tle_data
            else:
                logger.warning(f"TLE no encontrado para {satellite_id or satellite_name}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error al recuperar TLE desde Celestrak: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return None
    
    def authenticate_spacetrack(self) -> bool:
        """
        Autentica con Space-Track.org.
        
        Returns:
            True si la autenticación es exitosa, False en caso contrario
        """
        if not self.spacetrack_username or not self.spacetrack_password:
            logger.warning("Credenciales de Space-Track no configuradas")
            logger.warning(f"Username: {bool(self.spacetrack_username)}, Password: {bool(self.spacetrack_password)}")
            return False
        
        try:
            login_url = f"{SPACETRACK_BASE_URL}/ajaxauth/login"
            login_data = {
                'identity': self.spacetrack_username,
                'password': self.spacetrack_password
            }
            
            logger.info("Autenticando con Space-Track.org...")
            logger.info(f"URL de login: {login_url}")
            
            response = self.session.post(login_url, data=login_data, timeout=10)
            
            logger.info(f"Respuesta de autenticación: {response.status_code}")
            logger.info(f"Cookies recibidas: {len(response.cookies)}")
            
            # Space-Track devuelve diferentes códigos según el resultado
            if response.status_code == 200:
                # Verificar si realmente estamos autenticados haciendo una consulta de prueba
                test_url = f"{SPACETRACK_BASE_URL}/basicspacedata/query/class/satcat/NORAD_CAT_ID/25544/format/json/limit/1"
                test_response = self.session.get(test_url, timeout=10)
                
                if test_response.status_code == 200:
                    self._spacetrack_authenticated = True
                    logger.info("Autenticación exitosa con Space-Track.org")
                    return True
                else:
                    logger.error(f"Autenticación falló - test query status: {test_response.status_code}")
                    return False
            else:
                logger.error(f"Autenticación falló - status code: {response.status_code}")
                logger.error(f"Respuesta: {response.text[:200]}")
                return False
            
        except requests.RequestException as e:
            logger.error(f"Error de conexión durante autenticación: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado durante autenticación: {e}")
            return False
    
    def get_satellite_info_spacetrack(self, satellite_id: int) -> Optional[Dict]:
        """
        Recupera información detallada del satélite desde Space-Track.
        
        Args:
            satellite_id: NORAD ID del satélite
            
        Returns:
            Diccionario con información del satélite o None
        """
        if not self._spacetrack_authenticated:
            if not self.authenticate_spacetrack():
                return None
        
        try:
            # Consulta básica de información del catálogo
            query_url = (f"{SPACETRACK_BASE_URL}/basicspacedata/query/class/satcat/"
                        f"NORAD_CAT_ID/{satellite_id}/format/json")
            
            logger.info(f"Consultando información desde Space-Track para ID: {satellite_id}")
            response = self.session.get(query_url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                return data[0]  # Retorna el primer resultado
            else:
                logger.warning(f"No se encontró información para satélite ID: {satellite_id}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error al consultar Space-Track: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar respuesta JSON: {e}")
            return None
    
    def search_satellite_by_name(self, satellite_name: str) -> List[Dict]:
        """
        Busca satélites por nombre en Space-Track.
        
        Args:
            satellite_name: Nombre del satélite a buscar
            
        Returns:
            Lista de diccionarios con información de satélites encontrados
        """
        if not self._spacetrack_authenticated:
            if not self.authenticate_spacetrack():
                return []
        
        try:
            # Búsqueda por nombre en el catálogo
            query_url = (f"{SPACETRACK_BASE_URL}/basicspacedata/query/class/satcat/"
                        f"OBJECT_NAME/{satellite_name}~~*/format/json")
            
            logger.info(f"Buscando satélites con nombre: {satellite_name}")
            response = self.session.get(query_url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return data if data else []
            
        except requests.RequestException as e:
            logger.error(f"Error en búsqueda por nombre: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar respuesta JSON: {e}")
            return []
    
    def get_satellite_launches_info(self, satellite_id: int) -> Optional[Dict]:
        """
        Obtiene información de lanzamiento desde fuentes públicas.
        
        Args:
            satellite_id: NORAD ID del satélite
            
        Returns:
            Diccionario con información de lanzamiento o None
        """
        try:
            # Buscar en N2YO para información adicional (fuente pública)
            n2yo_url = f"https://www.n2yo.com/satellite/?s={satellite_id}"
            
            logger.info(f"Buscando información adicional para ID: {satellite_id}")
            response = self.session.get(n2yo_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información básica (esto puede variar según el HTML actual)
            info = {}
            
            # Buscar tabla de información del satélite
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        info[key] = value
            
            return info if info else None
            
        except requests.RequestException as e:
            logger.error(f"Error al obtener información adicional: {e}")
            return None
        except Exception as e:
            logger.error(f"Error al procesar información adicional: {e}")
            return None
    
    def get_comprehensive_satellite_data(self, satellite_id: int = None, 
                                       satellite_name: str = None) -> Dict:
        """
        Recupera datos completos del satélite desde múltiples fuentes.
        
        Args:
            satellite_id: NORAD ID del satélite
            satellite_name: Nombre del satélite
            
        Returns:
            Diccionario con toda la información disponible
        """
        result = {
            'tle': None,
            'spacetrack_info': None,
            'additional_info': None,
            'search_results': [],
            'errors': [],
            'celestrak_data': None
        }
        
        # Recuperar TLE desde Celestrak (esto siempre funciona)
        logger.info("Recuperando datos desde Celestrak...")
        if satellite_id:
            result['tle'] = self.get_tle_from_celestrak(satellite_id=satellite_id)
        elif satellite_name:
            result['tle'] = self.get_tle_from_celestrak(satellite_name=satellite_name)
        
        # Si tenemos TLE, extraer información básica
        if result['tle']:
            try:
                lines = result['tle'].strip().split('\n')
                if len(lines) >= 3:
                    sat_name = lines[0].strip()
                    line1 = lines[1].strip()
                    line2 = lines[2].strip()
                    
                    # Extraer información del TLE
                    result['celestrak_data'] = {
                        'satellite_name': sat_name,
                        'norad_id': satellite_id or self._extract_norad_from_tle(line1),
                        'classification': line1[7:8],
                        'international_designator': line1[9:17].strip(),
                        'epoch_year': int(line1[18:20]),
                        'epoch_day': float(line1[20:32]),
                        'inclination': float(line2[8:16]),
                        'raan': float(line2[17:25]),
                        'eccentricity': float('0.' + line2[26:33]),
                        'arg_perigee': float(line2[34:42]),
                        'mean_anomaly': float(line2[43:51]),
                        'mean_motion': float(line2[52:63]),
                        'revolution_number': int(line2[63:68])
                    }
                    
                    # Inferir información adicional del nombre
                    result['celestrak_data'].update(self._infer_satellite_info(sat_name))
                    
            except Exception as e:
                logger.error(f"Error procesando TLE: {e}")
        
        # Intentar Space-Track solo si las credenciales están disponibles
        if self.spacetrack_username and self.spacetrack_password:
            logger.info("Intentando recuperar datos desde Space-Track...")
            try:
                # Si solo tenemos nombre, buscar primero el ID
                if satellite_name and not satellite_id:
                    search_results = self.search_satellite_by_name(satellite_name)
                    result['search_results'] = search_results
                    
                    if search_results:
                        satellite_id = int(search_results[0].get('NORAD_CAT_ID', 0))
                        logger.info(f"Encontrado ID {satellite_id} para nombre '{satellite_name}'")
                
                # Recuperar información desde Space-Track
                if satellite_id:
                    result['spacetrack_info'] = self.get_satellite_info_spacetrack(satellite_id)
                    
            except Exception as e:
                logger.warning(f"Error al acceder Space-Track (continuando con Celestrak): {e}")
                result['errors'].append(f"Space-Track error: {e}")
        else:
            logger.info("Credenciales de Space-Track no disponibles, usando solo Celestrak")
        
        # Información adicional de fuentes públicas
        if satellite_id:
            try:
                result['additional_info'] = self.get_satellite_launches_info(satellite_id)
            except Exception as e:
                logger.warning(f"Error obteniendo información adicional: {e}")
        
        return result
    
    def _extract_norad_from_tle(self, tle_line1: str) -> int:
        """Extrae el NORAD ID de la primera línea del TLE."""
        try:
            return int(tle_line1[2:7])
        except:
            return 0
    
    def _infer_satellite_info(self, satellite_name: str) -> Dict:
        """Infiere información del satélite basado en su nombre."""
        name_upper = satellite_name.upper()
        info = {
            'inferred_country': 'UNKNOWN',
            'inferred_type': 'UNKNOWN',
            'inferred_purpose': 'UNKNOWN'
        }
        
        # Inferir país basado en patrones de nombres
        if any(pattern in name_upper for pattern in ['ISS', 'DRAGON', 'CYGNUS']):
            info['inferred_country'] = 'INTERNATIONAL'
        elif any(pattern in name_upper for pattern in ['STARLINK', 'GPS', 'NOAA', 'GOES']):
            info['inferred_country'] = 'US'
        elif any(pattern in name_upper for pattern in ['COSMOS', 'GLONASS']):
            info['inferred_country'] = 'RU'
        elif 'BEIDOU' in name_upper:
            info['inferred_country'] = 'CN'
        elif 'GALILEO' in name_upper:
            info['inferred_country'] = 'EU'
        
        # Inferir tipo/propósito
        if any(pattern in name_upper for pattern in ['STARLINK', 'ONEWEB', 'IRIDIUM']):
            info['inferred_type'] = 'COMMUNICATION'
            info['inferred_purpose'] = 'Internet/Communications constellation'
        elif any(pattern in name_upper for pattern in ['GPS', 'GLONASS', 'GALILEO', 'BEIDOU']):
            info['inferred_type'] = 'NAVIGATION'
            info['inferred_purpose'] = 'Global Navigation Satellite System'
        elif any(pattern in name_upper for pattern in ['NOAA', 'GOES', 'METOP']):
            info['inferred_type'] = 'WEATHER'
            info['inferred_purpose'] = 'Weather monitoring and forecasting'
        elif any(pattern in name_upper for pattern in ['LANDSAT', 'SENTINEL', 'WORLDVIEW']):
            info['inferred_type'] = 'EARTH_OBSERVATION'
            info['inferred_purpose'] = 'Earth observation and remote sensing'
        elif 'ISS' in name_upper:
            info['inferred_type'] = 'SPACE_STATION'
            info['inferred_purpose'] = 'International Space Station'
        elif 'COSMOS' in name_upper:
            info['inferred_type'] = 'MILITARY'
            info['inferred_purpose'] = 'Military/Intelligence satellite'
        
        return info


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
    
    def get_tle_from_celestrak(self, satellite_id: int = None, 
                              satellite_name: str = None) -> Optional[str]:
        """
        Recupera TLE desde Celestrak.
        
        Args:
            satellite_id: NORAD ID del satélite
            satellite_name: Nombre del satélite
            
        Returns:
            String con el TLE en formato de 3 líneas o None si no se encuentra
        """
        try:
            if satellite_id:
                url = f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?CATNR={satellite_id}&FORMAT=tle"
            elif satellite_name:
                url = f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?NAME={satellite_name}&FORMAT=tle"
            else:
                raise ValueError("Debe proporcionar satellite_id o satellite_name")
            
            logger.info(f"Recuperando TLE desde Celestrak: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            tle_data = response.text.strip()
            if len(tle_data.split('\n')) >= 3:
                return tle_data
            else:
                logger.warning(f"TLE no encontrado para {satellite_id or satellite_name}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error al recuperar TLE desde Celestrak: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return None
    
    def authenticate_spacetrack(self) -> bool:
        """
        Autentica con Space-Track.org.
        
        Returns:
            True si la autenticación es exitosa, False en caso contrario
        """
        if not SPACETRACK_USERNAME or not SPACETRACK_PASSWORD:
            logger.warning("Credenciales de Space-Track no configuradas")
            return False
        
        try:
            login_url = f"{SPACETRACK_BASE_URL}/ajaxauth/login"
            login_data = {
                'identity': SPACETRACK_USERNAME,
                'password': SPACETRACK_PASSWORD
            }
            
            logger.info("Autenticando con Space-Track.org...")
            response = self.session.post(login_url, data=login_data, timeout=10)
            response.raise_for_status()
            
            self._spacetrack_authenticated = True
            logger.info("Autenticación exitosa con Space-Track.org")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Error de autenticación con Space-Track: {e}")
            return False
    
    def get_satellite_info_spacetrack(self, satellite_id: int) -> Optional[Dict]:
        """
        Recupera información detallada del satélite desde Space-Track.
        
        Args:
            satellite_id: NORAD ID del satélite
            
        Returns:
            Diccionario con información del satélite o None
        """
        if not self._spacetrack_authenticated:
            if not self.authenticate_spacetrack():
                return None
        
        try:
            # Consulta básica de información del catálogo
            query_url = (f"{SPACETRACK_BASE_URL}/basicspacedata/query/class/satcat/"
                        f"NORAD_CAT_ID/{satellite_id}/format/json")
            
            logger.info(f"Consultando información desde Space-Track para ID: {satellite_id}")
            response = self.session.get(query_url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                return data[0]  # Retorna el primer resultado
            else:
                logger.warning(f"No se encontró información para satélite ID: {satellite_id}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error al consultar Space-Track: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar respuesta JSON: {e}")
            return None
    
    def search_satellite_by_name(self, satellite_name: str) -> List[Dict]:
        """
        Busca satélites por nombre en Space-Track.
        
        Args:
            satellite_name: Nombre del satélite a buscar
            
        Returns:
            Lista de diccionarios con información de satélites encontrados
        """
        if not self._spacetrack_authenticated:
            if not self.authenticate_spacetrack():
                return []
        
        try:
            # Búsqueda por nombre en el catálogo
            query_url = (f"{SPACETRACK_BASE_URL}/basicspacedata/query/class/satcat/"
                        f"OBJECT_NAME/{satellite_name}~~*/format/json")
            
            logger.info(f"Buscando satélites con nombre: {satellite_name}")
            response = self.session.get(query_url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return data if data else []
            
        except requests.RequestException as e:
            logger.error(f"Error en búsqueda por nombre: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar respuesta JSON: {e}")
            return []
    
    def get_satellite_launches_info(self, satellite_id: int) -> Optional[Dict]:
        """
        Obtiene información de lanzamiento desde fuentes públicas.
        
        Args:
            satellite_id: NORAD ID del satélite
            
        Returns:
            Diccionario con información de lanzamiento o None
        """
        try:
            # Buscar en N2YO para información adicional (fuente pública)
            n2yo_url = f"https://www.n2yo.com/satellite/?s={satellite_id}"
            
            logger.info(f"Buscando información adicional para ID: {satellite_id}")
            response = self.session.get(n2yo_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información básica (esto puede variar según el HTML actual)
            info = {}
            
            # Buscar tabla de información del satélite
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        info[key] = value
            
            return info if info else None
            
        except requests.RequestException as e:
            logger.error(f"Error al obtener información adicional: {e}")
            return None
        except Exception as e:
            logger.error(f"Error al procesar información adicional: {e}")
            return None
    
    def get_comprehensive_satellite_data(self, satellite_id: int = None, 
                                       satellite_name: str = None) -> Dict:
        """
        Recupera datos completos del satélite desde múltiples fuentes.
        
        Args:
            satellite_id: NORAD ID del satélite
            satellite_name: Nombre del satélite
            
        Returns:
            Diccionario con toda la información disponible
        """
        result = {
            'tle': None,
            'spacetrack_info': None,
            'additional_info': None,
            'search_results': [],
            'errors': []
        }
        
        # Si solo tenemos nombre, buscar primero el ID
        if satellite_name and not satellite_id:
            search_results = self.search_satellite_by_name(satellite_name)
            result['search_results'] = search_results
            
            if search_results:
                satellite_id = int(search_results[0].get('NORAD_CAT_ID', 0))
                logger.info(f"Encontrado ID {satellite_id} para nombre '{satellite_name}'")
        
        # Recuperar TLE desde Celestrak
        if satellite_id:
            result['tle'] = self.get_tle_from_celestrak(satellite_id=satellite_id)
        elif satellite_name:
            result['tle'] = self.get_tle_from_celestrak(satellite_name=satellite_name)
        
        # Recuperar información desde Space-Track
        if satellite_id:
            result['spacetrack_info'] = self.get_satellite_info_spacetrack(satellite_id)
            result['additional_info'] = self.get_satellite_launches_info(satellite_id)
        
        return result


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
