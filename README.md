# SAT HACKER TOOL - Herramienta de Inteligencia Satelital

SatIntel 2.0 - Herramienta Profesional de Inteligencia Satelital
Mostrar imagen
Mostrar imagen
Mostrar imagen
SatIntel es una herramienta profesional de línea de comandos desarrollada en Python para la recopilación, análisis y evaluación de datos satelitales con enfoque en inteligencia de seguridad basada en el framework SPARTA.
🚀 Características Principales
📡 Recuperación de Datos Multi-Fuente

Celestrak: TLEs oficiales de NORAD/NASA (siempre funciona)
N2YO API: Seguimiento satelital en tiempo real
SatNOGS DB: Base de datos colaborativa de radioaficionados
Web Scraping: Información detallada de fuentes públicas

🛰️ Análisis Orbital Preciso

Cálculos de posición en tiempo real usando SGP4
Predicción de pases sobre ubicaciones específicas
Elementos orbitales completos (inclinación, excentricidad, etc.)
Conversión automática de coordenadas ECI a geodésicas

🔒 Inteligencia de Seguridad SPARTA

Evaluación automatizada de riesgos por país de origen
Categorización por tipo de misión y capacidades
Identificación de tácticas y técnicas potenciales
Generación de recomendaciones de seguridad

💻 Interfaz CLI Profesional

Comandos intuitivos con validación completa
Múltiples formatos de salida (tabla, JSON, detallado)
Salida coloreada y formateada
Manejo robusto de errores

📋 Requisitos

Python: 3.8 o superior
Conexión a Internet: Para acceso a APIs y fuentes de datos
Sistema Operativo: Linux, macOS, Windows
Memoria RAM: Mínimo 512MB disponible

📦 Dependencias
txtrequests>=2.31.0      # Comunicación HTTP
sgp4>=2.21           # Cálculos orbitales SGP4
beautifulsoup4>=4.12.0 # Web scraping
python-dotenv>=1.0.0  # Variables de entorno
tabulate>=0.9.0      # Formateo de tablas
pytest>=7.4.0        # Testing framework
colorama>=0.4.6      # Colores en terminal
lxml>=4.9.0          # Parser XML/HTML optimizado
🛠️ Instalación
Instalación Rápida
bash# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/satintel.git
cd satintel

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (opcional)
cp .env.example .env
# Editar .env con tus credenciales
Verificar Instalación
bashpython satintel.py --id 25544
⚙️ Configuración
Variables de Entorno (.env)
env# Credenciales Space-Track.org (opcional pero recomendado)
SPACETRACK_USERNAME=tu_usuario
SPACETRACK_PASSWORD=tu_contraseña

# API Key N2YO (registro gratuito recomendado)
N2YO_API_KEY=tu_clave_n2yo

# Configuración general
LOG_LEVEL=INFO
DEFAULT_LATITUDE=20.67
DEFAULT_LONGITUDE=-103.35
Obtener Credenciales
Space-Track.org (Opcional)

Registrarse en Space-Track.org
Crear cuenta gratuita
Agregar credenciales al archivo .env

N2YO API (Recomendado)

Registrarse en N2YO.com
Obtener API key gratuita (1000 requests/hora)
Agregar clave al archivo .env

📖 Uso
Comandos Básicos
Consultar Satélite por NORAD ID
bashpython satintel.py --id 25544
Consultar Satélite por Nombre
bashpython satintel.py --name "ISS"
Buscar Satélites
bashpython satintel.py --search "starlink"
python satintel.py --search "cosmos"
Análisis Orbital
Calcular Pases Futuros
bash# Pases sobre Las Pintitas, Jalisco (ubicación por defecto)
python satintel.py --id 25544 --passes

# Pases sobre ubicación específica
python satintel.py --id 25544 --passes --location "40.7128,-74.0060"  # Nueva York

# Personalizar parámetros
python satintel.py --id 25544 --passes --hours 48 --location "19.4326,-99.1332"  # Ciudad de México, 48 horas
Formatos de Salida
Salida Detallada (por defecto)
bashpython satintel.py --id 25544
Formato Tabla
bashpython satintel.py --id 25544 --output table
Formato JSON
bashpython satintel.py --id 25544 --output json
Opciones Avanzadas
Omitir Análisis de Seguridad
bashpython satintel.py --id 25544 --no-security
Salida Detallada con Logs
bashpython satintel.py --id 25544 --verbose
Análisis Completo
bashpython satintel.py --id 25544 --passes --location "20.67,-103.35" --hours 24 --verbose
📊 Ejemplos de Salida
Información Básica
============================================================
                INFORMACIÓN BÁSICA DEL SATÉLITE
============================================================
Fuentes: Celestrak, N2YO, SatNOGS

NORAD ID................. 25544
Nombre................... ISS (ZARYA)
Operador................. NASA/Roscosmos/ESA/JAXA/CSA
País..................... INTERNATIONAL
Estado................... OPERATIONAL
Lanzamiento.............. 1998-11-20
Sitio Web................ https://www.nasa.gov/mission_pages/station/

============================================================
                    INFORMACIÓN DE MISIÓN
============================================================

Descripción.............. International Space Station, habitable artificial satellite
Tipo..................... Space Station
Órbita................... LEO

============================================================
                  ESPECIFICACIONES TÉCNICAS
============================================================

Size..................... Large
Freq Bands............... VHF, UHF, S-band
Modes.................... FM, SSTV, Packet

============================================================
                    ELEMENTOS ORBITALES
============================================================

Inclinación.............. 51.64°
Excentricidad............ 0.000123
Movimiento Medio......... 15.488194 rev/día
RAAN..................... 339.79°
Arg. Perigeo............. 356.85°

============================================================
                     POSICIÓN ACTUAL
============================================================

Tiempo UTC............... 2025-09-14 15:30:45
Latitud.................. 23.4567°
Longitud................. -45.6789°
Altitud.................. 408.12 km
Velocidad................ 7.66 km/s
Análisis SPARTA
============================================================
                 ANÁLISIS DE SEGURIDAD SPARTA
============================================================
Satélite: ISS (ZARYA) (ID: 25544)
País: INTERNATIONAL
Categoría: Estación Espacial
Nivel de Riesgo: LOW
Confianza: 85.0%

PREOCUPACIONES DE SEGURIDAD:
  ⚠ Capacidades de vigilancia sobre territorio nacional
  ⚠ Recolección de inteligencia geoespacial
  ⚠ Satélite operacionalmente activo - capacidades en tiempo real

RECOMENDACIONES:
  → Mantener vigilancia rutinaria
  → Auditar tráfico de comunicaciones sensibles
  → Evaluar exposición de infraestructura crítica

============================================================
Pases Futuros
============================================================
                   PASES FUTUROS (24h)
============================================================
Ubicación: 20.67°, -103.35°

┌───┬────────────┬──────────┬───────────┐
│ # │ Inicio     │ Duración │ Elev. Máx │
├───┼────────────┼──────────┼───────────┤
│ 1 │ 09-14 18:45│ 6.2 min  │ 45.2°     │
│ 2 │ 09-14 20:22│ 4.8 min  │ 28.7°     │
│ 3 │ 09-15 06:15│ 7.1 min  │ 62.4°     │
│ 4 │ 09-15 07:52│ 5.5 min  │ 35.9°     │
└───┴────────────┴──────────┴───────────┘
🔍 Casos de Uso
1. Análisis de la Estación Espacial Internacional
bashpython satintel.py --id 25544 --passes --location "19.4326,-99.1332"
Resultado: Información completa, pases sobre Ciudad de México, análisis de seguridad bajo
2. Investigación de Constelación Starlink
bashpython satintel.py --search "starlink"
Resultado: Lista de satélites Starlink activos con información de operador
3. Monitoreo de Satélites de Alto Riesgo
bashpython satintel.py --search "cosmos"
Resultado: Satélites militares rusos con análisis SPARTA de alto riesgo
4. Análisis de Satélites Meteorológicos
bashpython satintel.py --name "NOAA"
Resultado: Información de satélites meteorológicos estadounidenses
5. Estudio de Navegación Global
bashpython satintel.py --search "gps"
python satintel.py --search "glonass"
python satintel.py --search "galileo"
Resultado: Comparación de sistemas de navegación global
📁 Estructura del Proyecto
satintel/
├── satintel.py              # Punto de entrada principal
├── modules/
│   ├── __init__.py
│   ├── data_sources.py      # Gestión de fuentes de datos
│   ├── orbital.py           # Cálculos de mecánica orbital
│   ├── security.py          # Análisis de seguridad SPARTA
│   ├── cli.py               # Interfaz de línea de comandos
│   └── utils.py             # Utilidades y funciones comunes
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuración centralizada
├── tests/
│   ├── __init__.py
│   ├── test_data_sources.py # Tests para fuentes de datos
│   ├── test_orbital.py      # Tests para cálculos orbitales
│   └── test_security.py     # Tests para análisis SPARTA
├── requirements.txt         # Dependencias del proyecto
├── .env.example            # Ejemplo de variables de entorno
├── .gitignore              # Archivos ignorados por Git
├── LICENSE                 # Licencia del proyecto
└── README.md               # Este archivo
🧪 Testing
Ejecutar Tests
bash# Todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/test_data_sources.py -v
pytest tests/test_orbital.py -v
pytest tests/test_security.py -v

# Tests con cobertura
pytest tests/ --cov=modules --cov-report=html
Tests de Integración
bash# Test básico de funcionamiento
python satintel.py --id 25544 --no-security

# Test de todas las fuentes
python satintel.py --id 25544 --verbose

# Test de búsqueda
python satintel.py --search "test"
🌐 Fuentes de Datos
🔴 Fuentes Primarias (Críticas)
Celestrak

URL: https://celestrak.org
Datos: TLEs oficiales de NORAD/NASA
Actualización: Diaria
Confiabilidad: 99.9%
Costo: Gratuito

N2YO API

URL: https://www.n2yo.com/api/
Datos: Seguimiento en tiempo real, información de satélites
Límites: 1000 requests/hora (gratuito)
Confiabilidad: 95%
Registro: Requerido (gratuito)

🟡 Fuentes Secundarias (Importantes)
SatNOGS DB

URL: https://db.satnogs.org
Datos: Base de datos colaborativa, información de radioaficionados
Actualización: Continua
Confiabilidad: 90%
Costo: Gratuito

Space-Track.org

URL: https://www.space-track.org
Datos: Catálogo oficial del Departamento de Defensa de EE.UU.
Acceso: Requiere registro y autenticación
Confiabilidad: 99%
Limitaciones: Problemas de autenticación actuales

🟢 Fuentes Complementarias (Opcionales)
Web Scraping

Gunter's Space Page
Orbit.ing-info.net
Páginas públicas de información satelital

🔒 Framework SPARTA
SatIntel implementa una versión adaptada del framework SPARTA para análisis de seguridad espacial:
Tácticas Identificadas

Reconocimiento: Satélites de observación terrestre
Comando y Control: Satélites de comunicaciones
Recolección: Capacidades de inteligencia
Impacto: Potencial disruptivo
Persistencia: Capacidades de larga duración

Evaluación de Riesgos

Alto Riesgo: RU, CN, KP, IR
Riesgo Medio: Países no alineados
Bajo Riesgo: US, CA, GB, FR, DE, JP, AU

Categorías de Satélites

Comunicaciones
Observación Terrestre
Navegación
Meteorológicos
Científicos
Militares
Estaciones Espaciales

⚠️ Limitaciones y Consideraciones
Técnicas

Los cálculos orbitales son aproximaciones basadas en SGP4
La precisión depende de la actualidad de los datos TLE
Algunas fuentes pueden tener rate limits o estar temporalmente inaccesibles

Legales

Respeta los términos de uso de todas las APIs utilizadas
No usar para actividades ilegales o no autorizadas
Los datos de Space-Track.org están sujetos a restricciones gubernamentales

Éticas

El análisis SPARTA es para fines educativos y de investigación
No realizar actividades de vigilancia sin autorización apropiada
Respetar la privacidad y soberanía nacional

🐛 Resolución de Problemas
Problemas Comunes
Error de Imports
bashModuleNotFoundError: No module named 'requests'
Solución: pip install -r requirements.txt
Error de Credenciales
bashWARNING: Credenciales de Space-Track no configuradas
Solución: Configurar .env o usar solo Celestrak con --no-security
Error de Ubicación
bashValueError: Formato de ubicación inválido
Solución: Usar formato "lat,lon" (ej: "20.67,-103.35")
No se Encuentran Datos
bash❌ No se encontraron datos para el satélite
Solución: Verificar NORAD ID o nombre del satélite
Debugging
bash# Salida detallada
python satintel.py --id 25544 --verbose

# Solo datos básicos
python satintel.py --id 25544 --no-security

# Verificar fuentes
python satintel.py --search "test" --verbose
🤝 Contribuciones
Las contribuciones son bienvenidas. Para contribuir:

Fork el repositorio
Crear rama para tu feature (git checkout -b feature/nueva-funcionalidad)
Commit cambios (git commit -am 'Agregar nueva funcionalidad')
Push a la rama (git push origin feature/nueva-funcionalidad)
Crear Pull Request

Guías de Contribución

Seguir PEP 8 para estilo de código
Agregar tests para nuevas funcionalidades
Actualizar documentación según sea necesario
Probar en múltiples plataformas

📄 Licencia
Este proyecto está bajo la Licencia MIT. Ver LICENSE para más detalles.
MIT License

Copyright (c) 2025 SatIntel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
🔗 Enlaces Útiles
APIs y Fuentes de Datos

Celestrak - TLEs oficiales
N2YO API - API de seguimiento satelital
SatNOGS DB - Base de datos colaborativa
Space-Track.org - Catálogo oficial

Documentación Técnica

SGP4 Library - Cálculos orbitales
SPARTA Framework - Framework de análisis
TLE Format - Formato TLE

Herramientas Relacionadas

Gpredict - Software de seguimiento satelital
Orbitron - Tracker satelital para Windows
ISS Tracker - Rastreador oficial de la ISS

📞 Soporte
Reportar Bugs
Crear un issue en GitHub con:

Descripción del problema
Comando ejecutado
Salida de error completa
Sistema operativo y versión de Python

Solicitar Features
Crear un issue con:

Descripción de la funcionalidad deseada
Casos de uso
Beneficios esperados

Preguntas Generales

Revisar este README
Consultar issues existentes
Crear nuevo issue si es necesario


⚠️ Disclaimer: Esta herramienta está destinada únicamente para fines educativos, de investigación y análisis de seguridad legítimos. El uso indebido de esta herramienta es responsabilidad del usuario. Los autores no se hacen responsables del mal uso de la información obtenida.
🌟 Agradecimientos: Agradecemos a todas las organizaciones que proporcionan datos satelitales abiertos: NORAD, NASA, Celestrak, N2YO, SatNOGS y la comunidad de radioaficionados worldwide.

SatIntel v2.0 - Desarrollado con ❤️ para la comunidad de inteligencia espacial
