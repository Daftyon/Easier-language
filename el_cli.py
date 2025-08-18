#!/usr/bin/env python3
"""
El Programming Language - Command Line Interface
Enhanced version with package download support
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from requests import *

# Import your existing compiler components
try:
    from compiler.main import El
    from system.package_manager import EasierHubPackageManager
    from utils.colors import Colors
    from requests import *

except ImportError as e:
    print(f"Error: Unable to import El compiler components: {e}")
    print("Make sure all modules are in the Python path")
    sys.exit(1)

# Import bring parser
try:
    from bring_parser.parser import parse_bring_file, parse_bring_string, BringParseError
    from bring_parser.parser import BringObject, BringArray, BringPrimitive
except ImportError:
    print("Warning: bring_parser not found. Package download features will be limited.")
    
    # Fallback minimal parser
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

class PackageDownloader:
    """Package download manager for .bring files"""
    
    def __init__(self):
        self.package_manager = EasierHubPackageManager(show_progress=True)
        self.downloaded_packages = []
        self.failed_packages = []
    
    def download_from_bring_file(self, bring_file_path: Path) -> Dict[str, Any]:
        """Download packages specified in a .bring file"""
        try:
            print(f"\n{Colors.BRIGHT_CYAN}📋 Reading package configuration from: {bring_file_path}{Colors.RESET}")
            
            # Parse .bring file
            bring_data = parse_bring_file(bring_file_path)
            
            # Extract package information
            package_info = self.extract_package_info(bring_data)
            
            if not package_info:
                print(f"{Colors.ERROR}❌ No valid package configuration found in {bring_file_path}{Colors.RESET}")
                return {"success": False, "message": "No package configuration found"}
            
            # Display package information
            self.display_package_info(package_info)
            
            # Download dependencies
            success = self.download_dependencies(package_info)
            
            # Summary
            self.print_download_summary()
            
            return {
                "success": success,
                "downloaded": self.downloaded_packages,
                "failed": self.failed_packages
            }
            
        except BringParseError as e:
            print(f"{Colors.ERROR}❌ Parse error in {bring_file_path}: {e}{Colors.RESET}")
            return {"success": False, "message": str(e)}
        except FileNotFoundError:
            print(f"{Colors.ERROR}❌ File not found: {bring_file_path}{Colors.RESET}")
            return {"success": False, "message": "File not found"}
        except Exception as e:
            print(f"{Colors.ERROR}❌ Error processing {bring_file_path}: {e}{Colors.RESET}")
            return {"success": False, "message": str(e)}
    
    def extract_package_info(self, bring_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract package information from parsed .bring data"""
        
        # Look for 'package' key
        if 'package' in bring_data:
            package_obj = bring_data['package']
            
            if isinstance(package_obj, BringObject):
                return self.convert_bring_object_to_dict(package_obj)
            elif isinstance(package_obj, dict):
                return package_obj
        
        # Look for top-level package fields
        package_fields = ['name', 'version', 'dependencies', 'dev_dependencies']
        if any(field in bring_data for field in package_fields):
            result = {}
            for key, value in bring_data.items():
                result[key] = self.convert_bring_value(value)
            return result
        
        return None
    
    def convert_bring_object_to_dict(self, bring_obj: BringObject) -> Dict[str, Any]:
        """Convert BringObject to regular dictionary"""
        result = {}
        for key, value in bring_obj.items.items():
            result[key] = self.convert_bring_value(value)
        return result
    
    def convert_bring_value(self, value: Any) -> Any:
        """Convert Bring values to Python values"""
        if isinstance(value, BringPrimitive):
            return value.value
        elif isinstance(value, BringObject):
            return self.convert_bring_object_to_dict(value)
        elif isinstance(value, BringArray):
            return [self.convert_bring_value(item) for item in value.items]
        else:
            return value
    
    def display_package_info(self, package_info: Dict[str, Any]):
        """Display package information"""
        print(f"\n{Colors.BRIGHT_WHITE}📦 Package Information:{Colors.RESET}")
        print(f"   Name: {Colors.CYAN}{package_info.get('name', 'Unknown')}{Colors.RESET}")
        print(f"   Version: {Colors.CYAN}{package_info.get('version', 'Unknown')}{Colors.RESET}")
        
        if 'description' in package_info:
            print(f"   Description: {Colors.YELLOW}{package_info['description']}{Colors.RESET}")
        
        if 'author' in package_info:
            print(f"   Author: {Colors.MAGENTA}{package_info['author']}{Colors.RESET}")
        
        if 'license' in package_info:
            print(f"   License: {Colors.GREEN}{package_info['license']}{Colors.RESET}")
        
        # Show dependencies
        deps = package_info.get('dependencies', [])
        if deps:
            print(f"\n{Colors.BRIGHT_YELLOW}📋 Dependencies ({len(deps)}):{Colors.RESET}")
            for dep in deps:
                dep_info = self.parse_dependency_string(dep)
                print(f"   • {Colors.CYAN}{dep_info['name']}{Colors.RESET} {Colors.YELLOW}{dep_info['version']}{Colors.RESET}")
        
        # Show dev dependencies
        dev_deps = package_info.get('dev_dependencies', [])
        if dev_deps:
            print(f"\n{Colors.BRIGHT_BLUE}🛠️  Dev Dependencies ({len(dev_deps)}):{Colors.RESET}")
            for dep in dev_deps:
                dep_info = self.parse_dependency_string(dep)
                print(f"   • {Colors.CYAN}{dep_info['name']}{Colors.RESET} {Colors.YELLOW}{dep_info['version']}{Colors.RESET}")
    
    def parse_dependency_string(self, dep_str: str) -> Dict[str, str]:
        """Parse dependency string like 'package@^1.2.0' or 'package@>=1.0.0'"""
        if '@' in dep_str:
            name, version = dep_str.split('@', 1)
            return {'name': name.strip(), 'version': version.strip()}
        else:
            return {'name': dep_str.strip(), 'version': 'latest'}
    
    def download_dependencies(self, package_info: Dict[str, Any]) -> bool:
        """Download all dependencies"""
        all_deps = []
        
        # Regular dependencies
        deps = package_info.get('dependencies', [])
        if deps:
            print(f"\n{Colors.BRIGHT_GREEN}⬇️  Downloading dependencies...{Colors.RESET}")
            all_deps.extend(deps)
        
        # Dev dependencies (optional - ask user)
        dev_deps = package_info.get('dev_dependencies', [])
        if dev_deps:
            print(f"\n{Colors.BRIGHT_BLUE}🤔 Dev dependencies found. Download them too? (y/N):{Colors.RESET} ", end="")
            try:
                response = input().strip().lower()
                if response in ['y', 'yes']:
                    all_deps.extend(dev_deps)
                    print(f"{Colors.GREEN}✓ Including dev dependencies{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}⏭️  Skipping dev dependencies{Colors.RESET}")
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}⏭️  Skipping dev dependencies{Colors.RESET}")
        
        if not all_deps:
            print(f"{Colors.YELLOW}⚠️  No dependencies to download{Colors.RESET}")
            return True
        
        # Download each dependency
        success_count = 0
        total_count = len(all_deps)
        
        print(f"\n{Colors.BRIGHT_WHITE}📥 Downloading {total_count} packages...{Colors.RESET}")
        
        for i, dep_str in enumerate(all_deps, 1):
            dep_info = self.parse_dependency_string(dep_str)
            package_name = dep_info['name']
            version = dep_info['version']
            
            print(f"\n{Colors.BRIGHT_CYAN}[{i}/{total_count}] {package_name}{Colors.RESET}")
            
            try:
                # Download the package
                result = self.package_manager.fetch_package(package_name)
                
                if result:
                    self.downloaded_packages.append({
                        'name': package_name,
                        'requested_version': version,
                        'actual_version': result.get('version', 'unknown'),
                        'cached': result.get('cached', False)
                    })
                    success_count += 1
                    print(f"   {Colors.SUCCESS}✅ Downloaded successfully{Colors.RESET}")
                else:
                    self.failed_packages.append({
                        'name': package_name,
                        'requested_version': version,
                        'error': 'Package not found or download failed'
                    })
                    print(f"   {Colors.ERROR}❌ Download failed{Colors.RESET}")
                    
            except Exception as e:
                self.failed_packages.append({
                    'name': package_name,
                    'requested_version': version,
                    'error': str(e)
                })
                print(f"   {Colors.ERROR}❌ Error: {e}{Colors.RESET}")
        
        return success_count == total_count
    
    def print_download_summary(self):
        """Print download summary"""
        total = len(self.downloaded_packages) + len(self.failed_packages)
        success = len(self.downloaded_packages)
        failed = len(self.failed_packages)
        
        print(f"\n{Colors.BRIGHT_WHITE}📊 Download Summary:{Colors.RESET}")
        print(f"   Total packages: {total}")
        print(f"   {Colors.SUCCESS}✅ Successfully downloaded: {success}{Colors.RESET}")
        
        if failed > 0:
            print(f"   {Colors.ERROR}❌ Failed to download: {failed}{Colors.RESET}")
        
        # Show successful downloads
        if self.downloaded_packages:
            print(f"\n{Colors.SUCCESS}Successfully downloaded packages:{Colors.RESET}")
            for pkg in self.downloaded_packages:
                cached_str = " (cached)" if pkg['cached'] else ""
                print(f"   • {Colors.CYAN}{pkg['name']}{Colors.RESET} v{pkg['actual_version']}{cached_str}")
        
        # Show failed downloads
        if self.failed_packages:
            print(f"\n{Colors.ERROR}Failed packages:{Colors.RESET}")
            for pkg in self.failed_packages:
                print(f"   • {Colors.RED}{pkg['name']}{Colors.RESET} - {pkg['error']}")

def create_sample_bring_file():
    """Create a sample .bring file for demonstration"""
    sample_content = '''# package.bring
package = {
    name = "my-project"
    version = "1.0.0"
    description = "My awesome EL project"
    author = "Your Name <you@example.com>"
    license = "MIT"
    
    dependencies = [
        "http-server@^2.3.0"
        "json-parser@^1.2.0" 
        "logger@~2.1.0"
        "crypto@>=1.0.0"
    ]
    
    dev_dependencies = [
        "test-framework@^1.0.0"
        "benchmark-tools@^0.5.0"
    ]
    
    repository = "https://github.com/yourname/my-project"
    homepage = "https://yourname.github.io/my-project"
}
'''
    
    bring_file = Path("package.bring")
    bring_file.write_text(sample_content)
    print(f"{Colors.SUCCESS}✅ Created sample package.bring file{Colors.RESET}")

def main():
    """Main entry point for El CLI"""
    parser = argparse.ArgumentParser(
        description='El Programming Language',
        prog='el'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command (default)
    run_parser = subparsers.add_parser('run', help='Run El source code')
    run_parser.add_argument('file', nargs='?', help='El source file (.el)')
    run_parser.add_argument('-c', '--code', help='Execute El code from command line')
    
    # Download command for packages
    download_parser = subparsers.add_parser('download', help='Download packages from .bring file')
    download_parser.add_argument(
        'bring_file', 
        nargs='?', 
        default='package.bring',
        help='Path to .bring file (default: package.bring)'
    )
    download_parser.add_argument(
        '--sample', 
        action='store_true',
        help='Create a sample package.bring file'
    )
    
    # Package management commands
    pkg_parser = subparsers.add_parser('package', help='Package management')
    pkg_subparsers = pkg_parser.add_subparsers(dest='pkg_command', help='Package commands')
    
    # Cache commands
    cache_parser = pkg_subparsers.add_parser('cache', help='Cache management')
    cache_parser.add_argument('action', choices=['list', 'clear'], help='Cache action')
    
    # Global options
    parser.add_argument('-v', '--version', action='version', version=f'El {__version__}')
    
    # Handle case where no command is specified
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # If first argument is a file and no subcommand, treat as 'run'
    if len(sys.argv) >= 2 and not sys.argv[1] in ['run', 'download', 'package'] and not sys.argv[1].startswith('-'):
        sys.argv.insert(1, 'run')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'run' or args.command is None:
            handle_run_command(args)
        elif args.command == 'download':
            handle_download_command(args)
        elif args.command == 'package':
            handle_package_command(args)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.ERROR}Error: {e}{Colors.RESET}")
        sys.exit(1)

def handle_run_command(args):
    """Handle the run command"""
    if args.code:
        # Execute code directly
        print(f"{Colors.BRIGHT_GREEN}🚀 Executing code:{Colors.RESET} {args.code}")
        El.compile(args.code)
            
    elif args.file:
        # Execute a file
        file_path = Path(args.file)
        
        # Add .el extension if it doesn't exist
        if not file_path.suffix:
            file_path = file_path.with_suffix('.el')
        
        if not file_path.exists():
            print(f"{Colors.ERROR}❌ File '{file_path}' not found{Colors.RESET}")
            sys.exit(1)
        
        try:
            print(f"{Colors.BRIGHT_GREEN}🚀 Executing file:{Colors.RESET} {file_path}")
            # Use your existing method to compile files
            El.compile_file(str(file_path).replace('.el', ''))
                
        except IOError as e:
            print(f"{Colors.ERROR}File read error: {e}{Colors.RESET}")
            sys.exit(1)
    else:
        # No arguments for run, show help
        print(f"{Colors.YELLOW}Please specify a file to run or use -c to execute code directly{Colors.RESET}")

def handle_download_command(args):
    """Handle the download command"""
    if args.sample:
        create_sample_bring_file()
        return
    
    bring_file_path = Path(args.bring_file)
    
    if not bring_file_path.exists():
        print(f"{Colors.ERROR}❌ Bring file not found: {bring_file_path}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Use 'el download --sample' to create a sample package.bring file{Colors.RESET}")
        sys.exit(1)
    
    downloader = PackageDownloader()
    result = downloader.download_from_bring_file(bring_file_path)
    
    if not result['success']:
        sys.exit(1)

def handle_package_command(args):
    """Handle package management commands"""
    if args.pkg_command == 'cache':
        pm = EasierHubPackageManager(show_progress=False)
        
        if args.action == 'list':
            print(f"{Colors.BRIGHT_CYAN}📦 Cached Packages:{Colors.RESET}")
            cached = pm.list_cached_packages()
            if cached:
                for package in cached:
                    print(f"   • {package}")
            else:
                print(f"   {Colors.YELLOW}No cached packages found{Colors.RESET}")
        
        elif args.action == 'clear':
            print(f"{Colors.YELLOW}🗑️  Clearing package cache...{Colors.RESET}")
            pm.clear_cache(show_progress=True)

if __name__ == '__main__':
    main()
