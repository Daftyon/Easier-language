#!/usr/bin/env python3
"""
Bring File Parser - Parse .bring files for package dependencies
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from utils.colors import Colors

@dataclass
class PackageDependency:
    """Represents a package dependency with version constraints"""
    name: str
    version_spec: str
    constraint_type: str = "exact"  # exact, caret (^), tilde (~), gte (>=)
    
    def __post_init__(self):
        """Parse version specification"""
        if self.version_spec.startswith("^"):
            self.constraint_type = "caret"
            self.version_spec = self.version_spec[1:]
        elif self.version_spec.startswith("~"):
            self.constraint_type = "tilde" 
            self.version_spec = self.version_spec[1:]
        elif self.version_spec.startswith(">="):
            self.constraint_type = "gte"
            self.version_spec = self.version_spec[2:]
        elif self.version_spec.startswith("=="):
            self.constraint_type = "exact"
            self.version_spec = self.version_spec[2:]
    
    def matches_version(self, version: str) -> bool:
        """Check if a version satisfies this dependency constraint"""
        # Simple version matching - in production you'd use a proper semver library
        try:
            dep_parts = [int(x) for x in self.version_spec.split('.')]
            ver_parts = [int(x) for x in version.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(dep_parts), len(ver_parts))
            dep_parts.extend([0] * (max_len - len(dep_parts)))
            ver_parts.extend([0] * (max_len - len(ver_parts)))
            
            if self.constraint_type == "exact":
                return dep_parts == ver_parts
            elif self.constraint_type == "caret":  # ^1.2.3 allows 1.x.x but not 2.x.x
                return (dep_parts[0] == ver_parts[0] and 
                       ver_parts >= dep_parts)
            elif self.constraint_type == "tilde":  # ~1.2.3 allows 1.2.x but not 1.3.x
                return (dep_parts[:2] == ver_parts[:2] and 
                       ver_parts >= dep_parts)
            elif self.constraint_type == "gte":
                return ver_parts >= dep_parts
            
        except (ValueError, IndexError):
            return False
        
        return False
    
    def __str__(self):
        constraint_symbol = {
            "caret": "^",
            "tilde": "~", 
            "gte": ">=",
            "exact": "=="
        }.get(self.constraint_type, "")
        
        return f"{self.name}@{constraint_symbol}{self.version_spec}"

@dataclass 
class BringPackage:
    """Represents a package definition from a .bring file"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    license: str = ""
    repository: str = ""
    homepage: str = ""
    dependencies: List[PackageDependency] = None
    dev_dependencies: List[PackageDependency] = None
    semver: bool = False
    git: bool = False
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.dev_dependencies is None:
            self.dev_dependencies = []

class BringFileParser:
    """Parser for .bring package definition files using bring_parser library"""
    
    def __init__(self):
        self.use_bring_parser = BRING_PARSER_AVAILABLE
        
    def parse_file(self, file_path: Path) -> Optional[BringPackage]:
        """Parse a .bring file and return package definition"""
        try:
            if not file_path.exists():
                print(f"{Colors.ERROR}❌ Bring file not found: {file_path}{Colors.RESET}")
                return None
            
            content = file_path.read_text(encoding='utf-8')
            return self.parse_string(content)
            
        except Exception as e:
            print(f"{Colors.ERROR}❌ Error reading bring file: {e}{Colors.RESET}")
            return None
    
    def parse_string(self, content: str) -> Optional[BringPackage]:
        """Parse bring file content string using bring_parser"""
        try:
            if self.use_bring_parser:
                # Use the official bring_parser library
                parsed_data = parse_bring_string(content)
                
                if "error" in parsed_data:
                    print(f"{Colors.ERROR}❌ Parsing error: {parsed_data['error']}{Colors.RESET}")
                    return None
                
                return self._convert_parsed_data_to_package(parsed_data)
            else:
                # Fallback to basic parsing
                return self._fallback_parse(content)
                
        except BringParseError as e:
            print(f"{Colors.ERROR}❌ Bring parsing error: {e}{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.ERROR}❌ Error parsing bring file: {e}{Colors.RESET}")
            return None
    
    def _convert_parsed_data_to_package(self, parsed_data: Dict[str, Any]) -> BringPackage:
        """Convert parsed data from bring_parser to BringPackage object"""
        # The bring_parser should return structured data
        package_info = parsed_data.get('package', {})
        
        # Extract basic information
        name = package_info.get('name', '')
        version = package_info.get('version', '1.0.0')
        description = package_info.get('description', '')
        author = package_info.get('author', '')
        license_info = package_info.get('license', '')
        repository = package_info.get('repository', '')
        homepage = package_info.get('homepage', '')
        
        # Parse dependencies
        dependencies = []
        if 'dependencies' in package_info:
            deps = package_info['dependencies']
            if isinstance(deps, list):
                for dep in deps:
                    dependencies.append(self._parse_dependency_from_parser(dep))
            elif isinstance(deps, dict):
                for name, version in deps.items():
                    dependencies.append(PackageDependency(name, str(version)))
        
        # Parse dev dependencies
        dev_dependencies = []
        if 'dev_dependencies' in package_info:
            dev_deps = package_info['dev_dependencies']
            if isinstance(dev_deps, list):
                for dep in dev_deps:
                    dev_dependencies.append(self._parse_dependency_from_parser(dep))
            elif isinstance(dev_deps, dict):
                for name, version in dev_deps.items():
                    dev_dependencies.append(PackageDependency(name, str(version)))
        
        # Check for special flags
        semver = package_info.get('semver', False) or '@semver=true' in str(package_info)
        git = package_info.get('git', False) or '@git=true' in str(package_info)
        
        return BringPackage(
            name=name,
            version=version,
            description=description,
            author=author,
            license=license_info,
            repository=repository,
            homepage=homepage,
            dependencies=dependencies,
            dev_dependencies=dev_dependencies,
            semver=semver,
            git=git
        )
    
    def _parse_dependency_from_parser(self, dep_data) -> PackageDependency:
        """Parse dependency from bring_parser output"""
        if isinstance(dep_data, str):
            # Simple string format: "package@version"
            return self._parse_dependency_string(dep_data)
        elif isinstance(dep_data, dict):
            # Object format: {"name": "package", "version": "^1.0.0"}
            name = dep_data.get('name', '')
            version = dep_data.get('version', '*')
            return PackageDependency(name, version)
        else:
            # Fallback
            return PackageDependency(str(dep_data), '*')
    
    def _parse_dependency_string(self, dep_str: str) -> PackageDependency:
        """Parse a dependency string like 'package@^1.2.0'"""
        if '@' in dep_str:
            name, version_spec = dep_str.split('@', 1)
            return PackageDependency(name.strip(), version_spec.strip())
        else:
            return PackageDependency(dep_str.strip(), "*")
    
    def _fallback_parse(self, content: str) -> Optional[BringPackage]:
        """Fallback parser when bring_parser is not available"""
        print(f"{Colors.WARNING}⚠️  Using fallback parser (limited functionality){Colors.RESET}")
        
        # Very basic regex-based parsing for essential fields
        import re
        
        # Extract package name
        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        name = name_match.group(1) if name_match else "unknown-package"
        
        # Extract version
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        version = version_match.group(1) if version_match else "1.0.0"
        
        # Extract description
        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
        description = desc_match.group(1) if desc_match else ""
        
        # Extract dependencies (very basic)
        dependencies = []
        dep_section = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if dep_section:
            dep_content = dep_section.group(1)
            # Find quoted strings
            dep_matches = re.findall(r'["\']([^"\']+)["\']', dep_content)
            for dep_str in dep_matches:
                dependencies.append(self._parse_dependency_string(dep_str))
        
        return BringPackage(
            name=name,
            version=version,
            description=description,
            dependencies=dependencies,
            dev_dependencies=[],  # Not parsed in fallback mode
        )

class BringFileValidator:
    """Validator for bring file content"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, package: BringPackage) -> bool:
        """Validate a bring package definition"""
        self.errors = []
        self.warnings = []
        
        # Required fields
        if not package.name:
            self.errors.append("Package name is required")
        elif not re.match(r'^[a-zA-Z0-9_-]+$', package.name):
            self.errors.append("Package name contains invalid characters")
        
        if not package.version:
            self.errors.append("Package version is required")
        elif not self._is_valid_version(package.version):
            self.errors.append("Invalid version format")
        
        # Optional field validation
        if package.author and '@' not in package.author:
            self.warnings.append("Author should include email address")
        
        if package.repository and not (package.repository.startswith('http') or package.repository.startswith('git')):
            self.warnings.append("Repository URL should be a valid URL")
        
        # Dependency validation
        for dep in package.dependencies + package.dev_dependencies:
            if not self._is_valid_dependency(dep):
                self.errors.append(f"Invalid dependency: {dep}")
        
        return len(self.errors) == 0
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version follows semantic versioning"""
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9-]+)?$'
        return bool(re.match(pattern, version))
    
    def _is_valid_dependency(self, dep: PackageDependency) -> bool:
        """Check if dependency specification is valid"""
        if not dep.name:
            return False
        
        if dep.version_spec != "*" and not self._is_valid_version(dep.version_spec):
            return False
        
        return True
    
    def print_results(self):
        """Print validation results"""
        if self.errors:
            print(f"{Colors.ERROR}❌ Validation Errors:{Colors.RESET}")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"{Colors.WARNING}⚠️  Warnings:{Colors.RESET}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if not self.errors and not self.warnings:
            print(f"{Colors.SUCCESS}✅ Bring file is valid{Colors.RESET}")

def create_sample_bring_file(file_path: Path):
    """Create a sample .bring file"""
    sample_content = '''# package.bring
package = {
    name = "my-project"
    version = "1.0.0"
    description = "My awesome EL project"
    author = "Your Name <your.email@example.com>"
    license = "MIT"
    
    dependencies = [
        "json-parser@^1.2.0"
        "logger@~2.1.0"
        "crypto@>=1.0.0"
    ]
    
    dev_dependencies = [
        "test-framework@^1.0.0"
        "benchmark-tools@^0.5.0"
    ]
    
    repository = "https://github.com/username/my-project"
    homepage = "https://username.github.io/my-project"
}
'''
    
    try:
        file_path.write_text(sample_content, encoding='utf-8')
        print(f"{Colors.SUCCESS}✅ Sample .bring file created: {file_path}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.ERROR}❌ Error creating sample file: {e}{Colors.RESET}")

if __name__ == "__main__":
    # Test the parser
    parser = BringFileParser()
    validator = BringFileValidator()
    
    # Create sample file
    sample_file = Path("sample.bring")
    create_sample_bring_file(sample_file)
    
    # Test parsing
    package = parser.parse_file(sample_file)
    if package:
        print(f"{Colors.SUCCESS}✅ Parsed package:{Colors.RESET}")
        print(f"   Name: {package.name}")
        print(f"   Version: {package.version}")
        print(f"   Dependencies: {len(package.dependencies)}")
        
        # Validate
        if validator.validate(package):
            validator.print_results()
        else:
            validator.print_results()
