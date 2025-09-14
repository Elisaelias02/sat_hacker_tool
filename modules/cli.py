import argparse
import logging
import sys
from typing import Optional
from datetime import datetime
from tabulate import tabulate
from colorama import init, Fore, Style
from modules.sat_data import SatelliteDataRetriever, parse_tle
from modules.orbital import OrbitalCalculator
from modules.security import SPARTAAnalyzer
from config.settings import DEFAULT_LATITUDE, DEFAULT_LONGITUDE

# Inicializar colorama para colores en terminal
init(autoreset=True)

logger = logging.getLogger(__name__)

class SatIntelCLI:
    """Interfaz de línea de comandos principal."""
    
    def __init__(self):
        """Inicializa la interfaz CLI."""
        self.data_retriever = SatelliteDataRetriever()
        self.sparta_analyzer = SPARTAAnalyzer()
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Crea el parser de argumentos de línea de comandos."""
        parser = argparse.ArgumentParser(
            description="SatIntel - Herramienta de Inteligencia Satelital",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Ejemplos de uso:
  python satintel.py --id 25544
  python satintel.py --name "ISS"
  python satintel.py --id 25544 --location "20.67,-103.35"
  python satintel.py --id 25544 --passes --location "20.67,-103.35"
  python satintel.py --search "starlink"
            """
        )
        
        # Grupo de identificación del satélite
        id_group = parser.add_mutually_exclusive_group(required=True)
        id_group.add_argument(
            '--id', 
            type=int,
            help='NORAD ID del satélite'
        )
        id_group.add_argument(
            '--name', 
            type=str,
            help='Nombre del satélite'
        )
        id_group.add_argument(
            '--search',
            type=str,
            help='Buscar satélites por nombre (muestra lista de resultados)'
        )
        
        # Opciones de ubicación
        parser.add_argument(
            '--location',
            type=str,
            default=f"{DEFAULT_LATITUDE},{DEFAULT_LONGITUDE}",
            help='Ubicación del observador en formato "lat,lon" (default: Las Pintitas, Jalisco)'
        )
        
        # Opciones de análisis
        parser.add_argument(
            '--passes',
            action='store_true',
            help='Calcular pases futuros sobre la ubicación especificada'
        )
        
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Horas hacia adelante para calcular pases (default: 24)'
        )
        
        parser.add_argument(
            '--min-elevation',
            type=float,
            default=10.0,
            help='Elevación mínima en grados para considerar un pase visible (default: 10.0)'
        )
        
        # Opciones de salida
        parser.add_argument(
            '--output',
            choices=['table', 'json', 'detailed'],
            default='detailed',
            help='Formato de salida (default: detailed)'
        )
        
        parser.add_argument(
            '--no-security',
            action='store_true',
            help='Omitir análisis de seguridad SPARTA'
        )
        
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Salida detallada (logging)'
        )
        
        return parser
    
    def parse_location(self, location_str: str) -> tuple:
        """Parsea string de ubicación en formato 'lat,lon'."""
        try:
            lat, lon = map(float, location_str.split(','))
            return lat, lon
        except (ValueError, IndexError):
            raise ValueError(f"Formato de ubicación inválido: {location_str}. Use 'lat,lon'")
    
    def print_header(self, title: str):
        """Imprime encabezado con formato."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
        print(f"{title:^60}")
        print(f"{'=' * 60}{Style.RESET_ALL}\n")
    
    def print_satellite_basic_info(self, satellite_data: dict, output_format: str):
        """Imprime información básica del satélite."""
        spacetrack_info = satellite_data.get('spacetrack_info', {})
        tle = satellite_data.get('tle')
        
        if output_format == 'json':
            import json
            print(json.dumps(satellite_data, indent=2, default=str))
            return
        
        self.print_header("INFORMACIÓN BÁSICA DEL SATÉLITE")
        
        if spacetrack_info:
            info_data = [
                ["NORAD ID", spacetrack_info.get('NORAD_CAT_ID', 'N/A')],
                ["Nombre", spacetrack_info.get('OBJECT_NAME', 'N/A')],
                ["País", spacetrack_info.get('COUNTRY', 'N/A')],
                ["Fecha Lanzamiento", spacetrack_info.get('LAUNCH_DATE', 'N/A')],
                ["Sitio Lanzamiento", spacetrack_info.get('LAUNCH_SITE', 'N/A')],
                ["Tipo de Objeto", spacetrack_info.get('OBJECT_TYPE', 'N/A')],
                ["Estado", spacetrack_info.get('OPS_STATUS_CODE', 'N/A')],
                ["Período Orbital (min)", spacetrack_info.get('PERIOD', 'N/A')]
            ]
            
            if output_format == 'table':
                print(tabulate(info_data, headers=["Parámetro", "Valor"], tablefmt="grid"))
            else:
                for param, value in info_data:
                    print(f"{Fore.YELLOW}{param:.<20}{Style.RESET_ALL} {value}")
        
        if tle:
            self.print_header("ELEMENTOS ORBITALES (TLE)")
            try:
                name, line1, line2 = parse_tle(tle)
                orbital_calc = OrbitalCalculator(line1, line2)
                elements = orbital_calc.get_orbital_elements()
                
                orbital_data = [
                    ["Inclinación", f"{elements.get('inclination_deg', 'N/A'):.2f}°"],
                    ["Excentricidad", f"{elements.get('eccentricity', 'N/A'):.6f}"],
                    ["Argumento Perigeo", f"{elements.get('argument_of_perigee_deg', 'N/A'):.2f}°"],
                    ["RAAN", f"{elements.get('raan_deg', 'N/A'):.2f}°"],
                    ["Movimiento Medio", f"{elements.get('mean_motion_rev_per_day', 'N/A'):.6f} rev/día"],
                    ["Coeficiente BSTAR", f"{elements.get('bstar_drag', 'N/A'):.2e}"]
                ]
                
                if output_format == 'table':
                    print(tabulate(orbital_data, headers=["Elemento", "Valor"], tablefmt="grid"))
                else:
                    for element, value in orbital_data:
                        print(f"{Fore.GREEN}{element:.<20}{Style.RESET_ALL} {value}")
                
            except Exception as e:
                print(f"{Fore.RED}Error al procesar TLE: {e}{Style.RESET_ALL}")
    
    def print_current_position(self, satellite_data: dict):
        """Imprime posición actual del satélite."""
        tle = satellite_data.get('tle')
        if not tle:
            print(f"{Fore.RED}No hay datos TLE disponibles para calcular posición{Style.RESET_ALL}")
            return
        
        try:
            name, line1, line2 = parse_tle(tle)
            orbital_calc = OrbitalCalculator(line1, line2)
            
            current_time = datetime.utcnow()
            position = orbital_calc.get_position_at_time(current_time)
            
            if position:
                self.print_header("POSICIÓN ACTUAL")
                print(f"{Fore.YELLOW}Tiempo UTC:{Style.RESET_ALL} {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{Fore.YELLOW}Latitud:{Style.RESET_ALL} {position['latitude']:.4f}°")
                print(f"{Fore.YELLOW}Longitud:{Style.RESET_ALL} {position['longitude']:.4f}°")
                print(f"{Fore.YELLOW}Altitud:{Style.RESET_ALL} {position['altitude_km']:.2f} km")
                print(f"{Fore.YELLOW}Velocidad:{Style.RESET_ALL} {position['velocity_km_s']:.2f} km/s")
            
        except Exception as e:
            print(f"{Fore.RED}Error al calcular posición: {e}{Style.RESET_ALL}")
    
    def print_passes(self, satellite_data: dict, observer_lat: float, 
                    observer_lon: float, hours: int, min_elevation: float):
        """Imprime información de pases futuros."""
        tle = satellite_data.get('tle')
        if not tle:
            print(f"{Fore.RED}No hay datos TLE disponibles para calcular pases{Style.RESET_ALL}")
            return
        
        try:
            name, line1, line2 = parse_tle(tle)
            orbital_calc = OrbitalCalculator(line1, line2)
            
            self.print_header(f"PASES FUTUROS ({hours}h desde ubicación {observer_lat:.2f}, {observer_lon:.2f})")
            print(f"Elevación mínima: {min_elevation}°\n")
            
            passes = orbital_calc.calculate_passes(
                observer_lat, observer_lon, 0.0, hours, min_elevation
            )
            
            if not passes:
                print(f"{Fore.YELLOW}No se encontraron pases visibles en las próximas {hours} horas{Style.RESET_ALL}")
                return
            
            passes_data = []
            for i, pass_info in enumerate(passes, 1):
                start_time = pass_info['start_time'].strftime('%Y-%m-%d %H:%M')
                duration = pass_info['duration_minutes']
                max_elevation = pass_info['max_elevation']
                max_azimuth = pass_info['max_elevation_azimuth']
                
                passes_data.append([
                    i,
                    start_time,
                    f"{duration:.1f} min",
                    f"{max_elevation:.1f}°",
                    f"{max_azimuth:.1f}°"
                ])
            
            print(tabulate(
                passes_data,
                headers=["#", "Inicio (UTC)", "Duración", "Elev. Máx", "Azimut Máx"],
                tablefmt="grid"
            ))
            
        except Exception as e:
            print(f"{Fore.RED}Error al calcular pases: {e}{Style.RESET_ALL}")
    
    def print_security_analysis(self, satellite_data: dict):
        """Imprime análisis de seguridad SPARTA."""
        try:
            analysis = self.sparta_analyzer.analyze_satellite(satellite_data)
            report = self.sparta_analyzer.generate_sparta_report(analysis)
            print(f"\n{Fore.RED}{report}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}Error en análisis de seguridad: {e}{Style.RESET_ALL}")
    
    def print_search_results(self, search_results: list, search_term: str):
        """Imprime resultados de búsqueda."""
        self.print_header(f"RESULTADOS DE BÚSQUEDA: '{search_term}'")
        
        if not search_results:
            print(f"{Fore.YELLOW}No se encontraron satélites con el término '{search_term}'{Style.RESET_ALL}")
            return
        
        results_data = []
        for sat in search_results[:20]:  # Limitar a 20 resultados
            results_data.append([
                sat.get('NORAD_CAT_ID', 'N/A'),
                sat.get('OBJECT_NAME', 'N/A')[:40],  # Truncar nombres largos
                sat.get('COUNTRY', 'N/A'),
                sat.get('LAUNCH_DATE', 'N/A')
            ])
        
        print(tabulate(
            results_data,
            headers=["NORAD ID", "Nombre", "País", "Lanzamiento"],
            tablefmt="grid"
        ))
        
        if len(search_results) > 20:
            print(f"\n{Fore.YELLOW}Mostrando 20 de {len(search_results)} resultados{Style.RESET_ALL}")
    
    def run(self, args):
        """Ejecuta la aplicación principal."""
        try:
            # Configurar logging
            if args.verbose:
                logging.basicConfig(level=logging.INFO)
            
            # Parsear ubicación
            observer_lat, observer_lon = self.parse_location(args.location)
            
            # Caso especial: búsqueda
            if args.search:
                search_results = self.data_retriever.search_satellite_by_name(args.search)
                self.print_search_results(search_results, args.search)
                return
            
            # Recuperar datos del satélite
            print(f"{Fore.CYAN}Recuperando datos satelitales...{Style.RESET_ALL}")
            
            satellite_data = self.data_retriever.get_comprehensive_satellite_data(
                satellite_id=args.id,
                satellite_name=args.name
            )
            
            if not satellite_data['tle'] and not satellite_data['spacetrack_info']:
                print(f"{Fore.RED}No se pudieron recuperar datos para el satélite especificado{Style.RESET_ALL}")
                return
            
            # Mostrar información básica
            self.print_satellite_basic_info(satellite_data, args.output)
            
            # Mostrar posición actual
            if satellite_data['tle']:
                self.print_current_position(satellite_data)
            
            # Calcular y mostrar pases si se solicita
            if args.passes and satellite_data['tle']:
                self.print_passes(
                    satellite_data, observer_lat, observer_lon, 
                    args.hours, args.min_elevation
                )
            
            # Análisis de seguridad SPARTA
            if not args.no_security:
                self.print_security_analysis(satellite_data)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operación cancelada por el usuario{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            if args.verbose:
                import traceback
                traceback.print_exc()
