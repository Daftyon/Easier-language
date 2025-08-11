import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from bring_parser import parse_bring_string, BringParseError
except ImportError:
    print("Warning: bring-parser not installed. Run: pip install bring-parser")
    # Fallback simple parser for basic functionality
    def parse_bring_string(content: str) -> Dict[str, Any]:
        return {"error": "bring-parser not available"}
    
    class BringParseError(Exception):
        pass

class EasierHubPackageManager:
    """Package manager for Easier Hub integration"""
    
    def __init__(self, hub_url: str = "https://easier-hub.vercel.app"):
        self.hub_url = hub_url
        self.cache_dir = Path.home() / ".easier_lang" / "packages"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_packages = {}
    
    def fetch_package(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Fetch package from Easier Hub"""
        try:
            # Try cache first
            cache_file = self.cache_dir / f"{package_name}.bring"
            if cache_file.exists():
                return self.load_from_cache(cache_file)
            
            # Fetch from hub
            url = f"{self.hub_url}/api/packages/{package_name}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                package_data = response.json()
                
                # Save to cache
                bring_content = package_data.get('content', '')
                cache_file.write_text(bring_content, encoding='utf-8')
                
                # Parse bring content
                parsed_content = parse_bring_string(bring_content)
                return {
                    'name': package_name,
                    'metadata': package_data.get('metadata', {}),
                    'content': parsed_content,
                    'version': package_data.get('version', '1.0.0')
                }
            else:
                print(f"Package '{package_name}' not found on Easier Hub")
                return None
                
        except requests.RequestException as e:
            print(f"Failed to fetch package '{package_name}': {e}")
            return None
        except BringParseError as e:
            print(f"Failed to parse package '{package_name}': {e}")
            return None
    
    def load_from_cache(self, cache_file: Path) -> Optional[Dict[str, Any]]:
        """Load package from local cache"""
        try:
            content = cache_file.read_text(encoding='utf-8')
            parsed_content = parse_bring_string(content)
            return {
                'name': cache_file.stem,
                'content': parsed_content,
                'cached': True
            }
        except Exception as e:
            print(f"Failed to load cached package: {e}")
            return None
    
    def list_cached_packages(self) -> list:
        """List all cached packages"""
        cached = []
        for file in self.cache_dir.glob("*.bring"):
            cached.append(file.stem)
        return cached
    
    def clear_cache(self):
        """Clear package cache"""
        for file in self.cache_dir.glob("*.bring"):
            file.unlink()
        print("Package cache cleared")
