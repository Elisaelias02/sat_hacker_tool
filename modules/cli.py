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
