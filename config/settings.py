import os
from dotenv import load_dotenv

load_dotenv()

# URLs de APIs y fuentes de datos
CELESTRAK_BASE_URL = "https://celestrak.org"
SPACETRACK_BASE_URL = "https://www.space-track.org"

# URLs específicas de TLE
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

# Credenciales Space-Track
SPACETRACK_USERNAME = os.getenv("SPACETRACK_USERNAME")
SPACETRACK_PASSWORD = os.getenv("SPACETRACK_PASSWORD")

# Configuración de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Ubicación por defecto (Las Pintitas, Jalisco, MX)
DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LATITUDE", "20.67"))
DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LONGITUDE", "-103.35"))

# Configuración orbital
EARTH_RADIUS_KM = 6371.0
MIN_ELEVATION_DEGREES = 10.0  # Elevación mínima para considerar un pase visible
