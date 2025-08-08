#!/usr/bin/env python3
"""
El Programming Language - Command Line Interface
Simple version to get started
"""

import argparse
import sys
from pathlib import Path

# Import your existing compiler components
try:
    from compiler.main import El
except ImportError as e:
    print(f"Error: Unable to import El compiler components: {e}")
    print("Make sure all modules are in the Python path")
    sys.exit(1)

__version__ = "1.0.6"

def main():
    """Main entry point for El CLI"""
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
            # Execute code directly
            print(f"Executing code: {args.code}")
            El.compile(args.code)
                
        elif args.file:
            # Execute a file
            file_path = Path(args.file)
            
            # Add .el extension if it doesn't exist
            if not file_path.suffix:
                file_path = file_path.with_suffix('.el')
            
            if not file_path.exists():
                print(f"Error: File '{file_path}' not found")
                sys.exit(1)
            
            try:
                print(f"Executing file: {file_path}")
                # Use your existing method to compile files
                El.compile_file(str(file_path).replace('.el', ''))
                    
            except IOError as e:
                print(f"File read error: {e}")
                sys.exit(1)
        else:
            # No arguments, show help
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
