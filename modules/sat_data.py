import requests
import logging
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import json
import time
from config.settings import *

logger = logging.getLogger(__name__)

class SatelliteDataRetriever:
    """Clase para recuperar datos satelitales desde múltiples fuentes."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SatIntel/1.0 (Educational Purpose)'
        })
        self._spacetrack_authenticated = False
    
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
