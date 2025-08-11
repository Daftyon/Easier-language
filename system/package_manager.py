import requests
import json
import tarfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import os
import io

try:
    from bring_parser import parse_bring_string, BringParseError
except ImportError:
    print("Warning: bring-parser not installed. Using fallback parser.")
    # Fallback simple parser for basic functionality
    def parse_bring_string(content: str) -> Dict[str, Any]:
        return {"content": content, "parsed": False}
    
    class BringParseError(Exception):
        pass

class GitHubTarPackageManager:
    """Enhanced package manager for GitHub tar packages"""
    
    def __init__(self, github_repo_url: str = "https://github.com/Daftyon/Easier-Hub", 
                 packages_path: str = "easier-packages"):
        """
        Initialize package manager
        
        Args:
            github_repo_url: Base GitHub repository URL
            packages_path: Path within repo where packages are stored
        """
        self.github_repo_url = github_repo_url.rstrip('/')
        self.packages_path = packages_path
        self.cache_dir = Path.home() / ".easier_lang" / "packages"
        self.extracted_dir = Path.home() / ".easier_lang" / "extracted"
        
        # Create directories if they don't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        
        self.loaded_packages = {}
        
        # Convert GitHub URL to raw content URL
        if "github.com" in self.github_repo_url:
            self.raw_base_url = self.github_repo_url.replace("github.com", "raw.githubusercontent.com")
            if not self.raw_base_url.endswith("/master"):
                self.raw_base_url += "/master"
        else:
            self.raw_base_url = self.github_repo_url
    
    def fetch_package(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Fetch package tar file from GitHub and process it"""
        try:
            # Check cache first
            extracted_package_dir = self.extracted_dir / package_name
            if extracted_package_dir.exists():
                print(f"Loading cached package '{package_name}'")
                return self.load_from_extracted_cache(package_name)
            
            # Construct tar file URL
            tar_filename = f"{package_name}.tar"
            tar_url = f"{self.raw_base_url}/{self.packages_path}/{tar_filename}"
            
            print(f"Fetching from: {tar_url}")
            
            # Download tar file
            response = requests.get(tar_url, timeout=30)
            
            if response.status_code == 200:
                # Save tar file to cache
                cache_tar_file = self.cache_dir / tar_filename
                cache_tar_file.write_bytes(response.content)
                
                # Extract tar file
                extracted_content = self.extract_tar_package(cache_tar_file, package_name)
                
                if extracted_content:
                    return {
                        'name': package_name,
                        'content': extracted_content,
                        'version': extracted_content.get('version', '1.0.0'),
                        'source': 'github-tar',
                        'cached': False
                    }
                else:
                    print(f"Failed to process tar content for package '{package_name}'")
                    return None
            
            elif response.status_code == 404:
                print(f"Package '{package_name}' not found at {tar_url}")
                return None
            else:
                print(f"Failed to fetch package '{package_name}': HTTP {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"Network error fetching package '{package_name}': {e}")
            return None
        except Exception as e:
            print(f"Error processing package '{package_name}': {e}")
            return None
    
    def extract_tar_package(self, tar_file_path: Path, package_name: str) -> Optional[Dict[str, Any]]:
        """Extract tar file and process contents"""
        try:
            # Create extraction directory for this package
            extract_dir = self.extracted_dir / package_name
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir(parents=True)
            
            # Extract tar file
            with tarfile.open(tar_file_path, 'r') as tar:
                # Security check: ensure all members are safe
                def is_safe_path(member_path):
                    return not (member_path.startswith('/') or 
                              '..' in member_path or 
                              member_path.startswith('~'))
                
                safe_members = []
                for member in tar.getmembers():
                    if is_safe_path(member.name):
                        safe_members.append(member)
                    else:
                        print(f"Skipping unsafe tar member: {member.name}")
                
                # Extract safe members
                tar.extractall(path=extract_dir, members=safe_members)
            
            print(f"Extracted {len(safe_members)} files to {extract_dir}")
            
            # Process extracted content
            return self.process_extracted_content(extract_dir, package_name)
            
        except tarfile.TarError as e:
            print(f"Error extracting tar file: {e}")
            return None
        except Exception as e:
            print(f"Error processing extracted content: {e}")
            return None
    
    def process_extracted_content(self, extract_dir: Path, package_name: str) -> Dict[str, Any]:
        """Process extracted package content"""
        content = {}
        metadata = {
            'name': package_name,
            'version': '1.0.0',
            'description': f'Package {package_name}',
            'files': []
        }
        
        try:
            # Look for package metadata file
            metadata_files = ['package.json', 'metadata.json', 'info.json']
            for metadata_file in metadata_files:
                metadata_path = extract_dir / metadata_file
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            file_metadata = json.load(f)
                            metadata.update(file_metadata)
                        break
                    except json.JSONDecodeError:
                        continue
            
            # Process all files in the extracted directory
            for file_path in extract_dir.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(extract_dir)
                    metadata['files'].append(str(relative_path))
                    
                    # Process different file types
                    if file_path.suffix == '.el':
                        # EL source files
                        content[f"el:{relative_path.stem}"] = file_path.read_text(encoding='utf-8')
                    
                    elif file_path.suffix == '.bring':
                        # Bring definition files
                        bring_content = file_path.read_text(encoding='utf-8')
                        try:
                            parsed = parse_bring_string(bring_content)
                            content[f"bring:{relative_path.stem}"] = parsed
                        except BringParseError:
                            content[f"bring:{relative_path.stem}"] = bring_content
                    
                    elif file_path.suffix == '.json':
                        # JSON configuration files
                        try:
                            json_content = json.loads(file_path.read_text(encoding='utf-8'))
                            content[f"json:{relative_path.stem}"] = json_content
                        except json.JSONDecodeError:
                            content[f"text:{relative_path.stem}"] = file_path.read_text(encoding='utf-8')
                    
                    elif file_path.suffix in ['.txt', '.md']:
                        # Text files
                        content[f"text:{relative_path.stem}"] = file_path.read_text(encoding='utf-8')
                    
                    else:
                        # Binary or other files - store path reference
                        content[f"file:{relative_path.stem}"] = str(file_path)
            
            # Store processed content for caching
            cache_file = extract_dir / 'processed_content.json'
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': metadata,
                    'content': content,
                    'timestamp': str(extract_dir.stat().st_mtime)
                }, f, indent=2, default=str)
            
            return {
                'metadata': metadata,
                'content': content,
                'version': metadata.get('version', '1.0.0')
            }
            
        except Exception as e:
            print(f"Error processing extracted content: {e}")
            # Return basic content even if processing fails
            return {
                'metadata': metadata,
                'content': {'error': str(e)},
                'version': '1.0.0'
            }
    
    def load_from_extracted_cache(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Load package from extracted cache"""
        try:
            cache_file = self.extracted_dir / package_name / 'processed_content.json'
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # Add cache indicator
                cached_data['cached'] = True
                cached_data['name'] = package_name
                cached_data['source'] = 'github-tar-cached'
                
                return cached_data
            
            # If no processed cache, try to reprocess
            extract_dir = self.extracted_dir / package_name
            if extract_dir.exists():
                processed_content = self.process_extracted_content(extract_dir, package_name)
                processed_content['cached'] = True
                processed_content['name'] = package_name
                return processed_content
            
            return None
            
        except Exception as e:
            print(f"Failed to load cached package '{package_name}': {e}")
            return None
    
    def list_cached_packages(self) -> list:
        """List all cached packages"""
        cached = []
        
        # List tar files in cache
        for tar_file in self.cache_dir.glob("*.tar"):
            cached.append(f"tar:{tar_file.stem}")
        
        # List extracted packages
        for extract_dir in self.extracted_dir.iterdir():
            if extract_dir.is_dir():
                cached.append(f"extracted:{extract_dir.name}")
        
        return cached
    
    def clear_cache(self):
        """Clear package cache"""
        try:
            # Clear tar cache
            for tar_file in self.cache_dir.glob("*.tar"):
                tar_file.unlink()
            
            # Clear extracted cache
            if self.extracted_dir.exists():
                shutil.rmtree(self.extracted_dir)
                self.extracted_dir.mkdir(parents=True)
            
            print("Package cache cleared successfully")
        except Exception as e:
            print(f"Error clearing cache: {e}")
    
    def get_package_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a cached package"""
        try:
            extract_dir = self.extracted_dir / package_name
            if not extract_dir.exists():
                return None
            
            cache_file = extract_dir / 'processed_content.json'
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('metadata', {})
            
            return None
        except Exception as e:
            print(f"Error getting package info: {e}")
            return None


# Backwards compatibility - use the new manager as default
class EasierHubPackageManager(GitHubTarPackageManager):
    """Backwards compatible package manager"""
    
    def __init__(self):
        super().__init__(
            github_repo_url="https://github.com/Daftyon/Easier-Hub",
            packages_path="easier-packages"
        )


if __name__ == "__main__":
    # Test the package manager
    pm = EasierHubPackageManager()
    
    print("Testing package manager...")
    print("Attempting to fetch 'variables_demo' package...")
    
    result = pm.fetch_package("variables_demo")
    if result:
        print(f"Successfully loaded package: {result['name']}")
        print(f"Version: {result.get('version', 'unknown')}")
        print(f"Files: {len(result.get('content', {}).get('metadata', {}).get('files', []))}")
    else:
        print("Failed to load package")
