#!/usr/bin/env python3
"""
El Programming Language - Standalone Executable
Version complète pour distribution
"""

import sys
import os
import argparse
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
if getattr(sys, 'frozen', False):
    # Si nous sommes dans un exécutable PyInstaller
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)

# Import des composants du compilateur
try:
    from compiler.main import El
    from compiler.lexer import Lexer
    from compiler.parser import Parser
    from utils.constants import EOF
    from utils.errors import *
except ImportError as e:
    print(f"Erreur: Impossible d'importer les composants El: {e}")
    sys.exit(1)

__version__ = "1.0.1"
__author__ = "El Language Team"

class ElREPL:
    """Interface interactive pour El Language"""
    
    def __init__(self):
        self.history = []
        self.commands = {
            'help': self.show_help,
            'exit': self.exit_repl,
            'quit': self.exit_repl,
            'version': self.show_version,
            'clear': self.clear_screen,
            'history': self.show_history,
        }
        
    def start(self):
        """Démarrer le REPL interactif"""
        self.show_welcome()
        
        while True:
            try:
                code = input("el> ").strip()
                
                if not code:
                    continue
                    
                # Commandes spéciales
                if code in self.commands:
                    self.commands[code]()
                    continue
                
                # Sauvegarder dans l'historique
                self.history.append(code)
                
                # Exécuter le code El
                try:
                    # Envelopper le code dans un programme si nécessaire
                    if not code.startswith('program'):
                        code = f"program repl {{ {code} }}"
                    
                    El.compile(code)
                except Exception as e:
                    print(f"Erreur El: {e}")
                    
            except KeyboardInterrupt:
                print("\nUtilisez 'exit' pour quitter")
                continue
            except EOFError:
                print("\nAu revoir!")
                break
                
    def show_welcome(self):
        """Afficher le message de bienvenue"""
        print(f"""
╔══════════════════════════════════════╗
║     El Programming Language v{__version__}   ║
╚══════════════════════════════════════╝

Tapez 'help' pour l'aide, 'exit' pour quitter
Créé par {__author__}
""")
    
    def show_help(self):
        """Afficher l'aide"""
        help_text = """
Commandes El REPL:
  help      - Afficher cette aide
  version   - Afficher la version
  clear     - Effacer l'écran
  history   - Afficher l'historique des commandes
  exit/quit - Quitter le REPL

Syntaxe El Language:
  Variables:  var x: integer = 5;
  Fonctions:  function add(a: integer, b: integer): integer { return a + b; }
  Affichage:  show "Hello, World!";
  Boucles:    for i: integer = 0; i < 10; i = i + 1 { show i; }
  
Documentation complète:https://github.com/Daftyon/Easier-language
"""
        print(help_text)
    
    def show_version(self):
        """Afficher la version"""
        print(f"El Programming Language v{__version__}")
        print(f"Créé par {__author__}")
    
    def clear_screen(self):
        """Effacer l'écran"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_history(self):
        """Afficher l'historique"""
        if not self.history:
            print("Aucun historique disponible")
            return
        
        print("Historique des commandes:")
        for i, cmd in enumerate(self.history[-10:], 1):
            print(f"  {i}: {cmd}")
    
    def exit_repl(self):
        """Quitter le REPL"""
        print("Au revoir!")
        sys.exit(0)

def show_banner():
    """Afficher la bannière El"""
    banner = f"""
    ███████╗██╗         ██╗      █████╗ ███╗   ██╗ ██████╗ 
    ██╔════╝██║         ██║     ██╔══██╗████╗  ██║██╔════╝ 
    █████╗  ██║         ██║     ███████║██╔██╗ ██║██║  ███╗
    ██╔══╝  ██║         ██║     ██╔══██║██║╚██╗██║██║   ██║
    ███████╗███████╗    ███████╗██║  ██║██║ ╚████║╚██████╔╝
    ╚══════╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    
                    Version {__version__}
          Un langage de programmation moderne et facile
    """
    print(banner)

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description='El Programming Language - Un langage moderne et facile',
        prog='el',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  el                          Démarrer le mode interactif
  el hello.el                 Exécuter un fichier El
  el -c "show 'Hello';"       Exécuter du code directement
  el --version                Afficher la version
  
Documentation:https://github.com/Daftyon/Easier-language
        """
    )
    
    parser.add_argument(
        'file', 
        nargs='?', 
        help='Fichier source El (.el)'
    )
    
    parser.add_argument(
        '-v', '--version', 
        action='version', 
        version=f'El Language v{__version__}'
    )
    
    parser.add_argument(
        '-i', '--interactive', 
        action='store_true',
        help='Démarrer le mode interactif (REPL)'
    )
    
    parser.add_argument(
        '-c', '--code', 
        help='Exécuter du code El depuis la ligne de commande'
    )
    
    parser.add_argument(
        '--banner', 
        action='store_true',
        help='Afficher la bannière El'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Mode debug avec informations détaillées'
    )
    
    args = parser.parse_args()
    
    try:
        if args.banner:
            show_banner()
            return
            
        if args.interactive or (not args.file and not args.code):
            # Mode interactif par défaut
            repl = ElREPL()
            repl.start()
            
        elif args.code:
            # Exécuter du code depuis la ligne de commande
            if args.debug:
                print(f"Exécution du code: {args.code}")
            El.compile(args.code)
                
        elif args.file:
            # Exécuter un fichier
            file_path = Path(args.file)
            
            # Ajouter l'extension .el si nécessaire
            if not file_path.suffix:
                file_path = file_path.with_suffix('.el')
            
            if not file_path.exists():
                print(f"Erreur: Fichier '{file_path}' non trouvé")
                sys.exit(1)
            
            try:
                if args.debug:
                    print(f"Exécution du fichier: {file_path}")
                
                # Lire et compiler le fichier
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                El.compile(code)
                    
            except IOError as e:
                print(f"Erreur de lecture du fichier: {e}")
                sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"Erreur: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
