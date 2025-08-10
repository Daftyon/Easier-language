#!/usr/bin/env python3
"""
El Programming Language - Standalone Executable
Complete version for distribution
"""

import sys
import os
import argparse
from pathlib import Path

# Add current directory to path for imports
if getattr(sys, 'frozen', False):
    # If we are in a PyInstaller executable
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)

# Import compiler components
try:
    from compiler.main import El
    from compiler.lexer import Lexer
    from compiler.parser import Parser
    from utils.constants import EOF
    from utils.errors import *
except ImportError as e:
    print(f"Error: Unable to import El components: {e}")
    sys.exit(1)

__version__ = "1.0.7"
__author__ = "El Language Team"

class ElREPL:
    """Interactive interface for El Language"""
    
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
        """Start the interactive REPL"""
        self.show_welcome()
        
        while True:
            try:
                code = input("el> ").strip()
                
                if not code:
                    continue
                    
                # Special commands
                if code in self.commands:
                    self.commands[code]()
                    continue
                
                # Save to history
                self.history.append(code)
                
                # Execute El code
                try:
                    # Wrap code in a program if necessary
                    if not code.startswith('ALGORITHM'):
                        code = f"ALGORITHM repl {{ {code} }}"
                    
                    El.compile(code)
                except Exception as e:
                    print(f"El Error: {e}")
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
                continue
            except EOFError:
                print("\nGoodbye!")
                break
                
    def show_welcome(self):
        """Display welcome message"""
        # Show ASCII banner
        show_banner()
        
        print(f"""
Type 'help' for help, 'exit' to quit
Created by {__author__}
""")
    
    def show_help(self):
        """Display help"""
        help_text = """
El REPL Commands:
  help      - Show this help
  version   - Show version
  clear     - Clear screen
  history   - Show command history
  exit/quit - Exit REPL

El Language Syntax:
  Variables:  var x: integer = 5;
  Functions:  function add(a: integer, b: integer): integer { return a + b; }
  Display:    show "Hello, World!";
  Loops:      for i: integer = 0; i < 10; i = i + 1 { show i; }
  
Complete documentation: https://github.com/Daftyon/Easier-language
"""
        print(help_text)
    
    def show_version(self):
        """Display version"""
        print(f"El Programming Language v{__version__}")
        print(f"Created by {__author__}")
    
    def clear_screen(self):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_history(self):
        """Display history"""
        if not self.history:
            print("No history available")
            return
        
        print("Command history:")
        for i, cmd in enumerate(self.history[-10:], 1):
            print(f"  {i}: {cmd}")
    
    def exit_repl(self):
        """Exit REPL"""
        print("Goodbye!")
        sys.exit(0)

def show_banner():
    """Display El banner"""
    banner = f"""
    ███████╗██╗         ██╗      █████╗ ███╗   ██╗ ██████╗ 
    ██╔════╝██║         ██║     ██╔══██╗████╗  ██║██╔════╝ 
    █████╗  ██║         ██║     ███████║██╔██╗ ██║██║  ███╗
    ██╔══╝  ██║         ██║     ██╔══██║██║╚██╗██║██║   ██║
    ███████╗███████╗    ███████╗██║  ██║██║ ╚████║╚██████╔╝
    ╚══════╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    
                    Version {__version__}
          A modern and easy programming language
    """
    print(banner)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='El Programming Language - A modern and easy language',
        prog='el',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  el                          Start interactive mode
  el hello.el                 Execute an El file
  el -c "show 'Hello';"       Execute code directly
  el --version                Show version
  
Documentation: https://github.com/Daftyon/Easier-language
        """
    )
    
    parser.add_argument(
        'file', 
        nargs='?', 
        help='El source file (.el)'
    )
    
    parser.add_argument(
        '-v', '--version', 
        action='version', 
        version=f'El Language v{__version__}'
    )
    
    parser.add_argument(
        '-i', '--interactive', 
        action='store_true',
        help='Start interactive mode (REPL)'
    )
    
    parser.add_argument(
        '-c', '--code', 
        help='Execute El code from command line'
    )
    
    parser.add_argument(
        '--banner', 
        action='store_true',
        help='Display El banner'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Debug mode with detailed information'
    )
    
    args = parser.parse_args()
    
    try:
        if args.banner:
            show_banner()
            return
            
        if args.interactive or (not args.file and not args.code):
            # Interactive mode by default
            repl = ElREPL()
            repl.start()
            
        elif args.code:
            # Execute code from command line
            if args.debug:
                print(f"Executing code: {args.code}")
            El.compile(args.code)
                
        elif args.file:
            # Execute a file
            file_path = Path(args.file)
            
            # Add .el extension if necessary
            if not file_path.suffix:
                file_path = file_path.with_suffix('.el')
            
            if not file_path.exists():
                print(f"Error: File '{file_path}' not found")
                sys.exit(1)
            
            try:
                if args.debug:
                    print(f"Executing file: {file_path}")
                
                # Read and compile the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                El.compile(code)
                    
            except IOError as e:
                print(f"File read error: {e}")
                sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
