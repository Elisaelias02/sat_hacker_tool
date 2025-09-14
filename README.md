# SAT HACKER TOOL - Herramienta de Inteligencia Satelital

SatIntel es una herramienta profesional de línea de comandos desarrollada en Python para la recopilación y análisis de datos satelitales con enfoque en inteligencia de seguridad.

## 🚀 Características

- **Recuperación de datos multi-fuente**: Integra Celestrak, Space-Track.org y web scraping
- **Cálculos orbitales precisos**: Posicionamiento satelital y predicción de pases
- **Análisis de seguridad SPARTA**: Evaluación de riesgos basada en framework de inteligencia
- **Interfaz CLI profesional**: Comandos intuitivos con salida formateada
- **Arquitectura modular**: Código bien estructurado y extensible

## 📋 Requisitos

- Python 3.8 o superior
- Conexión a Internet
- Cuenta en Space-Track.org (opcional, para datos completos)

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/satintel.git
cd satintel
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (opcional)

```bash
cp .env.example .env
# Editar .env con tus credenciales de Space-Track.org
```

## 🔧 Configuración

### Credenciales de Space-Track.org

Para acceder a datos completos del catálogo satelital, necesitas una cuenta gratuita en [Space-Track.org](https://www.space-track.org):

1. Regístrate en Space-Track.org
2. Crea un archivo `.env` basado en `.env.example`
3. Agrega tus credenciales:

```env
SPACETRACK_USERNAME=tu_usuario
SPACETRACK_PASSWORD=tu_contraseña
```

## 📖 Uso

### Comandos Básicos

#### Consultar satélite por NORAD ID
```bash
python satintel.py --id 25544
```

#### Consultar satélite por nombre
```bash
python satintel.py --name "ISS"
```

#### Buscar satélites
```bash
python satintel.py --search "starlink"
```

### Análisis Orbital

#### Calcular pases futuros
```bash
python satintel.py --id 25544 --passes --location "20.67,-103.35"
```

#### Personalizar parámetros de pases
```bash
python satintel.py --id 25544 --passes --location "20.67,-103.35" --hours 48 --min-elevation 15
```

### Formatos de Salida

#### Salida en tabla
```bash
python satintel.py --id 25544 --output table
```

#### Salida en JSON
```bash
python satintel.py --id 25544 --output json
```

#### Omitir análisis de seguridad
```bash
python satintel.py --id 25544 --no-security
```

### Opciones de Debug

#### Activar logging detallado
```bash
python satintel.py --id 25544 --verbose
```

## 📊 Ejemplos de Salida

### Información Básica
```
============================================================
                 INFORMACIÓN BÁSICA DEL SATÉLITE
============================================================

NORAD ID................ 25544
Nombre.................. ISS (ZARYA)
País.................... US
Fecha Lanzamiento....... 1998-11-20
Tipo de Objeto.......... PAYLOAD
Estado.................. OPERATIONAL
```

### Análisis SPARTA
```
============================================================
                    ANÁLISIS DE SEGURIDAD SPARTA
============================================================
Satélite: ISS (ZARYA) (ID: 25544)
País de Origen: US
Categoría: Estación Espacial
Nivel de Riesgo: LOW
Confianza del Análisis: 90.0%

TÁCTICAS SPARTA IDENTIFICADAS:
  • Persistencia
  • Comando y Control
  • Recolección

PREOCUPACIONES DE SEGURIDAD:
  ⚠  Capacidades de vigilancia sobre territorio nacional
  ⚠  Recolección de inteligencia geoespacial

RECOMENDACIONES:
  →  Mantener vigilancia rutinaria
  →  Auditar tráfico de comunicaciones sensibles
```

## 🧪 Testing

Ejecutar tests unitarios:

```bash
pytest tests/ -v
```

Ejecutar tests con cobertura:

```bash
pytest tests/ --cov=modules --cov-report=html
```

## 📁 Estructura del Proyecto

```
satintel/
├── satintel.py              # Punto de entrada principal
├── modules/
│   ├── __init__.py
│   ├── sat_data.py          # Recuperación de datos
│   ├── orbital.py           # Cálculos orbitales
│   ├── cli.py               # Interfaz CLI
│   └── security.py          # Análisis SPARTA
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuración
├── tests/
│   ├── __init__.py
│   ├── test_sat_data.py
│   ├── test_orbital.py
│   └── test_security.py
├── requirements.txt
├── README.md
└── .env.example
```

## 🔍 Framework SPARTA

SatIntel implementa una versión adaptada del framework SPARTA para análisis de seguridad satelital:

### Tácticas Principales:
- **Reconocimiento**: Satélites de observación terrestre
- **Comando y Control**: Satélites de comunicaciones
- **Recolección**: Capacidades de inteligencia
- **Impacto**: Potencial disruptivo

### Evaluación de Riesgos:
- **Alto Riesgo**: Países adversarios (RU, CN, KP, IR)
- **Riesgo Medio**: Países no alineados
- **Bajo Riesgo**: Aliados y partners (US, CA, GB, FR, DE, etc.)

## 🚨 Limitaciones y Consideraciones

### Técnicas:
- Los cálculos orbitales son aproximaciones basadas en SGP4
- La precisión depende de la actualidad de los datos TLE
- El web scraping puede fallar si cambian las estructuras web

### Legales:
- Respeta los términos de uso de las APIs utilizadas
- No uses para actividades ilegales o no autorizadas
- Los datos de Space-Track.org están sujetos a restricciones

### Éticas:
- El análisis SPARTA es para fines educativos y de investigación
- No realices actividades de vigilancia sin autorización
- Respeta la privacidad y soberanía nacional

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🔗 Enlaces Útiles

- [Celestrak](https://celestrak.org) - Fuente de datos TLE
- [Space-Track.org](https://www.space-track.org) - Catálogo oficial de objetos espaciales
- [SGP4 Documentation](https://pypi.org/project/sgp4/) - Librería de cálculos orbitales
- [SPARTA Framework](https://attack.mitre.org/) - Framework de análisis de seguridad

## 📞 Soporte

Para reportar bugs o solicitar nuevas funcionalidades, por favor crea un issue en GitHub.

---

**⚠️ Disclaimer**: Esta herramienta está destinada únicamente para fines educativos, de investigación y análisis de seguridad legítimos. El uso indebido de esta herramienta es responsabilidad del usuario.
```

## Instrucciones de Ejecución Completas

### Paso 1: Preparación del Entorno

```bash
# Crear directorio del proyecto
mkdir satintel && cd satintel

# Crear estructura de directorios
mkdir -p modules config tests

# Crear archivos __init__.py
touch modules/__init__.py config/__init__.py tests/__init__.py
```

### Paso 2: Instalación de Dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install requests sgp4 beautifulsoup4 python-dotenv tabulate pytest colorama
```

### Paso 3: Configuración

```bash
# Crear archivo .env (opcional)
echo "SPACETRACK_USERNAME=tu_usuario" > .env
echo "SPACETRACK_PASSWORD=tu_contraseña" >> .env
echo "LOG_LEVEL=INFO" >> .env
```

### Paso 4: Pruebas de Funcionamiento

```bash
# Test básico - ISS
python satintel.py --id 25544

# Test con pases
python satintel.py --id 25544 --passes --location "20.67,-103.35"

# Test de búsqueda
python satintel.py --search "starlink"

# Test con salida en tabla
python satintel.py --id 25544 --output table

# Test sin análisis de seguridad
python satintel.py --id 25544 --no-security
```

### Paso 5: Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar tests específicos
pytest tests/test_sat_data.py -v
```

## Características Técnicas Implementadas

### ✅ Recuperación de Datos Multi-Fuente
- **Celestrak**: TLEs actualizados de múltiples categorías
- **Space-Track.org**: Catálogo oficial con autenticación
- **Web Scraping**: Información adicional de fuentes públicas

### ✅ Cálculos Orbitales Precisos
- **SGP4**: Propagación orbital estándar
- **Coordenadas**: Conversión ECI a geodésicas
- **Pases**: Cálculo de visibilidad desde estación terrestre
- **Elementos**: Extracción completa de parámetros orbitales

### ✅ Análisis de Seguridad SPARTA
- **Taxonomía**: 14 tácticas adaptadas al dominio espacial
- **Categorización**: Clasificación automática por tipo de satélite
- **Evaluación**: Riesgo basado en país de origen y capacidades
- **Reporte**: Formato profesional con recomendaciones

### ✅ Interfaz CLI Profesional
- **Argumentos**: Parser completo con validación
- **Formatos**: Tabla, JSON, detallado
- **Colores**: Salida formateada con colorama
- **Logging**: Sistema profesional de debugging

### ✅ Arquitectura Modular
- **Separación**: Módulos independientes y reutilizables
- **Configuración**: Centralizada en config/settings.py
- **Tests**: Cobertura completa con pytest
- **Documentación**: README detallado con ejemplos

## Casos de Uso Demostrados

### 1. Análisis de la ISS (ID: 25544)
```bash
python satintel.py --id 25544 --passes --location "20.67,-103.35"
```

### 2. Investigación de Constelación Starlink
```bash
python satintel.py --search "starlink" | head -20
```

### 3. Monitoreo de Satélites de Alto Riesgo
```bash
python satintel.py --name "COSMOS" --verbose
```

### 4. Análisis de Capacidades de Observación
```bash
python satintel.py --search "landsat" --output table
```
