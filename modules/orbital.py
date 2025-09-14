import logging
import math
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
from sgp4.api import Satrec, jday
from sgp4 import exporter
import numpy as np
from config.settings import EARTH_RADIUS_KM, MIN_ELEVATION_DEGREES

logger = logging.getLogger(__name__)

class OrbitalCalculator:
    """Clase para realizar cálculos de mecánica orbital."""
    
    def __init__(self, tle_line1: str, tle_line2: str):
        """
        Inicializa el calculador orbital con datos TLE.
        
        Args:
            tle_line1: Primera línea del TLE
            tle_line2: Segunda línea del TLE
        """
        try:
            self.satellite = Satrec.twoline2rv(tle_line1, tle_line2)
            if self.satellite.error != 0:
                raise ValueError(f"Error al parsear TLE: {self.satellite.error}")
            
            logger.info("Calculador orbital inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar calculador orbital: {e}")
            raise
    
    def get_position_at_time(self, dt: datetime) -> Optional[Dict]:
        """
        Calcula la posición del satélite en un momento específico.
        
        Args:
            dt: Datetime para el cual calcular la posición
            
        Returns:
            Diccionario con lat, lon, alt, velocidad, y otros parámetros
        """
        try:
            # Convertir datetime a Julian Day
            jd, fr = jday(dt.year, dt.month, dt.day, 
                         dt.hour, dt.minute, dt.second + dt.microsecond/1e6)
            
            # Calcular posición y velocidad
            error, position, velocity = self.satellite.sgp4(jd, fr)
            
            if error != 0:
                logger.error(f"Error SGP4: {error}")
                return None
            
            # Convertir de coordenadas ECI a geodésicas
            lat, lon, alt = self._eci_to_geodetic(position, dt)
            
            # Calcular velocidad
            velocity_magnitude = math.sqrt(sum(v**2 for v in velocity))
            
            return {
                'timestamp': dt.isoformat(),
                'latitude': lat,
                'longitude': lon,
                'altitude_km': alt,
                'position_eci': position,
                'velocity_eci': velocity,
                'velocity_km_s': velocity_magnitude,
                'error': error
            }
            
        except Exception as e:
            logger.error(f"Error al calcular posición: {e}")
            return None
    
    def _eci_to_geodetic(self, position_eci: Tuple[float, float, float], 
                        dt: datetime) -> Tuple[float, float, float]:
        """
        Convierte coordenadas ECI a geodésicas (lat/lon/alt).
        
        Args:
            position_eci: Posición en coordenadas ECI (x, y, z) en km
            dt: Datetime para calcular la rotación de la Tierra
            
        Returns:
            Tupla con (latitud, longitud, altitud)
        """
        x, y, z = position_eci
        
        # Calcular distancia al centro de la Tierra
        r = math.sqrt(x**2 + y**2 + z**2)
        
        # Calcular latitud
        lat = math.degrees(math.asin(z / r))
        
        # Calcular longitud considerando la rotación de la Tierra
        lon = math.degrees(math.atan2(y, x))
        
        # Ajustar por rotación de la Tierra (aproximación simple)
        # La Tierra rota 360° en 24 horas = 15°/hora = 0.25°/minuto
        earth_rotation_rate = 15.04107  # grados por hora sideral
        
        # Calcular horas desde el epoch J2000.0
        j2000 = datetime(2000, 1, 1, 12, 0, 0)
        hours_since_j2000 = (dt - j2000).total_seconds() / 3600.0
        
        # Ajustar longitud por rotación
        lon_adjusted = lon - (earth_rotation_rate * hours_since_j2000) % 360
        
        # Normalizar longitud a [-180, 180]
        if lon_adjusted > 180:
            lon_adjusted -= 360
        elif lon_adjusted < -180:
            lon_adjusted += 360
        
        # Calcular altitud
        alt = r - EARTH_RADIUS_KM
        
        return lat, lon_adjusted, alt
    
    def calculate_passes(self, observer_lat: float, observer_lon: float, 
                        observer_alt: float = 0.0, hours_ahead: int = 24,
                        min_elevation: float = MIN_ELEVATION_DEGREES) -> List[Dict]:
        """
        Calcula pases futuros del satélite sobre una ubicación.
        
        Args:
            observer_lat: Latitud del observador
            observer_lon: Longitud del observador  
            observer_alt: Altitud del observador en km
            hours_ahead: Horas hacia adelante para calcular
            min_elevation: Elevación mínima en grados
            
        Returns:
            Lista de diccionarios con información de pases
        """
        passes = []
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=hours_ahead)
        
        logger.info(f"Calculando pases desde {start_time} hasta {end_time}")
        
        # Buscar pases cada 5 minutos
        current_time = start_time
        time_step = timedelta(minutes=5)
        
        current_pass = None
        
        try:
            while current_time <= end_time:
                position_data = self.get_position_at_time(current_time)
                
                if position_data:
                    # Calcular elevación y azimut
                    elevation, azimuth, distance = self._calculate_look_angles(
                        observer_lat, observer_lon, observer_alt,
                        position_data['latitude'], position_data['longitude'], 
                        position_data['altitude_km']
                    )
                    
                    # Verificar si el satélite está visible
                    if elevation >= min_elevation:
                        if not current_pass:
                            # Inicio de un nuevo pase
                            current_pass = {
                                'start_time': current_time,
                                'max_elevation': elevation,
                                'max_elevation_time': current_time,
                                'max_elevation_azimuth': azimuth,
                                'points': []
                            }
                        else:
                            # Actualizar máxima elevación si es necesario
                            if elevation > current_pass['max_elevation']:
                                current_pass['max_elevation'] = elevation
                                current_pass['max_elevation_time'] = current_time
                                current_pass['max_elevation_azimuth'] = azimuth
                        
                        # Agregar punto al pase actual
                        current_pass['points'].append({
                            'time': current_time,
                            'elevation': elevation,
                            'azimuth': azimuth,
                            'distance_km': distance,
                            'satellite_position': position_data
                        })
                    
                    else:
                        # El satélite no está visible
                        if current_pass:
                            # Finalizar el pase actual
                            current_pass['end_time'] = current_pass['points'][-1]['time']
                            current_pass['duration_minutes'] = (
                                current_pass['end_time'] - current_pass['start_time']
                            ).total_seconds() / 60.0
                            
                            passes.append(current_pass)
                            current_pass = None
                
                current_time += time_step
            
            # Si queda un pase abierto al final, cerrarlo
            if current_pass:
                current_pass['end_time'] = current_pass['points'][-1]['time']
                current_pass['duration_minutes'] = (
                    current_pass['end_time'] - current_pass['start_time']
                ).total_seconds() / 60.0
                passes.append(current_pass)
            
            logger.info(f"Encontrados {len(passes)} pases")
            return passes
            
        except Exception as e:
            logger.error(f"Error al calcular pases: {e}")
            return []
    
    def _calculate_look_angles(self, obs_lat: float, obs_lon: float, obs_alt: float,
                              sat_lat: float, sat_lon: float, sat_alt: float) -> Tuple[float, float, float]:
        """
        Calcula ángulos de elevación, azimut y distancia desde observador a satélite.
        
        Args:
            obs_lat, obs_lon, obs_alt: Posición del observador
            sat_lat, sat_lon, sat_alt: Posición del satélite
            
        Returns:
            Tupla con (elevación, azimut, distancia) en grados, grados, km
        """
        # Convertir a radianes
        obs_lat_rad = math.radians(obs_lat)
        obs_lon_rad = math.radians(obs_lon)
        sat_lat_rad = math.radians(sat_lat)
        sat_lon_rad = math.radians(sat_lon)
        
        # Convertir a coordenadas cartesianas (geocéntricas)
        obs_x = (EARTH_RADIUS_KM + obs_alt) * math.cos(obs_lat_rad) * math.cos(obs_lon_rad)
        obs_y = (EARTH_RADIUS_KM + obs_alt) * math.cos(obs_lat_rad) * math.sin(obs_lon_rad)
        obs_z = (EARTH_RADIUS_KM + obs_alt) * math.sin(obs_lat_rad)
        
        sat_x = (EARTH_RADIUS_KM + sat_alt) * math.cos(sat_lat_rad) * math.cos(sat_lon_rad)
        sat_y = (EARTH_RADIUS_KM + sat_alt) * math.cos(sat_lat_rad) * math.sin(sat_lon_rad)
        sat_z = (EARTH_RADIUS_KM + sat_alt) * math.sin(sat_lat_rad)
        
        # Vector del observador al satélite
        dx = sat_x - obs_x
        dy = sat_y - obs_y
        dz = sat_z - obs_z
        
        # Distancia
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        # Transformar a sistema de coordenadas local (ENU - East, North, Up)
        sin_lat = math.sin(obs_lat_rad)
        cos_lat = math.cos(obs_lat_rad)
        sin_lon = math.sin(obs_lon_rad)
        cos_lon = math.cos(obs_lon_rad)
        
        # Matriz de rotación de ECEF a ENU
        east = -sin_lon * dx + cos_lon * dy
        north = -sin_lat * cos_lon * dx - sin_lat * sin_lon * dy + cos_lat * dz
        up = cos_lat * cos_lon * dx + cos_lat * sin_lon * dy + sin_lat * dz
        
        # Calcular elevación
        elevation = math.degrees(math.atan2(up, math.sqrt(east**2 + north**2)))
        
        # Calcular azimut
        azimuth = math.degrees(math.atan2(east, north))
        if azimuth < 0:
            azimuth += 360
        
        return elevation, azimuth, distance
    
    def get_orbital_elements(self) -> Dict:
        """
        Extrae los elementos orbitales del TLE.
        
        Returns:
            Diccionario con elementos orbitales
        """
        try:
            return {
                'satellite_number': self.satellite.satnum,
                'classification': self.satellite.classification,
                'international_designator': self.satellite.intldesg,
                'epoch_year': self.satellite.epochyr,
                'epoch_days': self.satellite.epochdays,
                'mean_motion_derivative': self.satellite.ndot,
                'mean_motion_second_derivative': self.satellite.nddot,
                'bstar_drag': self.satellite.bstar,
                'ephemeris_type': self.satellite.ephtype,
                'element_number': self.satellite.elnum,
                'inclination_deg': math.degrees(self.satellite.inclo),
                'raan_deg': math.degrees(self.satellite.nodeo),
                'eccentricity': self.satellite.ecco,
                'argument_of_perigee_deg': math.degrees(self.satellite.argpo),
                'mean_anomaly_deg': math.degrees(self.satellite.mo),
                'mean_motion_rev_per_day': self.satellite.no_kozai * 1440.0 / (2 * math.pi),
                'revolution_number': self.satellite.revnum
            }
        except Exception as e:
            logger.error(f"Error al extraer elementos orbitales: {e}")
            return {}
