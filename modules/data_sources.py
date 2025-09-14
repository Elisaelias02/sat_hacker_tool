import requests
import logging
import json
from typing import Dict, List, Optional  # ← IMPORTACIÓN FALTANTE
from bs4 import BeautifulSoup
from config.settings import *
from modules.utils import infer_satellite_info, extract_norad_from_tle

logger = logging.getLogger(__name__)

class SatelliteDataManager:
    """Gestor unificado de fuentes de datos satelitales."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SatIntel/1.0 (Educational Purpose)'
        })
        logger.info("SatelliteDataManager inicializado")
    
    def get_satellite_data(self, satellite_id: int = None, 
                          satellite_name: str = None) -> Dict:
        """
        Punto de entrada principal para obtener datos satelitales.
        
        Args:
            satellite_id: NORAD ID del satélite
            satellite_name: Nombre del satélite
            
        Returns:
            Diccionario con datos consolidados
        """
        result = {
            'basic_info': {},
            'mission_info': {},
            'technical_info': {},
            'orbital_info': {},
            'tle': None,
            'sources_used': [],
            'errors': [],
            'raw_data': {}
        }
        
        logger.info(f"Recuperando datos para: ID={satellite_id}, Nombre={satellite_name}")
        
        # 1. Obtener TLE desde Celestrak (prioritario)
        tle_data = self._get_celestrak_data(satellite_id, satellite_name)
        if tle_data:
            result['tle'] = tle_data['tle']
            result['orbital_info'] = tle_data['orbital_elements']
            result['sources_used'].append('Celestrak')
            result['raw_data']['celestrak'] = tle_data
            
            # Extraer ID si solo teníamos nombre
            if not satellite_id and tle_data.get('norad_id'):
                satellite_id = tle_data['norad_id']
        
        # 2. Obtener datos de N2YO
        n2yo_data = self._get_n2yo_data(satellite_id)
        if n2yo_data:
            result['basic_info'].update(n2yo_data['basic_info'])
            result['sources_used'].append('N2YO')
            result['raw_data']['n2yo'] = n2yo_data
        
        # 3. Obtener datos de SatNOGS
        satnogs_data = self._get_satnogs_data(satellite_id)
        if satnogs_data:
            result['basic_info'].update(satnogs_data['basic_info'])
            result['mission_info'].update(satnogs_data['mission_info'])
            result['technical_info'].update(satnogs_data['technical_info'])
            result['sources_used'].append('SatNOGS')
            result['raw_data']['satnogs'] = satnogs_data
        
        # 4. Consolidar información
        self._consolidate_data(result)
        
        logger.info(f"Datos recuperados de {len(result['sources_used'])} fuentes")
        return result
    
    def _get_celestrak_data(self, satellite_id: int = None, 
                           satellite_name: str = None) -> Optional[Dict]:
        """Recupera datos desde Celestrak."""
        try:
            if satellite_id:
                url = f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?CATNR={satellite_id}&FORMAT=tle"
            elif satellite_name:
                url = f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?NAME={satellite_name}&FORMAT=tle"
            else:
                return None
            
            logger.info(f"Consultando Celestrak: {url}")
            response = self.session.get(url, timeout=API_TIMEOUTS['celestrak'])
            response.raise_for_status()
            
            tle_text = response.text.strip()
            if len(tle_text.split('\n')) >= 3:
                lines = tle_text.split('\n')
                name = lines[0].strip()
                line1 = lines[1].strip()
                line2 = lines[2].strip()
                
                # Extraer elementos orbitales
                orbital_elements = {
                    'norad_id': extract_norad_from_tle(line1),
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
                
                # Información inferida
                inferred = infer_satellite_info(name)
                
                return {
                    'tle': tle_text,
                    'satellite_name': name,
                    'norad_id': orbital_elements['norad_id'],
                    'orbital_elements': orbital_elements,
                    'inferred_info': inferred
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error en Celestrak: {e}")
            return None
    
    def _get_n2yo_data(self, satellite_id: int) -> Optional[Dict]:
        """Recupera datos desde N2YO API."""
        if not satellite_id:
            return None
        
        try:
            url = f"{N2YO_BASE_URL}/tle/{satellite_id}&apiKey={N2YO_API_KEY}"
            
            logger.info(f"Consultando N2YO API: {satellite_id}")
            response = self.session.get(url, timeout=API_TIMEOUTS['n2yo'])
            response.raise_for_status()
            
            data = response.json()
            
            if 'info' in data:
                return {
                    'basic_info': {
                        'norad_id': data['info'].get('satid'),
                        'name': data['info'].get('satname'),
                        'launch_date': data['info'].get('launchDate'),
                        'decay_date': data['info'].get('decayDate')
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error en N2YO: {e}")
            return None
    
    def _get_satnogs_data(self, satellite_id: int) -> Optional[Dict]:
        """Recupera datos desde SatNOGS DB."""
        if not satellite_id:
            return None
        
        try:
            url = f"{SATNOGS_BASE_URL}/satellites/?norad_cat_id={satellite_id}"
            
            logger.info(f"Consultando SatNOGS: {satellite_id}")
            response = self.session.get(url, timeout=API_TIMEOUTS['satnogs'])
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                sat = data[0]
                return {
                    'basic_info': {
                        'name': sat.get('name'),
                        'operator': sat.get('operator'),
                        'countries': sat.get('countries'),
                        'launched': sat.get('launched'),
                        'status': sat.get('status'),
                        'website': sat.get('website')
                    },
                    'mission_info': {
                        'description': sat.get('description'),
                        'type': sat.get('type'),
                        'orbit': sat.get('orbit')
                    },
                    'technical_info': {
                        'size': sat.get('size'),
                        'freq_bands': [band.get('name') for band in sat.get('freq_bands', [])],
                        'modes': [mode.get('name') for mode in sat.get('modes', [])]
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error en SatNOGS: {e}")
            return None
    
    def _consolidate_data(self, result: Dict):
        """Consolida y limpia los datos obtenidos."""
        # Limpiar valores vacíos
        for section in ['basic_info', 'mission_info', 'technical_info', 'orbital_info']:
            result[section] = {k: v for k, v in result[section].items() 
                             if v and v != 'N/A' and v != ''}
        
        # Agregar información inferida si falta datos
        if 'celestrak' in result['raw_data']:
            celestrak_data = result['raw_data']['celestrak']
            inferred = celestrak_data.get('inferred_info', {})
            
            if not result['basic_info'].get('countries'):
                result['basic_info']['inferred_country'] = inferred.get('inferred_country')
            if not result['mission_info'].get('type'):
                result['mission_info']['inferred_type'] = inferred.get('inferred_type')
            if not result['mission_info'].get('purpose'):
                result['mission_info']['inferred_purpose'] = inferred.get('inferred_purpose')
            
            # Agregar nombre y NORAD ID desde Celestrak si no están
            if not result['basic_info'].get('name'):
                result['basic_info']['name'] = celestrak_data.get('satellite_name')
            if not result['basic_info'].get('norad_id'):
                result['basic_info']['norad_id'] = celestrak_data.get('norad_id')
    
    def search_satellites(self, search_term: str) -> List[Dict]:
        """Busca satélites por nombre en múltiples fuentes."""
        results = []
        
        # Buscar en SatNOGS
        try:
            url = f"{SATNOGS_BASE_URL}/satellites/?name__icontains={search_term}"
            response = self.session.get(url, timeout=API_TIMEOUTS['satnogs'])
            if response.status_code == 200:
                data = response.json()
                for sat in data[:20]:  # Primeros 20 resultados
                    results.append({
                        'source': 'SatNOGS',
                        'norad_id': sat.get('norad_cat_id'),
                        'name': sat.get('name'),
                        'operator': sat.get('operator'),
                        'status': sat.get('status')
                    })
        except Exception as e:
            logger.warning(f"Error buscando en SatNOGS: {e}")
        
        return results
