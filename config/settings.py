import os
from dotenv import load_dotenv

load_dotenv()

# URLs base de APIs
CELESTRAK_BASE_URL = "https://celestrak.org"
SPACETRACK_BASE_URL = "https://www.space-track.org"
N2YO_BASE_URL = "https://api.n2yo.com/rest/v1/satellite"
SATNOGS_BASE_URL = "https://db.satnogs.org/api"

# Credenciales
SPACETRACK_USERNAME = os.getenv("SPACETRACK_USERNAME")
SPACETRACK_PASSWORD = os.getenv("SPACETRACK_PASSWORD")
N2YO_API_KEY = os.getenv("N2YO_API_KEY", "25K5EB-9FM8MQ-BLDAGL-5B2J")  # Clave demo

# Configuración general
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LATITUDE", "20.67"))
DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LONGITUDE", "-103.35"))

# Constantes físicas
EARTH_RADIUS_KM = 6371.0
MIN_ELEVATION_DEGREES = 10.0

# Timeouts y límites
API_TIMEOUTS = {
    'celestrak': 10,
    'n2yo': 15,
    'satnogs': 10,
    'spacetrack': 15,
    'scraping': 20
}
