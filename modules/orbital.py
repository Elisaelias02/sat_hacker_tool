import logging
import math
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
from sgp4.api import Satrec, jday
from config.settings import EARTH_RADIUS_KM, MIN_ELEVATION_DEGREES

logger = logging.getLogger(__name__)

class OrbitalCalculator:
    """Calculador de mecánica orbital simplificado y limpio."""
    
    def __init__(self, tle_line1: str, tle_line2: str):
        """Inicializa con datos TLE."""
        try:
            self.satellite = Satrec.twoline2rv(tle_line1, tle_line2)
            if self.satellite.error != 0:
                raise ValueError(f"Error SGP4: {self.satellite.error}")
            logger.info("Calculador orbital inicializado")
        except Exception as e:
            logger.error(f"Error inicializando orbital: {e}")
            raise
    
    def get_current_position(self) -> Optional[Dict]:
        """Obtiene la posición actual del satélite."""
        return self.get_position_at_time(datetime.utcnow())
    
    def get_position_at_time(self, dt: datetime) -> Optional[Dict]:
        """Calcula posición en momento específico."""
        try:
            jd, fr = jday(dt.year, dt.month, dt.day, 
                         dt.hour, dt.minute, dt.second)
            
            error, position, velocity = self.satellite.sgp4(jd, fr)
            if error != 0:
                return None
            
            lat, lon, alt = self._eci_to_geodetic(position, dt)
            speed = math.sqrt(sum(v**2 for v in velocity))
            
            return {
                'timestamp': dt.isoformat(),
                'latitude': lat,
                'longitude': lon,
                'altitude_km': alt,
                'velocity_km_s': speed,
                'position_eci': position,
                'velocity_eci': velocity
            }
        except Exception as e:
            logger.error(f"Error calculando posición: {e}")
            return None
    
    def calculate_passes(self, observer_lat: float, observer_lon: float, 
                        hours_ahead: int = 24) -> List[Dict]:
        """Calcula pases futuros sobre una ubicación."""
        passes = []
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=hours_ahead)
        
        current_time = start_time
        time_step = timedelta(minutes=5)
        current_pass = None
        
        while current_time <= end_time:
            position = self.get_position_at_time(current_time)
            if not position:
                current_time += time_step
                continue
            
            elevation, azimuth, distance = self._calculate_look_angles(
                observer_lat, observer_lon, 0.0,
                position['latitude'], position['longitude'], 
                position['altitude_km']
            )
            
            if elevation >= MIN_ELEVATION_DEGREES:
                if not current_pass:
                    current_pass = {
                        'start_time': current_time,
                        'max_elevation': elevation,
                        'max_elevation_time': current_time,
                        'points': []
                    }
                
                if elevation > current_pass['max_elevation']:
                    current_pass['max_elevation'] = elevation
                    current_pass['max_elevation_time'] = current_time
                
                current_pass['points'].append({
                    'time': current_time,
                    'elevation': elevation,
                    'azimuth': azimuth,
                    'distance_km': distance
                })
            else:
                if current_pass:
                    current_pass['end_time'] = current_pass['points'][-1]['time']
                    current_pass['duration_minutes'] = (
                        current_pass['end_time'] - current_pass['start_time']
                    ).total_seconds() / 60.0
                    passes.append(current_pass)
                    current_pass = None
            
            current_time += time_step
        
        return passes
    
    def _eci_to_geodetic(self, position: Tuple[float, float, float], 
                        dt: datetime) -> Tuple[float, float, float]:
        """Convierte ECI a coordenadas geodésicas."""
        x, y, z = position
        r = math.sqrt(x**2 + y**2 + z**2)
        
        lat = math.degrees(math.asin(z / r))
        lon = math.degrees(math.atan2(y, x))
        
        # Ajuste por rotación terrestre
        hours_since_j2000 = (dt - datetime(2000, 1, 1, 12, 0, 0)).total_seconds() / 3600.0
        lon_adjusted = lon - (15.04107 * hours_since_j2000) % 360
        
        if lon_adjusted > 180:
            lon_adjusted -= 360
        elif lon_adjusted < -180:
            lon_adjusted += 360
        
        alt = r - EARTH_RADIUS_KM
        return lat, lon_adjusted, alt
    
    def _calculate_look_angles(self, obs_lat: float, obs_lon: float, obs_alt: float,
                              sat_lat: float, sat_lon: float, sat_alt: float) -> Tuple[float, float, float]:
        """Calcula ángulos de observación."""
        obs_lat_rad = math.radians(obs_lat)
        obs_lon_rad = math.radians(obs_lon)
        sat_lat_rad = math.radians(sat_lat)
        sat_lon_rad = math.radians(sat_lon)
        
        # Coordenadas cartesianas
        obs_x = (EARTH_RADIUS_KM + obs_alt) * math.cos(obs_lat_rad) * math.cos(obs_lon_rad)
        obs_y = (EARTH_RADIUS_KM + obs_alt) * math.cos(obs_lat_rad) * math.sin(obs_lon_rad)
        obs_z = (EARTH_RADIUS_KM + obs_alt) * math.sin(obs_lat_rad)
        
        sat_x = (EARTH_RADIUS_KM + sat_alt) * math.cos(sat_lat_rad) * math.cos(sat_lon_rad)
        sat_y = (EARTH_RADIUS_KM + sat_alt) * math.cos(sat_lat_rad) * math.sin(sat_lon_rad)
        sat_z = (EARTH_RADIUS_KM + sat_alt) * math.sin(sat_lat_rad)
        
        dx, dy, dz = sat_x - obs_x, sat_y - obs_y, sat_z - obs_z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        # Transformación a ENU
        sin_lat, cos_lat = math.sin(obs_lat_rad), math.cos(obs_lat_rad)
        sin_lon, cos_lon = math.sin(obs_lon_rad), math.cos(obs_lon_rad)
        
        east = -sin_lon * dx + cos_lon * dy
        north = -sin_lat * cos_lon * dx - sin_lat * sin_lon * dy + cos_lat * dz
        up = cos_lat * cos_lon * dx + cos_lat * sin_lon * dy + sin_lat * dz
        
        elevation = math.degrees(math.atan2(up, math.sqrt(east**2 + north**2)))
        azimuth = math.degrees(math.atan2(east, north))
        if azimuth < 0:
            azimuth += 360
        
        return elevation, azimuth, distance
