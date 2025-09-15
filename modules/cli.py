import argparse
import logging
import sys
from typing import Dict, List, Tuple
from datetime import datetime
from tabulate import tabulate
from colorama import init, Fore, Style

from modules.data_sources import SatelliteDataManager
from modules.orbital import OrbitalCalculator
from modules.security import SatelliteRiskAnalyzer
from modules.utils import parse_tle
from config.settings import DEFAULT_LATITUDE, DEFAULT_LONGITUDE

init(autoreset=True)
logger = logging.getLogger(__name__)

class SatIntelCLI:
    """Interfaz CLI principal - versión corregida."""
    
    def __init__(self):
        self.data_manager = SatelliteDataManager()
        self.risk_analyzer = SatelliteRiskAnalyzer()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Crea parser de argumentos."""
        parser = argparse.ArgumentParser(
            description="SatIntel - Herramienta de Inteligencia Satelital",
            epilog="""
Ejemplos:
  python satintel.py --id 25544
  python satintel.py --name "ISS"
  python satintel.py --id 25544 --passes --location "20.67,-103.35"
  python satintel.py --search "starlink"
            """
        )
        
        # Identificación del satélite
        id_group = parser.add_mutually_exclusive_group(required=True)
        id_group.add_argument('--id', type=int, help='NORAD ID del satélite')
        id_group.add_argument('--name', type=str, help='Nombre del satélite')
        id_group.add_argument('--search', type=str, help='Buscar satélites por nombre')
        
        # Opciones de análisis
        parser.add_argument('--location', type=str, 
                            default=f"{DEFAULT_LATITUDE},{DEFAULT_LONGITUDE}",
                            help='Ubicación observador "lat,lon"')
        parser.add_argument('--passes', action='store_true', 
                            help='Calcular pases futuros')
        parser.add_argument('--hours', type=int, default=24,
                            help='Horas para calcular pases')
        
        # Opciones de salida
        parser.add_argument('--output', choices=['table', 'json', 'detailed'],
                            default='detailed', help='Formato de salida')
        parser.add_argument('--no-security', action='store_true',
                            help='Omitir análisis SPARTA')
        parser.add_argument('--verbose', '-v', action='store_true',
                            help='Salida detallada')
        
        return parser
    
    def run(self, args):
        """Ejecuta la aplicación principal."""
        try:
            if args.verbose:
                logging.basicConfig(level=logging.INFO)
            
            # Caso búsqueda
            if args.search:
                self._handle_search(args.search)
                return
            
            # Obtener datos del satélite
            print(f"{Fore.CYAN} Recuperando datos satelitales...{Style.RESET_ALL}")
            
            satellite_data = self.data_manager.get_satellite_data(
                satellite_id=args.id,
                satellite_name=args.name
            )
            
            if not satellite_data.get('sources_used'):
                print(f"{Fore.RED} No se encontraron datos para el satélite{Style.RESET_ALL}")
                return
            
            # Mostrar información
            self._display_satellite_info(satellite_data, args.output)
            
            # Mostrar posición actual
            if satellite_data.get('tle'):
                self._display_current_position(satellite_data)
            
            # Calcular pases si se solicita
            if args.passes and satellite_data.get('tle'):
                observer_lat, observer_lon = self._parse_location(args.location)
                self._display_passes(satellite_data, observer_lat, observer_lon, args.hours)
            
            # Análisis de seguridad
            if not args.no_security:
                self._display_security_analysis(satellite_data)
            
            # Resumen final
            sources_count = len(satellite_data.get('sources_used', []))
            print(f"\n{Fore.GREEN} Consulta completada usando {sources_count} fuentes{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operación cancelada{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED} Error: {e}{Style.RESET_ALL}")
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    def _handle_search(self, search_term: str):
        """Maneja búsqueda de satélites - VERSIÓN MEJORADA."""
        print(f"{Fore.CYAN} Buscando satélites: '{search_term}'...{Style.RESET_ALL}")
        
        results = self.data_manager.search_satellites(search_term)
        
        if not results:
            print(f"{Fore.YELLOW} No se encontraron satélites con el término '{search_term}'{Style.RESET_ALL}")
            print(f"{Fore.CYAN} Sugerencias:{Style.RESET_ALL}")
            print(f"  • Intenta términos más cortos: 'star' en lugar de 'starlink'")
            print(f"  • Usa nombres comunes: 'ISS', 'NOAA', 'GPS'")
            print(f"  • Busca por operador: 'SpaceX', 'NASA', 'USAF'")
            return
        
        # Agrupar resultados por fuente
        results_by_source = {}
        for result in results:
            source = result.get('source', 'Unknown')
            if source not in results_by_source:
                results_by_source[source] = []
            results_by_source[source].append(result)
        
        print(f"\n{Fore.GREEN} Encontrados {len(results)} satélites en {len(results_by_source)} fuentes:{Style.RESET_ALL}\n")
        
        # Mostrar resultados por fuente
        for source, source_results in results_by_source.items():
            print(f"{Fore.CYAN} Resultados desde {source} ({len(source_results)}):{Style.RESET_ALL}")
            
            table_data = []
            for i, sat in enumerate(source_results[:10], 1):  # Máximo 10 por fuente
                table_data.append([
                    i,
                    sat.get('norad_id', 'N/A'),
                    sat.get('name', 'N/A')[:45],  # Truncar nombres largos
                    sat.get('operator', 'N/A')[:20],
                    sat.get('status', 'N/A')[:15]
                ])
            
            print(tabulate(
                table_data,
                headers=["#", "NORAD ID", "Nombre", "Operador", "Estado"],
                tablefmt="grid"
            ))
            
            if len(source_results) > 10:
                print(f"{Fore.YELLOW}... y {len(source_results) - 10} resultados más de {source}{Style.RESET_ALL}")
            
            print()  # Línea en blanco entre fuentes
        
        # Mostrar estadísticas finales
        print(f"{Fore.GREEN} Búsqueda completada. Total único: {len(results)} satélites{Style.RESET_ALL}")
        
        # Sugerir comandos de seguimiento
        if results:
            first_result = results[0]
            norad_id = first_result.get('norad_id')
            if norad_id:
                print(f"\n{Fore.CYAN} Para más detalles del primer resultado:{Style.RESET_ALL}")
                print(f"    python satintel.py --id {norad_id}")
    
    def _display_security_analysis(self, satellite_data: Dict):
    """Muestra evaluación de riesgos."""
    try:
        analysis = self.risk_analyzer.analyze_satellite(satellite_data)
        report = self.risk_analyzer.generate_assessment_report(analysis)
        print(f"\n{Fore.RED}{report}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error en evaluación de riesgos: {e}{Style.RESET_ALL}")
            return
        
        basic_info = satellite_data.get('basic_info', {})
        mission_info = satellite_data.get('mission_info', {})
        technical_info = satellite_data.get('technical_info', {})
        orbital_info = satellite_data.get('orbital_info', {})
        sources = ', '.join(satellite_data.get('sources_used', []))
        
        # Información básica
        self._print_header("INFORMACIÓN BÁSICA DEL SATÉLITE")
        print(f"{Fore.CYAN}Fuentes: {sources}{Style.RESET_ALL}\n")
        
        basic_data = [
            ["NORAD ID", basic_info.get('norad_id', 'N/A')],
            ["Nombre", basic_info.get('name', 'N/A')],
            ["Operador", basic_info.get('operator', 'N/A')],
            ["País", basic_info.get('countries', basic_info.get('inferred_country', 'N/A'))],
            ["Estado", basic_info.get('status', 'N/A')],
            ["Lanzamiento", basic_info.get('launched', basic_info.get('launch_date', 'N/A'))],
            ["Sitio Web", basic_info.get('website', 'N/A')]
        ]
        
        self._print_table(basic_data, output_format)
        
        # Información de misión
        if mission_info:
            self._print_header("INFORMACIÓN DE MISIÓN")
            
            mission_data = []
            if mission_info.get('description'):
                mission_data.append(["Descripción", mission_info['description'][:100] + "..."])
            if mission_info.get('type'):
                mission_data.append(["Tipo", mission_info['type']])
            if mission_info.get('orbit'):
                mission_data.append(["Órbita", mission_info['orbit']])
            if mission_info.get('inferred_purpose'):
                mission_data.append(["Propósito", mission_info['inferred_purpose']])
            
            if mission_data:
                self._print_table(mission_data, output_format)
        
        # Información técnica
        if technical_info:
            self._print_header("ESPECIFICACIONES TÉCNICAS")
            
            tech_data = []
            for key, value in technical_info.items():
                if value:
                    display_key = key.replace('_', ' ').title()
                    if isinstance(value, list):
                        value = ', '.join(str(v) for v in value)
                    tech_data.append([display_key, str(value)])
            
            if tech_data:
                self._print_table(tech_data, output_format)
        
        # Elementos orbitales
        if orbital_info:
            self._print_header("ELEMENTOS ORBITALES")
            
            orbital_data = [
                ["Inclinación", f"{orbital_info.get('inclination', 0):.2f}°"],
                ["Excentricidad", f"{orbital_info.get('eccentricity', 0):.6f}"],
                ["Movimiento Medio", f"{orbital_info.get('mean_motion', 0):.6f} rev/día"],
                ["RAAN", f"{orbital_info.get('raan', 0):.2f}°"],
                ["Arg. Perigeo", f"{orbital_info.get('arg_perigee', 0):.2f}°"]
            ]
            
            self._print_table(orbital_data, output_format)
    
    def _display_current_position(self, satellite_data: Dict):
        """Muestra posición actual del satélite."""
        try:
            tle = satellite_data.get('tle')
            if not tle:
                return
            
            name, line1, line2 = parse_tle(tle)
            calc = OrbitalCalculator(line1, line2)
            position = calc.get_current_position()
            
            if position:
                self._print_header("POSICIÓN ACTUAL")
                current_time = datetime.utcnow()
                
                position_data = [
                    ["Tiempo UTC", current_time.strftime('%Y-%m-%d %H:%M:%S')],
                    ["Latitud", f"{position['latitude']:.4f}°"],
                    ["Longitud", f"{position['longitude']:.4f}°"],
                    ["Altitud", f"{position['altitude_km']:.2f} km"],
                    ["Velocidad", f"{position['velocity_km_s']:.2f} km/s"]
                ]
                
                self._print_table(position_data, 'detailed')
                
        except Exception as e:
            print(f"{Fore.RED}Error calculando posición: {e}{Style.RESET_ALL}")
    
    def _display_passes(self, satellite_data: Dict, observer_lat: float, 
                        observer_lon: float, hours: int):
        """Muestra pases futuros."""
        try:
            tle = satellite_data.get('tle')
            name, line1, line2 = parse_tle(tle)
            calc = OrbitalCalculator(line1, line2)
            
            self._print_header(f"PASES FUTUROS ({hours}h)")
            print(f"Ubicación: {observer_lat:.2f}°, {observer_lon:.2f}°\n")
            
            passes = calc.calculate_passes(observer_lat, observer_lon, hours)
            
            if not passes:
                print(f"{Fore.YELLOW}No hay pases visibles{Style.RESET_ALL}")
                return
            
            passes_data = []
            for i, pass_info in enumerate(passes, 1):
                start_time = pass_info['start_time'].strftime('%m-%d %H:%M')
                duration = f"{pass_info['duration_minutes']:.1f} min"
                max_elev = f"{pass_info['max_elevation']:.1f}°"
                
                passes_data.append([i, start_time, duration, max_elev])
            
            print(tabulate(
                passes_data,
                headers=["#", "Inicio", "Duración", "Elev. Máx"],
                tablefmt="grid"
            ))
            
        except Exception as e:
            print(f"{Fore.RED}Error calculando pases: {e}{Style.RESET_ALL}")
    
    def _display_security_analysis(self, satellite_data: Dict):
        """Muestra análisis de seguridad."""
        try:
            analysis = self.security_analyzer.analyze_satellite(satellite_data)
            report = self.security_analyzer.generate_report(analysis)
            print(f"\n{Fore.RED}{report}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error en análisis SPARTA: {e}{Style.RESET_ALL}")
    
    def _print_header(self, title: str):
        """Imprime encabezado."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
        print(f"{title:^60}")
        print(f"{'=' * 60}{Style.RESET_ALL}\n")
    
    def _print_table(self, data: List, format_type: str):
        """Imprime tabla de datos."""
        if format_type == 'table':
            print(tabulate(data, headers=["Campo", "Valor"], tablefmt="grid"))
        else:
            for field, value in data:
                if value and str(value) != 'N/A':
                    print(f"{Fore.YELLOW}{field:.<25}{Style.RESET_ALL} {value}")
        print()
    
    def _parse_location(self, location_str: str) -> Tuple[float, float]:
        """Parse ubicación en formato 'lat,lon'."""
        try:
            lat, lon = map(float, location_str.split(','))
            return lat, lon
        except:
            raise ValueError(f"Formato de ubicación inválido: {location_str}")
