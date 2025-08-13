#!/usr/bin/env python3
"""
El Programming Language - Enhanced Standalone Executable
Complete version with REPL + CLI + Package Management
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

class ElREPL:
    """Enhanced interactive REPL with package management"""
    
    def __init__(self):
        self.history = []
        self.package_manager = EasierHubPackageManager(show_progress=True)
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
        show_banner()
        print(f"""
{Colors.BRIGHT_CYAN}Interactive Mode - Type 'help' for commands{Colors.RESET}
Created by {__author__}
""")
    
    def show_help(self):
        """Display enhanced help"""
        help_text = f"""
{Colors.BRIGHT_WHITE}El REPL Commands:{Colors.RESET}
  {Colors.CYAN}help{Colors.RESET}              - Show this help
  {Colors.CYAN}version{Colors.RESET}           - Show version info
  {Colors.CYAN}clear{Colors.RESET}             - Clear screen
  {Colors.CYAN}history{Colors.RESET}           - Show command history
  {Colors.CYAN}packages{Colors.RESET}          - List cached packages
  {Colors.CYAN}download <name>{Colors.RESET}   - Download a package
  {Colors.CYAN}exit/quit{Colors.RESET}         - Exit REPL

{Colors.BRIGHT_WHITE}El Language Syntax:{Colors.RESET}
  {Colors.YELLOW}Variables:{Colors.RESET}  var x: integer = 5;
  {Colors.YELLOW}Functions:{Colors.RESET}  function add(a: integer, b: integer): integer {{ return a + b; }}
  {Colors.YELLOW}Display:{Colors.RESET}    show "Hello, World!";
  {Colors.YELLOW}Loops:{Colors.RESET}      for i: integer = 0; i < 10; i = i + 1 {{ show i; }}
  {Colors.YELLOW}Packages:{Colors.RESET}   bring package_name;

{Colors.BRIGHT_WHITE}Documentation:{Colors.RESET} https://github.com/Daftyon/Easier-language
"""
        print(help_text)
    
    def show_version(self):
        """Display version"""
        print(f"{Colors.BRIGHT_GREEN}El Programming Language v{__version__}{Colors.RESET}")
        print(f"Created by {__author__}")
    
    def clear_screen(self):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        show_banner()
    
    def show_history(self):
        """Display history"""
        if not self.history:
            print(f"{Colors.YELLOW}No history available{Colors.RESET}")
            return
        
        print(f"{Colors.BRIGHT_WHITE}Command history:{Colors.RESET}")
        for i, cmd in enumerate(self.history[-10:], 1):
            print(f"  {Colors.CYAN}{i}:{Colors.RESET} {cmd}")
    
    def show_packages(self):
        """Show cached packages"""
        cached = self.package_manager.list_cached_packages()
        if cached:
            print(f"{Colors.BRIGHT_CYAN}📦 Cached Packages:{Colors.RESET}")
            for package in cached:
                print(f"   • {package}")
        else:
            print(f"{Colors.YELLOW}No cached packages{Colors.RESET}")
    
    def download_package(self, package_name=None):
        """Download a package"""
        if not package_name:
            package_name = input("Enter package name: ").strip()
        
        if package_name:
            print(f"{Colors.BRIGHT_GREEN}Downloading {package_name}...{Colors.RESET}")
            try:
                result = self.package_manager.fetch_package(package_name)
                if result:
                    print(f"{Colors.SUCCESS}✅ Package '{package_name}' downloaded successfully!{Colors.RESET}")
                else:
                    print(f"{Colors.ERROR}❌ Failed to download '{package_name}'{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.ERROR}❌ Error: {e}{Colors.RESET}")
    
    def exit_repl(self):
        """Exit REPL"""
        print(f"{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}")
        sys.exit(0)

class PackageDownloader:
    """Package download manager for .bring files"""
    
    def __init__(self):
        self.package_manager = EasierHubPackageManager(show_progress=True)
        self.downloaded_packages = []
        self.failed_packages = []
    
    def download_from_bring_file(self, bring_file_path: Path) -> Dict[str, Any]:
        """Download packages from .bring file"""
        try:
            print(f"\n{Colors.BRIGHT_CYAN}📋 Reading: {bring_file_path}{Colors.RESET}")
            
            bring_data = parse_bring_file(bring_file_path)
            package_info = self.extract_package_info(bring_data)
            
            if not package_info:
                print(f"{Colors.ERROR}❌ No package config found{Colors.RESET}")
                return {"success": False}
            
            self.display_package_info(package_info)
            success = self.download_dependencies(package_info)
            self.print_summary()
            
            return {"success": success}
            
        except Exception as e:
            print(f"{Colors.ERROR}❌ Error: {e}{Colors.RESET}")
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
        print(f"\n{Colors.BRIGHT_WHITE}📦 Package:{Colors.RESET}")
        print(f"   Name: {Colors.CYAN}{info.get('name', 'Unknown')}{Colors.RESET}")
        print(f"   Version: {Colors.CYAN}{info.get('version', 'Unknown')}{Colors.RESET}")
        
        if 'description' in info:
            print(f"   Description: {Colors.YELLOW}{info['description']}{Colors.RESET}")
        
        deps = info.get('dependencies', [])
        if deps:
            print(f"\n{Colors.BRIGHT_YELLOW}📋 Dependencies ({len(deps)}):{Colors.RESET}")
            for dep in deps:
                print(f"   • {Colors.CYAN}{dep}{Colors.RESET}")
    
    def download_dependencies(self, info: Dict[str, Any]) -> bool:
        """Download dependencies"""
        deps = info.get('dependencies', [])
        if not deps:
            print(f"{Colors.YELLOW}⚠️ No dependencies{Colors.RESET}")
            return True
        
        print(f"\n{Colors.BRIGHT_GREEN}📥 Downloading {len(deps)} packages...{Colors.RESET}")
        
        success_count = 0
        for i, dep in enumerate(deps, 1):
            name = dep.split('@')[0] if '@' in dep else dep
            print(f"\n{Colors.BRIGHT_CYAN}[{i}/{len(deps)}] {name}{Colors.RESET}")
            
            try:
                result = self.package_manager.fetch_package(name)
                if result:
                    self.downloaded_packages.append(name)
                    success_count += 1
                else:
                    self.failed_packages.append(name)
            except Exception as e:
                self.failed_packages.append(name)
                print(f"   {Colors.ERROR}❌ Error: {e}{Colors.RESET}")
        
        return success_count == len(deps)
    
    def print_summary(self):
        """Print download summary"""
        success = len(self.downloaded_packages)
        failed = len(self.failed_packages)
        
        print(f"\n{Colors.BRIGHT_WHITE}📊 Summary:{Colors.RESET}")
        print(f"   {Colors.SUCCESS}✅ Downloaded: {success}{Colors.RESET}")
        if failed > 0:
            print(f"   {Colors.ERROR}❌ Failed: {failed}{Colors.RESET}")

def show_banner():
    """Display El banner"""
    banner = f"""
    {Colors.BRIGHT_BLUE}███████╗██╗         ██╗      █████╗ ███╗   ██╗ ██████╗ {Colors.RESET}
    {Colors.BRIGHT_BLUE}██╔════╝██║         ██║     ██╔══██╗████╗  ██║██╔════╝ {Colors.RESET}
    {Colors.BRIGHT_BLUE}█████╗  ██║         ██║     ███████║██╔██╗ ██║██║  ███╗{Colors.RESET}
    {Colors.BRIGHT_BLUE}██╔══╝  ██║         ██║     ██╔══██║██║╚██╗██║██║   ██║{Colors.RESET}
    {Colors.BRIGHT_BLUE}███████╗███████╗    ███████╗██║  ██║██║ ╚████║╚██████╔╝{Colors.RESET}
    {Colors.BRIGHT_BLUE}╚══════╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ {Colors.RESET}
    
    {Colors.BRIGHT_WHITE}El Programming Language v{__version__}{Colors.RESET}
    {Colors.CYAN}A modern and easy programming language{Colors.RESET}
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
    print(f"{Colors.SUCCESS}✅ Created sample package.bring{Colors.RESET}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='El Programming Language - Enhanced CLI',
        prog='el',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.BRIGHT_WHITE}Examples:{Colors.RESET}
  el                          Start interactive REPL
  el hello.el                 Execute El file
  el -c "show 'Hello';"       Execute code directly
  el download                 Download from package.bring
  el download --sample        Create sample package.bring
  
{Colors.BRIGHT_WHITE}Documentation:{Colors.RESET} https://github.com/Daftyon/Easier-language
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
    
    # Global options
    parser.add_argument('-v', '--version', action='version', version=f'El v{__version__}')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive REPL')
    parser.add_argument('-c', '--code', help='Execute code directly')
    parser.add_argument('--banner', action='store_true', help='Show banner')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    # Single file argument handling
    parser.add_argument('file', nargs='?', help='El source file')
    
    args = parser.parse_args()
    
    try:
        # Handle banner
        if args.banner:
            show_banner()
            return
        
        # Handle commands
        if args.command == 'download':
            if args.sample:
                create_sample_bring_file()
                return
            
            bring_file = Path(args.bring_file)
            if not bring_file.exists():
                print(f"{Colors.ERROR}❌ File not found: {bring_file}{Colors.RESET}")
                print(f"{Colors.YELLOW}💡 Use 'el download --sample' to create one{Colors.RESET}")
                sys.exit(1)
            
            downloader = PackageDownloader()
            result = downloader.download_from_bring_file(bring_file)
            if not result['success']:
                sys.exit(1)
            return
        
        elif args.command == 'package':
            pm = EasierHubPackageManager(show_progress=False)
            if args.pkg_cmd == 'cache':
                if args.action == 'list':
                    cached = pm.list_cached_packages()
                    if cached:
                        print(f"{Colors.BRIGHT_CYAN}📦 Cached:{Colors.RESET}")
                        for pkg in cached:
                            print(f"   • {pkg}")
                    else:
                        print(f"{Colors.YELLOW}No cached packages{Colors.RESET}")
                elif args.action == 'clear':
                    pm.clear_cache(show_progress=True)
            return
        
        elif args.command == 'run':
            if args.code:
                El.compile(args.code)
            elif args.file:
                file_path = Path(args.file)
                if not file_path.suffix:
                    file_path = file_path.with_suffix('.el')
                
                if not file_path.exists():
                    print(f"{Colors.ERROR}❌ File not found: {file_path}{Colors.RESET}")
                    sys.exit(1)
                
                El.compile_file(str(file_path).replace('.el', ''))
            return
        
        # Default behavior
        if args.interactive or (not args.file and not args.code and not args.command):
            # Start REPL
            repl = ElREPL()
            repl.start()
        elif args.code:
            # Execute code
            El.compile(args.code)
        elif args.file:
            # Execute file
            file_path = Path(args.file)
            if not file_path.suffix:
                file_path = file_path.with_suffix('.el')
            
            if not file_path.exists():
                print(f"{Colors.ERROR}❌ File not found: {file_path}{Colors.RESET}")
                sys.exit(1)
            
            if args.debug:
                print(f"Executing: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            El.compile(code)
        else:
            # Show help
            parser.print_help()
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"{Colors.ERROR}Error: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == '__main__':
    main()
