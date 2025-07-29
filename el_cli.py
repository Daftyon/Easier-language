#!/usr/bin/env python3
"""
El Programming Language - Command Line Interface
Version simple pour commencer
"""

import argparse
import sys
from pathlib import Path

# Import your existing compiler components
try:
    from compiler.main import El
except ImportError as e:
    print(f"Erreur: Impossible d'importer les composants du compilateur El: {e}")
    print("Assurez-vous que tous les modules sont dans le chemin Python")
    sys.exit(1)

__version__ = "1.0.0"

def main():
    """Point d'entrée principal pour El CLI"""
    parser = argparse.ArgumentParser(
        description='El Programming Language',
        prog='el'
    )
    
    parser.add_argument(
        'file', 
        nargs='?', 
        help='El source file (.el)'
    )
    
    parser.add_argument(
        '-v', '--version', 
        action='version', 
        version=f'El {__version__}'
    )
    
    parser.add_argument(
        '-c', '--code', 
        help='Execute El code from command line'
    )
    
    args = parser.parse_args()
    
    try:
        if args.code:
            # Exécuter du code directement
            print(f"Exécution du code: {args.code}")
            El.compile(args.code)
                
        elif args.file:
            # Exécuter un fichier
            file_path = Path(args.file)
            
            # Ajouter l'extension .el si elle n'existe pas
            if not file_path.suffix:
                file_path = file_path.with_suffix('.el')
            
            if not file_path.exists():
                print(f"Erreur: Fichier '{file_path}' non trouvé")
                sys.exit(1)
            
            try:
                print(f"Exécution du fichier: {file_path}")
                # Utiliser votre méthode existante pour compiler des fichiers
                El.compile_file(str(file_path).replace('.el', ''))
                    
            except IOError as e:
                print(f"Erreur de lecture du fichier: {e}")
                sys.exit(1)
        else:
            # Aucun argument, afficher l'aide
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
