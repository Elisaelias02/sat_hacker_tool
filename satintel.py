#!/usr/bin/env python3
"""
Sat hacker Tool - Satellite Intelligence Tool
Herramienta de inteligencia satelital

Versión: 2.0 - Cinn4mor0ll
"""

import sys
from modules.cli import SatIntelCLI

def main():
    """Función principal."""
    try:
        cli = SatIntelCLI()
        parser = cli.create_parser()
        args = parser.parse_args()
        cli.run(args)
    except Exception as e:
        print(f"Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
