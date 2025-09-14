import requests
import logging
import json
from typing import Dict, List, Optional
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
        self.n2yo_api_key = N2YO_API_KEY # Se corrige para que sea una variable de la clase.
    
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
            url = f"{N2YO_BASE_URL}/tle/{satellite_id}&apiKey={self.n2yo_api_key}"
            
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
        """
        Busca satélites por nombre en múltiples fuentes - VERSIÓN CORREGIDA.
        
        Args:
            search_term: Término de búsqueda
            
        Returns:
            Lista de resultados de múltiples fuentes
        """
        results = []
        search_term_clean = search_term.strip().lower()
        
        logger.info(f"Buscando '{search_term}' en múltiples fuentes...")
        
        # 1. Buscar en SatNOGS (más completo)
        satnogs_results = self._search_satnogs(search_term_clean)
        results.extend(satnogs_results)
        
        # 2. Buscar en Celestrak por nombre
        celestrak_results = self._search_celestrak(search_term_clean)
        results.extend(celestrak_results)
        
        # 3. Buscar usando N2YO si tenemos API key
        if hasattr(self, 'n2yo_api_key') and self.n2yo_api_key and self.n2yo_api_key != "25K5EB-9FM8MQ-BLDAGL-5B2J":
            n2yo_results = self._search_n2yo(search_term_clean)
            results.extend(n2yo_results)
        
        # 4. Eliminar duplicados basado en NORAD ID
        unique_results = self._remove_duplicate_satellites(results)
        
        logger.info(f"Encontrados {len(unique_results)} satélites únicos")
        return unique_results

    def _search_satnogs(self, search_term: str) -> List[Dict]:
        """Busca en SatNOGS DB."""
        results = []
        try:
            # Múltiples estrategias de búsqueda en SatNOGS
            search_urls = [
                f"{SATNOGS_BASE_URL}/satellites/?name__icontains={search_term}",
                f"{SATNOGS_BASE_URL}/satellites/?operator__icontains={search_term}",
            ]
            
            for url in search_urls:
                try:
                    logger.info(f"Consultando SatNOGS: {url}")
                    response = self.session.get(url, timeout=API_TIMEOUTS['satnogs'])
                    
                    if response.status_code == 200:
                        data = response.json()
                        for sat in data[:15]:  # Limitar resultados por fuente
                            if sat.get('norad_cat_id'):  # Solo satélites con NORAD ID válido
                                results.append({
                                    'source': 'SatNOGS',
                                    'norad_id': sat.get('norad_cat_id'),
                                    'name': sat.get('name', '').strip(),
                                    'operator': sat.get('operator', '').strip(),
                                    'countries': sat.get('countries', '').strip(),
                                    'status': sat.get('status', '').strip(),
                                    'launched': sat.get('launched', ''),
                                    'description': sat.get('description', '').strip()[:100]
                                })
                    else:
                        logger.warning(f"SatNOGS respuesta: {response.status_code}")
                        
                except requests.RequestException as e:
                    logger.warning(f"Error en consulta SatNOGS: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error general en búsqueda SatNOGS: {e}")
        
        return results

    def _search_celestrak(self, search_term: str) -> List[Dict]:
        """Busca en Celestrak usando múltiples categorías."""
        results = []
        
        try:
            # Categorías principales de Celestrak para buscar
            categories = ['stations', 'visual', 'active', 'weather', 'noaa', 'goes', 'resource']
            
            for category in categories:
                try:
                    url = f"{CELESTRAK_BASE_URL}/NORAD/elements/gp.php?GROUP={category}&FORMAT=tle"
                    logger.info(f"Consultando Celestrak categoría: {category}")
                    
                    response = self.session.get(url, timeout=API_TIMEOUTS['celestrak'])
                    
                    if response.status_code == 200:
                        tle_data = response.text.strip()
                        satellites_found = self._parse_tle_search(tle_data, search_term)
                        results.extend(satellites_found)
                        
                        # Si encontramos suficientes resultados, no seguir buscando
                        if len(results) >= 20:
                            break
                            
                except requests.RequestException as e:
                    logger.warning(f"Error consultando Celestrak {category}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error general en búsqueda Celestrak: {e}")
        
        return results[:15]  # Limitar resultados

    def _search_n2yo(self, search_term: str) -> List[Dict]:
        """Busca usando N2YO API si está disponible."""
        results = []
        
        try:
            # N2YO no tiene búsqueda por nombre directa,
            # pero podemos intentar con satélites populares conocidos
            popular_satellites = {
                'iss': 25544,
                'hubble': 20580,
                'starlink': [44713, 44714, 44715],  # Algunos IDs de Starlink
                'noaa': [43013, 37849, 28654],      # NOAA satellites
                'goes': [41866, 36411, 29155],      # GOES satellites
                'cosmos': [32037, 32038, 32039],    # Algunos Cosmos
                'gps': [32711, 35752, 38833]        # Algunos GPS
            }
            
            # Buscar coincidencias en términos populares
            for keyword, sat_ids in popular_satellites.items():
                if keyword in search_term.lower():
                    if isinstance(sat_ids, list):
                        ids_to_check = sat_ids
                    else:
                        ids_to_check = [sat_ids]
                    
                    for sat_id in ids_to_check:
                        try:
                            url = f"{N2YO_BASE_URL}/tle/{sat_id}&apiKey={self.n2yo_api_key}"
                            response = self.session.get(url, timeout=API_TIMEOUTS['n2yo'])
                            
                            if response.status_code == 200:
                                data = response.json()
                                if 'info' in data:
                                    results.append({
                                        'source': 'N2YO',
                                        'norad_id': sat_id,
                                        'name': data['info'].get('satname', '').strip(),
                                        'operator': 'N/A',
                                        'status': 'N/A',
                                        'launch_date': data['info'].get('launchDate', '')
                                    })
                                    
                        except Exception as e:
                            logger.warning(f"Error consultando N2YO ID {sat_id}: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"Error en búsqueda N2YO: {e}")
        
        return results

    def _parse_tle_search(self, tle_data: str, search_term: str) -> List[Dict]:
        """Parse TLE data y busca coincidencias con el término de búsqueda."""
        results = []
        
        try:
            lines = tle_data.split('\n')
            
            # Procesar TLEs en grupos de 3 líneas
            for i in range(0, len(lines) - 2, 3):
                if i + 2 < len(lines):
                    name_line = lines[i].strip()
                    line1 = lines[i + 1].strip()
                    line2 = lines[i + 2].strip()
                    
                    # Verificar si el nombre contiene el término de búsqueda
                    if (search_term in name_line.lower() and
                        line1.startswith('1 ') and
                        line2.startswith('2 ')):
                        
                        try:
                            # Extraer NORAD ID de la primera línea TLE
                            norad_id = int(line1[2:7])
                            
                            results.append({
                                'source': 'Celestrak',
                                'norad_id': norad_id,
                                'name': name_line.strip(),
                                'operator': 'N/A',
                                'status': 'Active',
                                'classification': line1[7:8],
                                'tle_available': True
                            })
                            
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Error procesando TLE: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"Error parseando TLE para búsqueda: {e}")
        
        return results

    def _remove_duplicate_satellites(self, results: List[Dict]) -> List[Dict]:
        """Elimina satélites duplicados basado en NORAD ID."""
        seen_ids = set()
        unique_results = []
        
        for satellite in results:
            norad_id = satellite.get('norad_id')
            if norad_id and norad_id not in seen_ids:
                seen_ids.add(norad_id)
                unique_results.append(satellite)
        
        # Ordenar por relevancia (SatNOGS primero, luego por nombre)
        def sort_key(sat):
            source_priority = {'SatNOGS': 0, 'Celestrak': 1, 'N2YO': 2}
            return (source_priority.get(sat.get('source', ''), 3), sat.get('name', '').lower())
        
        unique_results.sort(key=sort_key)
        return unique_results
