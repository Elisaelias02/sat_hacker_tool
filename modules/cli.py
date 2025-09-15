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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SatIntelCLI:
    """Main CLI Interface - corrected version."""
    
    def __init__(self):
        self.data_manager = SatelliteDataManager()
        self.risk_analyzer = SatelliteRiskAnalyzer()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Creates the argument parser."""
        parser = argparse.ArgumentParser(
            description="SatIntel - Satellite Intelligence Tool",
            epilog="""
Examples:
  python satintel.py --id 25544
  python satintel.py --name "ISS"
  python satintel.py --id 25544 --passes --location "20.67,-103.35"
  python satintel.py --search "starlink"
            """
        )
        
        # Satellite identification
        id_group = parser.add_mutually_exclusive_group(required=True)
        id_group.add_argument('--id', type=int, help='NORAD ID of the satellite')
        id_group.add_argument('--name', type=str, help='Name of the satellite')
        id_group.add_argument('--search', type=str, help='Search satellites by name')
        
        # Analysis options
        parser.add_argument('--location', type=str, 
                            default=f"{DEFAULT_LATITUDE},{DEFAULT_LONGITUDE}",
                            help='Observer location "lat,lon"')
        parser.add_argument('--passes', action='store_true', 
                            help='Calculate future passes')
        parser.add_argument('--hours', type=int, default=24,
                            help='Hours to calculate passes for')
        
        # Output options
        parser.add_argument('--output', choices=['table', 'json', 'detailed'],
                            default='detailed', help='Output format')
        parser.add_argument('--no-security', action='store_true',
                            help='Omit SPARTA analysis')
        parser.add_argument('--verbose', '-v', action='store_true',
                            help='Detailed output')
        
        return parser
    
    def run(self, args):
        """Runs the main application."""
        try:
            if args.verbose:
                logging.basicConfig(level=logging.INFO)
            
            # Search case
            if args.search:
                self._handle_search(args.search)
                return
            
            # Get satellite data
            print(f"{Fore.CYAN} Retrieving satellite data...{Style.RESET_ALL}")
            
            satellite_data = self.data_manager.get_satellite_data(
                satellite_id=args.id,
                satellite_name=args.name
            )
            
            if not satellite_data.get('sources_used'):
                print(f"{Fore.RED} No data found for the satellite{Style.RESET_ALL}")
                return
            
            # Display information
            self._display_satellite_info(satellite_data, args.output)
            
            # Display current position
            if satellite_data.get('tle'):
                self._display_current_position(satellite_data)
            
            # Calculate passes if requested
            if args.passes and satellite_data.get('tle'):
                observer_lat, observer_lon = self._parse_location(args.location)
                self._display_passes(satellite_data, observer_lat, observer_lon, args.hours)
            
            # Security analysis
            if not args.no_security:
                self._display_security_analysis(satellite_data)
            
            # Final summary
            sources_count = len(satellite_data.get('sources_used', []))
            print(f"\n{Fore.GREEN} Query completed using {sources_count} sources{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operation canceled{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED} Error: {e}{Style.RESET_ALL}")
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    def _handle_search(self, search_term: str):
        """Handles satellite search - IMPROVED VERSION."""
        print(f"{Fore.CYAN} Searching for satellites: '{search_term}'...{Style.RESET_ALL}")
        
        results = self.data_manager.search_satellites(search_term)
        
        if not results:
            print(f"{Fore.YELLOW} No satellites found with the term '{search_term}'{Style.RESET_ALL}")
            print(f"{Fore.CYAN} Suggestions:{Style.RESET_ALL}")
            print(f"  • Try shorter terms: 'star' instead of 'starlink'")
            print(f"  • Use common names: 'ISS', 'NOAA', 'GPS'")
            print(f"  • Search by operator: 'SpaceX', 'NASA', 'USAF'")
            return
        
        # Group results by source
        results_by_source = {}
        for result in results:
            source = result.get('source', 'Unknown')
            if source not in results_by_source:
                results_by_source[source] = []
            results_by_source[source].append(result)
        
        print(f"\n{Fore.GREEN} Found {len(results)} satellites from {len(results_by_source)} sources:{Style.RESET_ALL}\n")
        
        # Display results by source
        for source, source_results in results_by_source.items():
            print(f"{Fore.CYAN} Results from {source} ({len(source_results)}):{Style.RESET_ALL}")
            
            table_data = []
            for i, sat in enumerate(source_results[:10], 1):  # Max 10 per source
                table_data.append([
                    i,
                    sat.get('norad_id', 'N/A'),
                    sat.get('name', 'N/A')[:45],  # Truncate long names
                    sat.get('operator', 'N/A')[:20],
                    sat.get('status', 'N/A')[:15]
                ])
            
            print(tabulate(
                table_data,
                headers=["#", "NORAD ID", "Name", "Operator", "Status"],
                tablefmt="grid"
            ))
            
            if len(source_results) > 10:
                print(f"{Fore.YELLOW}... and {len(source_results) - 10} more results from {source}{Style.RESET_ALL}")
            
            print()  # Blank line between sources
        
        # Display final statistics
        print(f"{Fore.GREEN} Search completed. Total unique: {len(results)} satellites{Style.RESET_ALL}")
        
        # Suggest follow-up commands
        if results:
            first_result = results[0]
            norad_id = first_result.get('norad_id')
            if norad_id:
                print(f"\n{Fore.CYAN} For more details on the first result:{Style.RESET_ALL}")
                print(f"    python satintel.py --id {norad_id}")
    
    def _display_satellite_info(self, satellite_data: Dict, output_format: str):
        """Displays satellite information."""
        basic_info = satellite_data.get('basic_info', {})
        mission_info = satellite_data.get('mission_info', {})
        technical_info = satellite_data.get('technical_info', {})
        orbital_info = satellite_data.get('orbital_info', {})
        sources = ', '.join(satellite_data.get('sources_used', []))
        
        # Basic information
        self._print_header("SATELLITE BASIC INFORMATION")
        print(f"{Fore.CYAN}Sources: {sources}{Style.RESET_ALL}\n")
        
        basic_data = [
            ["NORAD ID", basic_info.get('norad_id', 'N/A')],
            ["Name", basic_info.get('name', 'N/A')],
            ["Operator", basic_info.get('operator', 'N/A')],
            ["Country", basic_info.get('countries', basic_info.get('inferred_country', 'N/A'))],
            ["Status", basic_info.get('status', 'N/A')],
            ["Launch", basic_info.get('launched', basic_info.get('launch_date', 'N/A'))],
            ["Website", basic_info.get('website', 'N/A')]
        ]
        
        self._print_table(basic_data, output_format)
        
        # Mission information
        if mission_info:
            self._print_header("MISSION INFORMATION")
            
            mission_data = []
            if mission_info.get('description'):
                mission_data.append(["Description", mission_info['description'][:100] + "..."])
            if mission_info.get('type'):
                mission_data.append(["Type", mission_info['type']])
            if mission_info.get('orbit'):
                mission_data.append(["Orbit", mission_info['orbit']])
            if mission_info.get('inferred_purpose'):
                mission_data.append(["Purpose", mission_info['inferred_purpose']])
            
            if mission_data:
                self._print_table(mission_data, output_format)
        
        # Technical information
        if technical_info:
            self._print_header("TECHNICAL SPECIFICATIONS")
            
            tech_data = []
            for key, value in technical_info.items():
                if value:
                    display_key = key.replace('_', ' ').title()
                    if isinstance(value, list):
                        value = ', '.join(str(v) for v in value)
                    tech_data.append([display_key, str(value)])
            
            if tech_data:
                self._print_table(tech_data, output_format)
        
        # Orbital elements
        if orbital_info:
            self._print_header("ORBITAL ELEMENTS")
            
            orbital_data = [
                ["Inclination", f"{orbital_info.get('inclination', 0):.2f}°"],
                ["Eccentricity", f"{orbital_info.get('eccentricity', 0):.6f}"],
                ["Mean Motion", f"{orbital_info.get('mean_motion', 0):.6f} rev/day"],
                ["RAAN", f"{orbital_info.get('raan', 0):.2f}°"],
                ["Arg. Perigee", f"{orbital_info.get('arg_perigee', 0):.2f}°"]
            ]
            
            self._print_table(orbital_data, output_format)
    
    def _display_current_position(self, satellite_data: Dict):
        """Displays the current position of the satellite."""
        try:
            tle = satellite_data.get('tle')
            if not tle:
                return
            
            name, line1, line2 = parse_tle(tle)
            calc = OrbitalCalculator(line1, line2)
            position = calc.get_current_position()
            
            if position:
                self._print_header("CURRENT POSITION")
                current_time = datetime.utcnow()
                
                position_data = [
                    ["UTC Time", current_time.strftime('%Y-%m-%d %H:%M:%S')],
                    ["Latitude", f"{position['latitude']:.4f}°"],
                    ["Longitude", f"{position['longitude']:.4f}°"],
                    ["Altitude", f"{position['altitude_km']:.2f} km"],
                    ["Velocity", f"{position['velocity_km_s']:.2f} km/s"]
                ]
                
                self._print_table(position_data, 'detailed')
                
        except Exception as e:
            print(f"{Fore.RED}Error calculating position: {e}{Style.RESET_ALL}")
    
    def _display_passes(self, satellite_data: Dict, observer_lat: float, 
                        observer_lon: float, hours: int):
        """Displays future passes."""
        try:
            tle = satellite_data.get('tle')
            name, line1, line2 = parse_tle(tle)
            calc = OrbitalCalculator(line1, line2)
            
            self._print_header(f"FUTURE PASSES ({hours}h)")
            print(f"Location: {observer_lat:.2f}°, {observer_lon:.2f}°\n")
            
            passes = calc.calculate_passes(observer_lat, observer_lon, hours)
            
            if not passes:
                print(f"{Fore.YELLOW}No visible passes{Style.RESET_ALL}")
                return
            
            passes_data = []
            for i, pass_info in enumerate(passes, 1):
                start_time = pass_info['start_time'].strftime('%m-%d %H:%M')
                duration = f"{pass_info['duration_minutes']:.1f} min"
                max_elev = f"{pass_info['max_elevation']:.1f}°"
                
                passes_data.append([i, start_time, duration, max_elev])
            
            print(tabulate(
                passes_data,
                headers=["#", "Start", "Duration", "Max. Elev."],
                tablefmt="grid"
            ))
            
        except Exception as e:
            print(f"{Fore.RED}Error calculating passes: {e}{Style.RESET_ALL}")
    
    def _display_security_analysis(self, satellite_data: Dict):
        """Displays security analysis."""
        try:
            analysis = self.risk_analyzer.analyze_satellite(satellite_data)
            report = self.risk_analyzer.generate_assessment_report(analysis)
            print(f"\n{Fore.RED}{report}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error in SPARTA analysis: {e}{Style.RESET_ALL}")
    
    def _print_header(self, title: str):
        """Prints a header."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
        print(f"{title:^60}")
        print(f"{'=' * 60}{Style.RESET_ALL}\n")
    
    def _print_table(self, data: List, format_type: str):
        """Prints a data table."""
        if format_type == 'table':
            print(tabulate(data, headers=["Field", "Value"], tablefmt="grid"))
        else:
            for field, value in data:
                if value and str(value) != 'N/A':
                    print(f"{Fore.YELLOW}{field:.<25}{Style.RESET_ALL} {value}")
        print()
    
    def _parse_location(self, location_str: str) -> Tuple[float, float]:
        """Parses location in 'lat,lon' format."""
        try:
            lat, lon = map(float, location_str.split(','))
            return lat, lon
        except:
            raise ValueError(f"Invalid location format: {location_str}")
