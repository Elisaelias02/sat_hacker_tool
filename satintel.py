#!/usr/bin/env python3
"""
SatIntel - Satellite Intelligence Tool
Herramienta profesional de inteligencia satelital

Autor: Desarrollador Experto en Python
Versión: 1.0
"""

import sys
import logging
from modules.cli import SatIntelCLI

def main():
    """Función principal."""
    try:
        # Crear y configurar la interfaz CLI
        cli = SatIntelCLI()
        parser = cli.create_parser()
        
        # Parsear argumentos
        args = parser.parse_args()
        
        # Ejecutar aplicación
        cli.run(args)
        
    except Exception as e:
        print(f"Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
