import requests
import json
import tarfile
import tempfile
import shutil
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import os
import io
import sys

try:
    from bring_parser import parse_bring_string, BringParseError
except ImportError:
    print("Warning: bring-parser not installed. Using fallback parser.")
    def parse_bring_string(content: str) -> Dict[str, Any]:
        return {"content": content, "parsed": False}
    
    class BringParseError(Exception):
        pass

class ProgressBar:
    """Simple progress bar for download progress"""
    
    def __init__(self, total_size: int, description: str = "Downloading", width: int = 50):
        self.total_size = total_size
        self.description = description
        self.width = width
        self.downloaded = 0
        self.start_time = time.time()
        
    def update(self, chunk_size: int):
        """Update progress bar with new chunk size"""
        self.downloaded += chunk_size
        self._display_progress()
    
    def _display_progress(self):
        """Display the progress bar"""
        if self.total_size > 0:
            percentage = (self.downloaded / self.total_size) * 100
            filled_width = int(self.width * self.downloaded // self.total_size)
        else:
            percentage = 0
            filled_width = 0
        
        bar = '█' * filled_width + '░' * (self.width - filled_width)
        
        # Calculate speed
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            speed = self.downloaded / elapsed_time
            speed_str = self._format_bytes(speed) + "/s"
        else:
            speed_str = "calculating..."
        
        # Format sizes
        downloaded_str = self._format_bytes(self.downloaded)
        total_str = self._format_bytes(self.total_size) if self.total_size > 0 else "unknown"
        
        # Clear line and print progress
        sys.stdout.write('\r')
        sys.stdout.write(f"\033[K")  # Clear line
        progress_line = (f"{self.description}: [{bar}] {percentage:.1f}% "
                        f"({downloaded_str}/{total_str}) {speed_str}")
        sys.stdout.write(progress_line)
        sys.stdout.flush()
        
        if self.downloaded >= self.total_size and self.total_size > 0:
            sys.stdout.write('\n')
            sys.stdout.flush()
    
    def _format_bytes(self, bytes_value: float) -> str:
        """Format bytes into human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}TB"
    
    def complete(self):
        """Mark progress as complete"""
        if self.total_size > 0:
            self.downloaded = self.total_size
        self._display_progress()

class SpinnerProgress:
    """Spinning progress indicator for indeterminate progress"""
    
    def __init__(self, description: str = "Processing"):
        self.description = description
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.current_char = 0
        self.is_spinning = False
        self.thread = None
        
    def start(self):
        """Start the spinner"""
        self.is_spinning = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, final_message: str = None):
        """Stop the spinner"""
        self.is_spinning = False
        if self.thread:
            self.thread.join()
        
        # Clear the spinner line
        sys.stdout.write('\r')
        sys.stdout.write('\033[K')
        if final_message:
            sys.stdout.write(final_message + '\n')
        sys.stdout.flush()
    
    def _spin(self):
        """Internal spinning method"""
        while self.is_spinning:
            char = self.spinner_chars[self.current_char % len(self.spinner_chars)]
            sys.stdout.write(f'\r{char} {self.description}...')
            sys.stdout.flush()
            self.current_char += 1
            time.sleep(0.1)

class GitHubTarPackageManager:
    """Enhanced package manager with download progress for GitHub tar packages"""
    
    def __init__(self, github_repo_url: str = "https://github.com/Daftyon/Easier-Hub", 
                 packages_path: str = "easier-packages",
                 show_progress: bool = True):
        """
        Initialize package manager with progress support
        
        Args:
            github_repo_url: Base GitHub repository URL
            packages_path: Path within repo where packages are stored
            show_progress: Whether to show download progress
        """
        self.github_repo_url = github_repo_url.rstrip('/')
        self.packages_path = packages_path
        self.show_progress = show_progress
        self.cache_dir = Path.home() / "EL" / "packages"
        self.extracted_dir = Path.home() / "EL" / "extracted"
        
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
        """Fetch package tar file from GitHub with progress indication"""
        try:
            # Check cache first
            extracted_package_dir = self.extracted_dir / package_name
            if extracted_package_dir.exists():
                if self.show_progress:
                    print(f"📦 Loading cached package '{package_name}'...")
                return self.load_from_extracted_cache(package_name)
            
            # Construct tar file URL
            tar_filename = f"{package_name}.tar"
            tar_url = f"{self.raw_base_url}/{self.packages_path}/{tar_filename}"
            
            if self.show_progress:
                print(f"🌐 Connecting to: {tar_url}")
            
            # Download tar file with progress
            downloaded_content = self._download_with_progress(tar_url, package_name)
            
            if downloaded_content is None:
                return None
            
            # Save tar file to cache
            cache_tar_file = self.cache_dir / tar_filename
            cache_tar_file.write_bytes(downloaded_content)
            
            if self.show_progress:
                print(f"💾 Saved to cache: {cache_tar_file}")
            
            # Extract and process tar file
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
                print(f"❌ Failed to process tar content for package '{package_name}'")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Network error fetching package '{package_name}': {e}")
            return None
        except Exception as e:
            print(f"❌ Error processing package '{package_name}': {e}")
            return None
    
    def _download_with_progress(self, url: str, package_name: str) -> Optional[bytes]:
        """Download file with progress bar"""
        try:
            # First, get the file size
            head_response = requests.head(url, timeout=10)
            
            if head_response.status_code == 404:
                print(f"❌ Package '{package_name}' not found at {url}")
                return None
            elif head_response.status_code != 200:
                print(f"❌ Failed to fetch package '{package_name}': HTTP {head_response.status_code}")
                return None
            
            # Get file size
            total_size = int(head_response.headers.get('content-length', 0))
            
            # Start download with progress
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            if self.show_progress and total_size > 0:
                progress_bar = ProgressBar(
                    total_size, 
                    description=f"📥 Downloading {package_name}.tar"
                )
            elif self.show_progress:
                # Use spinner for unknown size
                spinner = SpinnerProgress(f"📥 Downloading {package_name}.tar")
                spinner.start()
            
            # Download in chunks
            downloaded_data = bytearray()
            chunk_size = 8192  # 8KB chunks
            
            try:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive chunks
                        downloaded_data.extend(chunk)
                        if self.show_progress and total_size > 0:
                            progress_bar.update(len(chunk))
                
                # Complete progress indication
                if self.show_progress:
                    if total_size > 0:
                        progress_bar.complete()
                        print(f"✅ Download complete! ({progress_bar._format_bytes(len(downloaded_data))})")
                    else:
                        spinner.stop(f"✅ Download complete! ({len(downloaded_data)} bytes)")
                
                return bytes(downloaded_data)
                
            except Exception as e:
                if self.show_progress:
                    if total_size > 0:
                        print(f"\n❌ Download failed: {e}")
                    else:
                        spinner.stop(f"❌ Download failed: {e}")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            return None
    
    def extract_tar_package(self, tar_file_path: Path, package_name: str) -> Optional[Dict[str, Any]]:
        """Extract tar file with progress indication"""
        try:
            if self.show_progress:
                spinner = SpinnerProgress(f"📂 Extracting {package_name}")
                spinner.start()
            
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
                        if self.show_progress:
                            spinner.stop()
                        print(f"⚠️  Skipping unsafe tar member: {member.name}")
                        if self.show_progress:
                            spinner.start()
                
                # Extract safe members
                tar.extractall(path=extract_dir, members=safe_members)
            
            if self.show_progress:
                spinner.stop(f"✅ Extracted {len(safe_members)} files to cache")
            
            # Process extracted content
            return self.process_extracted_content(extract_dir, package_name)
            
        except tarfile.TarError as e:
            if self.show_progress:
                if 'spinner' in locals():
                    spinner.stop(f"❌ Error extracting tar file: {e}")
                else:
                    print(f"❌ Error extracting tar file: {e}")
            return None
        except Exception as e:
            if self.show_progress:
                if 'spinner' in locals():
                    spinner.stop(f"❌ Error processing extracted content: {e}")
                else:
                    print(f"❌ Error processing extracted content: {e}")
            return None
    
    def process_extracted_content(self, extract_dir: Path, package_name: str) -> Dict[str, Any]:
        """Process extracted package content with progress indication"""
        content = {}
        metadata = {
            'name': package_name,
            'version': '1.0.0',
            'description': f'Package {package_name}',
            'files': []
        }
        
        try:
            if self.show_progress:
                spinner = SpinnerProgress(f"⚙️  Processing {package_name} content")
                spinner.start()
            
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
            
            # Get all files for processing
            all_files = list(extract_dir.rglob('*'))
            file_count = len([f for f in all_files if f.is_file()])
            
            if self.show_progress:
                spinner.stop(f"📁 Processing {file_count} files...")
            
            # Process all files in the extracted directory
            processed_count = 0
            for file_path in all_files:
                if file_path.is_file():
                    relative_path = file_path.relative_to(extract_dir)
                    metadata['files'].append(str(relative_path))
                    
                    # Show progress for large packages
                    processed_count += 1
                    if self.show_progress and file_count > 10 and processed_count % 5 == 0:
                        print(f"  📄 Processing... {processed_count}/{file_count} files")
                    
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
                    
                    elif file_path.suffix in ['.txt', '.md', '.rst']:
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
            
            if self.show_progress:
                print(f"✅ Package processing complete! {len(content)} items available")
            
            return {
                'metadata': metadata,
                'content': content,
                'version': metadata.get('version', '1.0.0')
            }
            
        except Exception as e:
            if self.show_progress:
                if 'spinner' in locals():
                    spinner.stop(f"❌ Error processing content: {e}")
                else:
                    print(f"❌ Error processing extracted content: {e}")
            
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
                
                if self.show_progress:
                    content_count = len(cached_data.get('content', {}))
                    print(f"✅ Loaded from cache! {content_count} items available")
                
                return cached_data
            
            # If no processed cache, try to reprocess
            extract_dir = self.extracted_dir / package_name
            if extract_dir.exists():
                if self.show_progress:
                    print(f"🔄 Reprocessing cached extraction...")
                processed_content = self.process_extracted_content(extract_dir, package_name)
                processed_content['cached'] = True
                processed_content['name'] = package_name
                return processed_content
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to load cached package '{package_name}': {e}")
            return None
    
    def list_cached_packages(self) -> list:
        """List all cached packages with status"""
        cached = []
        
        # List tar files in cache
        for tar_file in self.cache_dir.glob("*.tar"):
            size = tar_file.stat().st_size
            size_str = ProgressBar(0, "")._format_bytes(size)
            cached.append(f"tar:{tar_file.stem} ({size_str})")
        
        # List extracted packages
        for extract_dir in self.extracted_dir.iterdir():
            if extract_dir.is_dir():
                # Count files in extracted directory
                file_count = len(list(extract_dir.rglob('*')))
                cached.append(f"extracted:{extract_dir.name} ({file_count} files)")
        
        return cached
    
    def clear_cache(self, show_progress: bool = None):
        """Clear package cache with progress indication"""
        if show_progress is None:
            show_progress = self.show_progress
            
        try:
            if show_progress:
                spinner = SpinnerProgress("🗑️  Clearing package cache")
                spinner.start()
            
            # Clear tar cache
            tar_count = 0
            for tar_file in self.cache_dir.glob("*.tar"):
                tar_file.unlink()
                tar_count += 1
            
            # Clear extracted cache
            extract_count = 0
            if self.extracted_dir.exists():
                for extract_dir in self.extracted_dir.iterdir():
                    if extract_dir.is_dir():
                        shutil.rmtree(extract_dir)
                        extract_count += 1
            
            if show_progress:
                spinner.stop(f"✅ Cache cleared! Removed {tar_count} tar files and {extract_count} extracted packages")
            else:
                print(f"Package cache cleared: {tar_count} tar files, {extract_count} extracted packages")
                
        except Exception as e:
            if show_progress and 'spinner' in locals():
                spinner.stop(f"❌ Error clearing cache: {e}")
            else:
                print(f"❌ Error clearing cache: {e}")
    
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
            print(f"❌ Error getting package info: {e}")
            return None


# Backwards compatibility - use the new manager as default
class EasierHubPackageManager(GitHubTarPackageManager):
    """Backwards compatible package manager with progress support"""
    
    def __init__(self, show_progress: bool = True):
        super().__init__(
            github_repo_url="https://github.com/Daftyon/Easier-Hub",
            packages_path="easier-packages",
            show_progress=show_progress
        )


if __name__ == "__main__":
    # Test the enhanced package manager with progress
    pm = EasierHubPackageManager(show_progress=True)
    
    print("🚀 Testing Enhanced Package Manager with Progress")
    print("=" * 60)
    
    # Test listing cache
    print("\n📋 Current cache status:")
    cached = pm.list_cached_packages()
    if cached:
        for package in cached:
            print(f"  • {package}")
    else:
        print("  No cached packages")
    
    # Test downloading a package
    print(f"\n🎯 Testing package download:")
    result = pm.fetch_package("variables_demo")
    
    if result:
        print(f"\n📊 Package Summary:")
        print(f"   Name: {result['name']}")
        print(f"   Version: {result.get('version', 'unknown')}")
        print(f"   Source: {result.get('source', 'unknown')}")
        print(f"   Items: {len(result.get('content', {}))}")
    else:
        print("\n❌ Package download failed")