# SAT HACKER TOOL - Herramienta de Inteligencia Satelital

Sat Hacker Tool es una herramienta  de **línea de comandos** desarrollada en **Python** para la recopilación, análisis y evaluación de datos satelitales con enfoque en inteligencia de seguridad basada en el framework **SPARTA**.

-----

## 🚀 Características Principales

  * **📡 Recuperación de Datos Multi-Fuente:**

      * **Celestrak:** TLEs oficiales de NORAD/NASA
      * **N2YO API:** Seguimiento satelital en tiempo real
      * **SatNOGS DB:** Base de datos colaborativa de radioaficionados
      * **Web Scraping:** Información detallada de fuentes públicas

  * **🛰️ Análisis Orbital Preciso:**

      * Cálculos de posición en tiempo real usando **SGP4**
      * Predicción de pases sobre ubicaciones específicas
      * Elementos orbitales completos (inclinación, excentricidad, etc.)
      * Conversión automática de coordenadas ECI a geodésicas

  * **🔒 Inteligencia de Seguridad SPARTA:**

      * Evaluación automatizada de riesgos por país de origen
      * Categorización por tipo de misión y capacidades
      * Identificación de tácticas y técnicas potenciales
      * Generación de recomendaciones de seguridad

  * **💻 Interfaz CLI:**

      * Comandos intuitivos con validación completa
      * Múltiples formatos de salida (tabla, JSON, detallado)
      * Salida coloreada y formateada
      * Manejo robusto de errores

-----

## 📋 Requisitos

  * **Python:** 3.8 o superior
  * **Conexión a Internet:** Para acceso a APIs y fuentes de datos
  * **Sistema Operativo:** Linux, macOS, Windows
  * **Memoria RAM:** Mínimo 512MB disponible

### 📦 Dependencias

```txt
requests>=2.31.0      # Comunicación HTTP
sgp4>=2.21           # Cálculos orbitales SGP4
beautifulsoup4>=4.12.0 # Web scraping
python-dotenv>=1.0.0  # Variables de entorno
tabulate>=0.9.0      # Formateo de tablas
pytest>=7.4.0        # Testing framework
colorama>=0.4.6      # Colores en terminal
lxml>=4.9.0          # Parser XML/HTML optimizado
```

-----

## 🛠️ Instalación

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/Elisaelias02/sat_hacker_tool
cd sat_hacker_tool

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (opcional)
cp .env.example .env
# Editar .env con tus credenciales
```

### Verificar Instalación

```bash
python satintel.py --id 25544
```

-----

## ⚙️ Configuración

### Variables de Entorno (`.env`)

```env
# Credenciales Space-Track.org (opcional pero recomendado)
SPACETRACK_USERNAME=tu_usuario
SPACETRACK_PASSWORD=tu_contraseña

# API Key N2YO (registro gratuito recomendado)
N2YO_API_KEY=tu_clave_n2yo

# Configuración general
LOG_LEVEL=INFO
DEFAULT_LATITUDE=20.67
DEFAULT_LONGITUDE=-103.35
```

### Obtener Credenciales

  * **Space-Track.org (Opcional):**

      * Registrarse en [Space-Track.org](https://www.space-track.org)
      * Crear cuenta gratuita
      * Agregar credenciales al archivo `.env`

  * **N2YO API (Recomendado):**

      * Registrarse en [N2YO.com](https://www.n2yo.com)
      * Obtener API key gratuita (1000 requests/hora)
      * Agregar clave al archivo `.env`

-----

## 📖 Uso

### Comandos Básicos

  * **Consultar Satélite por NORAD ID:**

    ```bash
    python satintel.py --id 25544
    ```

  * **Consultar Satélite por Nombre:**

    ```bash
    python satintel.py --name "ISS"
    ```

  * **Buscar Satélites:**

    ```bash
    python satintel.py --search "starlink"
    python satintel.py --search "cosmos"
    ```

### Análisis Orbital

  * **Calcular Pases Futuros:**
    ```bash

    # Pases sobre ubicación específica
    python satintel.py --id 25544 --passes --location "40.7128,-74.0060"  # Nueva York

    # Personalizar parámetros
    python satintel.py --id 25544 --passes --hours 48 --location "19.4326,-99.1332"  # Ciudad de México, 48 horas
    ```

### Formatos de Salida

  * **Salida Detallada (por defecto):**

    ```bash
    python satintel.py --id 25544
    ```

  * **Formato Tabla:**

    ```bash
    python satintel.py --id 25544 --output table
    ```

  * **Formato JSON:**

    ```bash
    python satintel.py --id 25544 --output json
    ```

### Opciones Avanzadas

  * **Omitir Análisis de Seguridad:**

    ```bash
    python satintel.py --id 25544 --no-security
    ```

  * **Salida Detallada con Logs:**

    ```bash
    python satintel.py --id 25544 --verbose
    ```

  * **Análisis Completo:**

    ```bash
    python satintel.py --id 25544 --passes --location "20.67,-103.35" --hours 24 --verbose
    ```

-----

## 📊 Ejemplos de Salida

### Información Básica

```
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
```

### Análisis SPARTA

```
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
```

### Pases Futuros

```
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
```

-----

## 🔍 Casos de Uso

1.  **Análisis de la Estación Espacial Internacional:**

    ```bash
    python satintel.py --id 25544 --passes --location "19.4326,-99.1332"
    ```

      * **Resultado:** Información completa, pases sobre Ciudad de México, análisis de seguridad bajo.

2.  **Investigación de Constelación Starlink:**

    ```bash
    python satintel.py --search "starlink"
    ```

      * **Resultado:** Lista de satélites Starlink activos con información de operador.

3.  **Monitoreo de Satélites de Alto Riesgo:**

    ```bash
    python satintel.py --search "cosmos"
    ```

      * **Resultado:** Satélites militares rusos con análisis SPARTA de alto riesgo.

4.  **Análisis de Satélites Meteorológicos:**

    ```bash
    python satintel.py --name "NOAA"
    ```

      * **Resultado:** Información de satélites meteorológicos estadounidenses.

5.  **Estudio de Navegación Global:**

    ```bash
    python satintel.py --search "gps"
    python satintel.py --search "glonass"
    python satintel.py --search "galileo"
    ```

      * **Resultado:** Comparación de sistemas de navegación global.

-----

## 📁 Estructura del Proyecto

```
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
```

-----

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/test_data_sources.py -v
pytest tests/test_orbital.py -v
pytest tests/test_security.py -v

# Tests con cobertura
pytest tests/ --cov=modules --cov-report=html
```

### Tests de Integración

```bash
# Test básico de funcionamiento
python satintel.py --id 25544 --no-security

# Test de todas las fuentes
python satintel.py --id 25544 --verbose

# Test de búsqueda
python satintel.py --search "test"
```

-----

## 🌐 Fuentes de Datos

  * **🔴 Fuentes Primarias (Críticas):**

      * **Celestrak:** TLEs oficiales de NORAD/NASA. Actualización diaria. Confiabilidad 99.9%. Gratuito.
      * **N2YO API:** Seguimiento en tiempo real. 1000 requests/hora (gratuito). Confiabilidad 95%.

  * **🟡 Fuentes Secundarias (Importantes):**

      * **SatNOGS DB:** Base de datos colaborativa. Actualización continua. Confiabilidad 90%. Gratuito.
      * **Space-Track.org:** Catálogo oficial del Departamento de Defensa de EE.UU. Requiere registro y autenticación. Confiabilidad 99%.

  * **🟢 Fuentes Complementarias (Opcionales):**

      * Web Scraping de Gunter's Space Page, Orbit.ing-info.net y otras páginas públicas.

-----

## 🔒 Framework SPARTA

Sat Hacker Tool implementa una versión adaptada del framework **SPARTA** para análisis de seguridad espacial, clasificando satélites por:

  * **Tácticas Identificadas:** Reconocimiento, Comando y Control, Recolección, Impacto y Persistencia.
  * **Evaluación de Riesgos:** Alto (RU, CN, KP, IR), Medio (Países no alineados), Bajo (US, CA, GB, FR, DE, JP, AU).
  * **Categorías de Satélites:** Comunicaciones, Observación Terrestre, Navegación, Meteorológicos, Científicos, Militares, Estaciones Espaciales.

-----

## ⚠️ Limitaciones y Consideraciones

  * **Técnicas:** Los cálculos orbitales son aproximaciones; la precisión depende de la actualidad de los datos TLE.
  * **Legales:** Respetar los términos de uso de las APIs. No usar para actividades ilegales.
  * **Éticas:** El análisis SPARTA es para fines educativos y de investigación. Respetar la privacidad y soberanía nacional.

-----

## 🐛 Resolución de Problemas

### Problemas Comunes

  * **`ModuleNotFoundError: No module named 'requests'`:**

      * **Solución:** `pip install -r requirements.txt`

  * **`WARNING: Credenciales de Space-Track no configuradas`:**

      * **Solución:** Configurar las credenciales en `.env` o usar `--no-security` para omitir la fuente.

  * **`ValueError: Formato de ubicación inválido`:**

      * **Solución:** Usar el formato `"lat,lon"` (ej: `"20.67,-103.35"`).

  * **`❌ No se encontraron datos para el satélite`:**

      * **Solución:** Verificar el NORAD ID o el nombre del satélite.

-----

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1.  Hacer **fork** del repositorio.
2.  Crear una rama para la nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
3.  Hacer **commit** de los cambios.
4.  Hacer **push** a la rama.
5.  Crear un **Pull Request**.

-----

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver [LICENSE](https://www.google.com/search?q=LICENSE) para más detalles.

-----

## 🔗 Enlaces Útiles

  * **APIs y Fuentes de Datos:**

      * [Celestrak](https://celestrak.org) - TLEs oficiales
      * [N2YO API](https://www.n2yo.com/api/) - API de seguimiento satelital
      * [SatNOGS DB](https://db.satnogs.org) - Base de datos colaborativa
      * [Space-Track.org](https://www.space-track.org) - Catálogo oficial

  * **Documentación Técnica:**

      * [SGP4 Library](https://pypi.org/project/sgp4/) - Cálculos orbitales
      * [SPARTA Framework](https://www.google.com/search?q=SPARTA+framework) - Framework de análisis
      * [TLE Format](https://en.wikipedia.org/wiki/Two-line_element_set) - Formato TLE

  * **Herramientas Relacionadas:**

      * [Gpredict](http://gpredict.oz9aec.net/) - Software de seguimiento satelital
      * [Orbitron](https://www.google.com/search?q=https://www.stoff.pl/orbitron/) - Tracker satelital para Windows
      * [ISS Tracker](https://www.google.com/search?q=https://spotthestation.nasa.gov/tracking_map.cfm) - Rastreador oficial de la ISS

-----

## 📞 Soporte

  * **Reportar Bugs:** Crear un [issue en GitHub](https://www.google.com/search?q=https://github.com/tu-usuario/satintel/issues) con la descripción del problema, comando ejecutado, salida de error completa, sistema operativo y versión de Python.
  * **Solicitar Features:** Crear un [issue](https://www.google.com/search?q=https://github.com/tu-usuario/satintel/issues) con la descripción de la funcionalidad deseada, casos de uso y beneficios esperados.
  * **Preguntas Generales:** Revisar este README, consultar issues existentes o crear un nuevo issue si es necesario.

-----

**⚠️ Disclaimer:** Esta herramienta está destinada únicamente para fines educativos, de investigación y análisis de seguridad legítimos. El uso indebido de esta herramienta es responsabilidad del usuario. La autora no se hace responsable del mal uso de la información obtenida.

**🌟 Agradecimientos:** Agradezco a todas las organizaciones que proporcionan datos satelitales abiertos y a mi gatita Sky que me acompaño en el desarrollo de este proyecto.

**Sat HACKER Tool v1.0** - Desarrollado por Cinn4mor0ll (Elisa Elias) para la comunidad de inteligencia espacial.
