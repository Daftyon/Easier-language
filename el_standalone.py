#!/usr/bin/env python3
"""
El Programming Language - Enhanced Standalone Executable
FINAL VERSION - FIXED ARGUMENT PARSING
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from requests import *

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
    from utils.colors import Colors
    from system.package_manager import EasierHubPackageManager
    from requests import *

except ImportError as e:
    print(f"Error: Unable to import El components: {e}")
    sys.exit(1)

# Import bring parser
try:
    from bring_parser.parser import parse_bring_file, parse_bring_string, BringParseError
    from bring_parser.parser import BringObject, BringArray, BringPrimitive
except ImportError:
    print("Warning: bring_parser not found. Package features limited.")
    
    def parse_bring_file(file_path):
        return {}
    
    def parse_bring_string(content):
        return {}
    
    class BringParseError(Exception):
        pass
    
    class BringObject:
        def __init__(self, items):
            self.items = items
    
    class BringArray:
        def __init__(self, items):
            self.items = items
    
    class BringPrimitive:
        def __init__(self, value):
            self.value = value

__version__ = "1.0.9"
__author__ = "El Language Team"

def execute_el_file(file_path: Path, debug: bool = False) -> bool:
    """Execute an El file with proper error handling and debug output"""
    try:
        if debug:
            print(f"🔍 Debug: Starting execution of {file_path}")
        
        # Check if file exists
        if not file_path.exists():
            print(f"❌ Error: File '{file_path}' not found")
            return False
        
        if debug:
            print(f"🔍 Debug: File exists, reading content...")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read().strip()
        except UnicodeDecodeError:
            print(f"❌ Error: File encoding issue. Please ensure {file_path} is UTF-8 encoded.")
            return False
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
        
        if not code:
            print(f"❌ Error: File {file_path} is empty")
            return False
        
        if debug:
            print(f"🔍 Debug: File content read successfully ({len(code)} characters)")
            print(f"🔍 Debug: Content preview: {code[:100]}{'...' if len(code) > 100 else ''}")
        
        # Execute the code
        print(f"🚀 Executing: {file_path.name}")
        
        if debug:
            print(f"🔍 Debug: Calling El.compile() with code...")
        
        El.compile(code)
        
        if debug:
            print(f"🔍 Debug: El.compile() completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Execution error: {e}")
        if debug:
            import traceback
            print("🔍 Debug: Full traceback:")
            traceback.print_exc()
        return False

class ElREPL:
    """Enhanced interactive REPL with package management"""
    
    def __init__(self):
        self.history = []
        try:
            self.package_manager = EasierHubPackageManager(show_progress=True)
        except:
            self.package_manager = None
            
        self.commands = {
            'help': self.show_help,
            'exit': self.exit_repl,
            'quit': self.exit_repl,
            'version': self.show_version,
            'clear': self.clear_screen,
            'history': self.show_history,
            'packages': self.show_packages,
            'download': self.download_package,
        }
        
    def start(self):
        """Start the interactive REPL"""
        self.show_welcome()
        
        while True:
            try:
                code = input("el> ").strip()
                
                if not code:
                    continue
                
                # Handle special commands
                if code in self.commands:
                    self.commands[code]()
                    continue
                
                # Handle command with arguments
                if code.startswith('download '):
                    package_name = code[9:].strip()
                    self.download_package(package_name)
                    continue
                
                # Save to history
                self.history.append(code)
                
                # Execute El code
                try:
                    # Wrap code if necessary
                    if not code.startswith('ALGORITHM') and not code.startswith('program'):
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
        show_banner()
        print(f"""
Interactive Mode - Type 'help' for commands
Created by {__author__}
""")
    
    def show_help(self):
        """Display enhanced help"""
        help_text = f"""
El REPL Commands:
  help              - Show this help
  version           - Show version info
  clear             - Clear screen
  history           - Show command history
  packages          - List cached packages
  download <name>   - Download a package
  exit/quit         - Exit REPL

El Language Syntax:
  Variables:  var x: integer = 5;
  Functions:  function add(a: integer, b: integer): integer {{ return a + b; }}
  Display:    show "Hello, World!";
  Loops:      for i: integer = 0; i < 10; i = i + 1 {{ show i; }}
  Packages:   bring package_name;
  Program:    program main {{ var x: integer = 5; show x; }}

Documentation: https://github.com/Daftyon/Easier-language
"""
        print(help_text)
    
    def show_version(self):
        """Display version"""
        print(f"El Programming Language v{__version__}")
        print(f"Created by {__author__}")
    
    def clear_screen(self):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        show_banner()
    
    def show_history(self):
        """Display history"""
        if not self.history:
            print("No history available")
            return
        
        print("Command history:")
        for i, cmd in enumerate(self.history[-10:], 1):
            print(f"  {i}: {cmd}")
    
    def show_packages(self):
        """Show cached packages"""
        if not self.package_manager:
            print("Package manager not available")
            return
            
        try:
            cached = self.package_manager.list_cached_packages()
            if cached:
                print("📦 Cached Packages:")
                for package in cached:
                    print(f"   • {package}")
            else:
                print("No cached packages")
        except Exception as e:
            print(f"Error listing packages: {e}")
    
    def download_package(self, package_name=None):
        """Download a package"""
        if not self.package_manager:
            print("Package manager not available")
            return
            
        if not package_name:
            package_name = input("Enter package name: ").strip()
        
        if package_name:
            print(f"Downloading {package_name}...")
            try:
                result = self.package_manager.fetch_package(package_name)
                if result:
                    print(f"✅ Package '{package_name}' downloaded successfully!")
                else:
                    print(f"❌ Failed to download '{package_name}'")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def exit_repl(self):
        """Exit REPL"""
        print("Goodbye!")
        sys.exit(0)

class PackageDownloader:
    """Package download manager for .bring files"""
    
    def __init__(self):
        try:
            self.package_manager = EasierHubPackageManager(show_progress=True)
        except:
            self.package_manager = None
        self.downloaded_packages = []
        self.failed_packages = []
    
    def download_from_bring_file(self, bring_file_path: Path) -> Dict[str, Any]:
        """Download packages from .bring file"""
        if not self.package_manager:
            print("❌ Package manager not available")
            return {"success": False}
            
        try:
            print(f"\n📋 Reading: {bring_file_path}")
            
            bring_data = parse_bring_file(bring_file_path)
            package_info = self.extract_package_info(bring_data)
            
            if not package_info:
                print("❌ No package config found")
                return {"success": False}
            
            self.display_package_info(package_info)
            success = self.download_dependencies(package_info)
            self.print_summary()
            
            return {"success": success}
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False}
    
    def extract_package_info(self, bring_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract package info from .bring data"""
        if 'package' in bring_data:
            package_obj = bring_data['package']
            if isinstance(package_obj, BringObject):
                return self.convert_bring_object(package_obj)
            return package_obj
        
        # Check for top-level fields
        fields = ['name', 'version', 'dependencies', 'dev_dependencies']
        if any(field in bring_data for field in fields):
            result = {}
            for key, value in bring_data.items():
                result[key] = self.convert_bring_value(value)
            return result
        
        return None
    
    def convert_bring_object(self, obj: BringObject) -> Dict[str, Any]:
        """Convert BringObject to dict"""
        result = {}
        for key, value in obj.items.items():
            result[key] = self.convert_bring_value(value)
        return result
    
    def convert_bring_value(self, value: Any) -> Any:
        """Convert Bring values"""
        if isinstance(value, BringPrimitive):
            return value.value
        elif isinstance(value, BringObject):
            return self.convert_bring_object(value)
        elif isinstance(value, BringArray):
            return [self.convert_bring_value(item) for item in value.items]
        return value
    
    def display_package_info(self, info: Dict[str, Any]):
        """Display package information"""
        print(f"\n📦 Package:")
        print(f"   Name: {info.get('name', 'Unknown')}")
        print(f"   Version: {info.get('version', 'Unknown')}")
        
        if 'description' in info:
            print(f"   Description: {info['description']}")
        
        deps = info.get('dependencies', [])
        if deps:
            print(f"\n📋 Dependencies ({len(deps)}):")
            for dep in deps:
                print(f"   • {dep}")
    
    def download_dependencies(self, info: Dict[str, Any]) -> bool:
        """Download dependencies"""
        deps = info.get('dependencies', [])
        if not deps:
            print("⚠️ No dependencies")
            return True
        
        print(f"\n📥 Downloading {len(deps)} packages...")
        
        success_count = 0
        for i, dep in enumerate(deps, 1):
            name = dep.split('@')[0] if '@' in dep else dep
            print(f"\n[{i}/{len(deps)}] {name}")
            
            try:
                result = self.package_manager.fetch_package(name)
                if result:
                    self.downloaded_packages.append(name)
                    success_count += 1
                else:
                    self.failed_packages.append(name)
            except Exception as e:
                self.failed_packages.append(name)
                print(f"   ❌ Error: {e}")
        
        return success_count == len(deps)
    
    def print_summary(self):
        """Print download summary"""
        success = len(self.downloaded_packages)
        failed = len(self.failed_packages)
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Downloaded: {success}")
        if failed > 0:
            print(f"   ❌ Failed: {failed}")

def show_banner():
    """Display El banner"""
    banner = f"""
    ███████╗██╗         ██╗      █████╗ ███╗   ██╗ ██████╗ 
    ██╔════╝██║         ██║     ██╔══██╗████╗  ██║██╔════╝ 
    █████╗  ██║         ██║     ███████║██╔██╗ ██║██║  ███╗
    ██╔══╝  ██║         ██║     ██╔══██║██║╚██╗██║██║   ██║
    ███████╗███████╗    ███████╗██║  ██║██║ ╚████║╚██████╔╝
    ╚══════╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    
    El Programming Language v{__version__}
    A modern and easy programming language
    """
    print(banner)

def create_sample_bring_file():
    """Create sample .bring file"""
    content = '''# package.bring
package = {
    name = "my-project"
    version = "1.0.0"
    description = "My awesome EL project"
    
    dependencies = [
        "variables_demo"
        "hello"
        "ss"
    ]
}
'''
    Path("package.bring").write_text(content)
    print("✅ Created sample package.bring")

def main():
    """Main entry point - FIXED ARGUMENT PARSING"""
    
    # First, check if this is a direct file execution (no subcommands)
    # Handle case: 'el filename.el'
    if (len(sys.argv) == 2 and 
        not sys.argv[1].startswith('-') and 
        sys.argv[1] not in ['download', 'package', 'run'] and
        (sys.argv[1].endswith('.el') or Path(sys.argv[1] + '.el').exists())):
        
        file_path = Path(sys.argv[1])
        if not file_path.suffix:
            file_path = file_path.with_suffix('.el')
        
        success = execute_el_file(file_path, debug=False)
        sys.exit(0 if success else 1)
    
    # Create parser
    parser = argparse.ArgumentParser(
        description='El Programming Language - Enhanced CLI',
        prog='el',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Usage examples:
  el                          Start interactive mode
  el hello.el                 Execute an El file (direct)
  el run hello.el             Execute an El file (explicit)
  el -c "show 'Hello';"       Execute code directly
  el --version                Show version
  el download                 Download from package.bring
  el download --sample        Create sample package.bring
  el package cache list       List cached packages
  el package cache clear      Clear package cache
  
Documentation: https://github.com/Daftyon/Easier-language
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run El code')
    run_parser.add_argument('file', nargs='?', help='El file (.el)')
    run_parser.add_argument('-c', '--code', help='Execute code directly')
    
    # Download command
    dl_parser = subparsers.add_parser('download', help='Download packages')
    dl_parser.add_argument('bring_file', nargs='?', default='package.bring', help='Bring file')
    dl_parser.add_argument('--sample', action='store_true', help='Create sample')
    
    # Package command
    pkg_parser = subparsers.add_parser('package', help='Package management')
    pkg_sub = pkg_parser.add_subparsers(dest='pkg_cmd')
    cache_parser = pkg_sub.add_parser('cache', help='Cache management')
    cache_parser.add_argument('action', choices=['list', 'clear'], help='Action')
    
    # Global options (NO CONFLICTING FILE ARGUMENT)
    parser.add_argument('-v', '--version', action='version', version=f'El Language v{__version__}')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive mode (REPL)')
    parser.add_argument('-c', '--code', help='Execute El code from command line')
    parser.add_argument('--banner', action='store_true', help='Display El banner')
    parser.add_argument('--debug', action='store_true', help='Debug mode with detailed information')
    
    args = parser.parse_args()
    
    try:
        # Handle new commands first
        if args.command == 'download':
            if args.sample:
                create_sample_bring_file()
                return
            
            bring_file = Path(args.bring_file)
            if not bring_file.exists():
                print(f"❌ File not found: {bring_file}")
                print("💡 Use 'el download --sample' to create one")
                sys.exit(1)
            
            downloader = PackageDownloader()
            result = downloader.download_from_bring_file(bring_file)
            sys.exit(0 if result['success'] else 1)
        
        elif args.command == 'package':
            try:
                pm = EasierHubPackageManager(show_progress=False)
                if args.pkg_cmd == 'cache':
                    if args.action == 'list':
                        cached = pm.list_cached_packages()
                        if cached:
                            print("📦 Cached:")
                            for pkg in cached:
                                print(f"   • {pkg}")
                        else:
                            print("No cached packages")
                    elif args.action == 'clear':
                        pm.clear_cache(show_progress=True)
            except Exception as e:
                print(f"Package manager error: {e}")
            return
        
        elif args.command == 'run':
            # Handle 'el run' command
            if args.debug:
                print(f"🔍 Debug: Run command detected")
                print(f"🔍 Debug: args.file = {getattr(args, 'file', 'NOT_SET')}")
                print(f"🔍 Debug: args.code = {getattr(args, 'code', 'NOT_SET')}")
            
            if args.code:
                # Execute code directly
                if args.debug:
                    print(f"🔍 Debug: Executing code: {args.code}")
                El.compile(args.code)
            elif args.file:
                # Execute file using new method
                file_path = Path(args.file)
                if not file_path.suffix:
                    file_path = file_path.with_suffix('.el')
                
                if args.debug:
                    print(f"🔍 Debug: Executing file from run command: {file_path}")
                    
                success = execute_el_file(file_path, args.debug)
                sys.exit(0 if success else 1)
            else:
                print("❌ Error: No file or code specified for run command")
                print("Usage: el run <file.el> or el run -c \"code\"")
                if args.debug:
                    print(f"🔍 Debug: Available args: {vars(args)}")
                sys.exit(1)
            return
        
        # Default behavior
        if args.banner:
            show_banner()
            return
            
        if args.interactive:
            # Interactive mode
            repl = ElREPL()
            repl.start()
            
        elif args.code:
            # Execute code from command line
            if args.debug:
                print(f"🔍 Debug: Executing code: {args.code}")
            El.compile(args.code)
        else:
            # No command, no file, no code - start interactive mode
            repl = ElREPL()
            repl.start()
            
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
