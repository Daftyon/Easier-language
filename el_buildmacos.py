#!/usr/bin/env python3
"""
El Programming Language - Universal Build Script
Works on Windows, macOS, and Linux
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

__version__ = "1.0.9"

def run_command(cmd, cwd=None):
    """Execute a command and return success status"""
    print(f"🔧 Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            shell=isinstance(cmd, str),
            cwd=cwd
        )
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        if result.stdout.strip():
            print(f"📄 {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False

def detect_platform():
    """Detect current platform and return config"""
    system = platform.system().lower()
    
    configs = {
        'windows': {
            'name': 'Windows',
            'executable': 'el.exe',
            'icon_format': 'ico',
            'data_separator': ';',
            'pyinstaller_extra': []
        },
        'darwin': {
            'name': 'macOS',
            'executable': 'el',
            'icon_format': 'icns',
            'data_separator': ':',
            'pyinstaller_extra': ['--onedir']  # Better for macOS
        },
        'linux': {
            'name': 'Linux',
            'executable': 'el',
            'icon_format': 'png',
            'data_separator': ':',
            'pyinstaller_extra': []
        }
    }
    
    config = configs.get(system)
    if not config:
        print(f"❌ Unsupported platform: {system}")
        return None
    
    config['system'] = system
    config['arch'] = platform.machine().lower()
    
    return config

def check_dependencies():
    """Check build dependencies"""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    
    # Check PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller available")
    except ImportError:
        print("📦 Installing PyInstaller...")
        if not run_command([sys.executable, "-m", "pip", "install", "pyinstaller"]):
            return False
    
    # Check El modules
    required_modules = ['compiler', 'utils', 'system']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} module found")
        except ImportError:
            print(f"❌ {module} module not found")
            print("   Make sure you're in the El project root directory")
            return False
    
    # Check main script
    if not Path("el_standalone.py").exists():
        print("❌ el_standalone.py not found")
        return False
    
    print("✅ All dependencies satisfied")
    return True

def clean_build():
    """Clean old build artifacts"""
    print("🧹 Cleaning old build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ Removed: {dir_name}")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def create_examples():
    """Create platform-appropriate example files"""
    print("📝 Creating example files...")
    
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    config = detect_platform()
    platform_name = config['name'] if config else "Unknown"
    
    examples = {
        "hello_world.el": f'''program hello_world {{
    show "Hello, World!";
    show "Welcome to El Programming Language on {platform_name}!";
    
    var platform: string = "{platform_name}";
    show "Running on: " + platform;
}}''',
        
        "calculator.el": '''program calculator {
    function add(a: integer, b: integer): integer {
        return a + b;
    }
    
    function multiply(a: integer, b: integer): integer {
        return a * b;
    }
    
    function factorial(n: integer): integer {
        if n <= 1 {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    var x: integer = 10;
    var y: integer = 5;
    
    show "El Calculator";
    show x + " + " + y + " = " + add(x, y);
    show x + " * " + y + " = " + multiply(x, y);
    show "Factorial of " + y + " = " + factorial(y);
}''',
        
        "fibonacci.el": '''program fibonacci {
    function fib(n: integer): integer {
        if n <= 1 {
            return n;
        }
        return fib(n - 1) + fib(n - 2);
    }
    
    show "Fibonacci Sequence:";
    for i: integer = 0; i < 10; i = i + 1 {
        show "F(" + i + ") = " + fib(i);
    }
}''',
        
        "proof_demo.el": '''ALGORITHM proof_demo {
    // Mathematical proof demonstration
    axiom identity: true === true;
    axiom excluded_middle: true or ! true;
    
    theorem simple_theorem: true;
    
    proof simple_theorem {
        hypothesis h1: true;
        test verify_h1: h1: true;
        // The theorem follows from the hypothesis
        QED;
    }
    
    show "Proof system demonstration complete!";
}''',
        
        "graphics_demo.el": '''program graphics_demo {
    show "Graphics demonstration starting...";
    
    // Set colors
    color("blue");
    bgcolor("white");
    
    // Draw a square
    show "Drawing a square...";
    for i: integer = 0; i < 4; i = i + 1 {
        forward(100);
        right(90);
    }
    
    // Move to new position
    penup();
    goto(150, 0);
    pendown();
    
    // Draw a triangle
    show "Drawing a triangle...";
    color("red");
    for i: integer = 0; i < 3; i = i + 1 {
        forward(100);
        right(120);
    }
    
    // Draw a circle
    penup();
    goto(-50, -50);
    pendown();
    color("green");
    circle(30);
    
    show "Graphics demonstration complete!";
}'''
    }
    
    for filename, content in examples.items():
        with open(examples_dir / filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: examples/{filename}")

def find_icon(config):
    """Find appropriate icon file"""
    format_type = config['icon_format']
    icon_candidates = [
        f"el_icone.{format_type}",
        f"el.{format_type}",
        f"icon.{format_type}"
    ]
    
    for icon_path in icon_candidates:
        if Path(icon_path).exists():
            print(f"🎨 Found icon: {icon_path}")
            return icon_path
    
    print(f"⚠️ No {format_type} icon found")
    return None

def build_executable(config):
    """Build executable using PyInstaller"""
    print(f"🔨 Building executable for {config['name']}...")
    
    # Base PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--name", config['executable'].replace('.exe', ''),  # Remove .exe for PyInstaller
    ]
    
    # Add platform-specific options
    if config['system'] == 'darwin':
        cmd.append("--onedir")  # macOS works better with onedir
    else:
        cmd.append("--onefile")  # Windows and Linux use onefile
    
    cmd.extend(config['pyinstaller_extra'])
    cmd.append("--console")
    
    # Add data directories
    data_separator = config['data_separator']
    data_dirs = [
        f"compiler{data_separator}compiler",
        f"utils{data_separator}utils",
        f"system{data_separator}system",
        f"examples{data_separator}examples"
    ]
    
    for data_dir in data_dirs:
        cmd.extend(["--add-data", data_dir])
    
    # Add hidden imports
    for module in ["compiler", "utils", "system"]:
        cmd.extend(["--hidden-import", module])
    
    # Add icon if available
    icon_path = find_icon(config)
    if icon_path:
        cmd.extend(["--icon", icon_path])
    
    # Add main script
    cmd.append("el_standalone.py")
    
    print(f"🔧 Command: {' '.join(cmd)}")
    return run_command(cmd)

def test_executable(config):
    """Test the built executable"""
    print(f"🧪 Testing executable...")
    
    if config['system'] == 'darwin' and Path("dist/el").is_dir():
        # macOS onedir build
        exe_path = Path("dist/el/el")
    else:
        # Windows onefile or Linux onefile
        exe_path = Path("dist") / config['executable']
    
    if not exe_path.exists():
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    # Make executable on Unix systems
    if config['system'] in ['darwin', 'linux']:
        os.chmod(exe_path, 0o755)
    
    # Test version command
    if run_command([str(exe_path), "--version"]):
        print("✅ Executable test passed!")
        return True
    else:
        print("❌ Executable test failed!")
        return False

def create_portable_package(config):
    """Create portable distribution package"""
    print(f"📦 Creating portable package for {config['name']}...")
    
    # Determine source executable path
    if config['system'] == 'darwin' and Path("dist/el").is_dir():
        source_exe = Path("dist/el")
        is_app_bundle = True
    else:
        source_exe = Path("dist") / config['executable']
        is_app_bundle = False
    
    if not source_exe.exists():
        print(f"❌ Source executable not found: {source_exe}")
        return False
    
    # Create portable directory
    portable_name = f"el-portable-{config['system']}-{config['arch']}"
    portable_dir = Path("dist") / portable_name
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    if is_app_bundle:
        shutil.copytree(source_exe, portable_dir / "el", dirs_exist_ok=True)
    else:
        shutil.copy(source_exe, portable_dir)
    
    print(f"✅ Copied executable")
    
    # Copy examples
    if Path("examples").exists():
        shutil.copytree("examples", portable_dir / "examples", dirs_exist_ok=True)
        print("✅ Copied examples")
    
    # Create README
    create_readme(portable_dir, config)
    
    # Create launcher scripts
    create_launchers(portable_dir, config)
    
    # Create ZIP archive
    create_zip(portable_dir, config)
    
    return True

def create_readme(portable_dir, config):
    """Create README file"""
    exe_name = config['executable']
    if config['system'] == 'darwin' and Path(portable_dir / "el").is_dir():
        exe_path = "./el/el"
    else:
        exe_path = f"./{exe_name}"
    
    readme_content = f"""# El Programming Language - Portable {config['name']} Edition

## 🚀 Quick Start

### Running El
```bash
# Execute an El file
{exe_path} hello_world.el

# Interactive mode (REPL)
{exe_path} -i

# Execute code directly
{exe_path} -c "program test {{ show 'Hello {config['name']}!'; }}"

# Show help
{exe_path} --help
```

### Examples
Try the included examples:
```bash
{exe_path} examples/hello_world.el
{exe_path} examples/calculator.el
{exe_path} examples/fibonacci.el
{exe_path} examples/proof_demo.el
{exe_path} examples/graphics_demo.el
```

## 📝 El Language Syntax

### Basic Program Structure
```el
program my_program {{
    // Your code here
    show "Hello, World!";
}}
```

### Variables and Types
```el
var name: string = "El";
var age: integer = 1;
var price: float = 19.99;
var active: boolean = true;
```

### Functions
```el
function greet(name: string): string {{
    return "Hello " + name + "!";
}}
```

### Control Flow
```el
// Conditional statements
if x > 5 {{
    show "x is large";
}} elif x === 5 {{
    show "x equals 5";
}} else {{
    show "x is small";
}}

// Loops
for i: integer = 0; i < 5; i = i + 1 {{
    show i;
}}

while condition do {{
    // loop body
}}
```

### Mathematical Proofs
```el
axiom identity: true === true;

theorem simple: true;

proof simple {{
    hypothesis h1: true;
    // proof steps
    QED;
}}
```

### Graphics (Turtle Graphics)
```el
// Drawing commands
forward(100);
right(90);
circle(50);
color("red");
```

## 🔧 Advanced Usage

### Package Management
```bash
# Download packages
{exe_path} download

# Create sample package.bring file
{exe_path} download --sample

# Manage package cache
{exe_path} package cache list
{exe_path} package cache clear
```

### Command Line Options
- `--version` : Show version information
- `--debug` : Enable debug mode with detailed output
- `-i, --interactive` : Start interactive REPL mode
- `-c, --code CODE` : Execute code directly
- `--banner` : Show El language banner

## 🌐 More Information

- **GitHub**: https://github.com/Daftyon/Easier-language
- **Documentation**: https://el-language.org
- **Issues**: https://github.com/Daftyon/Easier-language/issues

## 📄 System Information

- **Platform**: {config['name']} ({config['arch']})
- **Version**: {__version__}
- **Build Date**: Generated with El Universal Builder

---
Created with ❤️ by the El Language Team
"""
    
    with open(portable_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ Created README.md")

def create_launchers(portable_dir, config):
    """Create platform-specific launcher scripts"""
    
    if config['system'] == 'windows':
        # Windows batch file
        batch_content = f"""@echo off
title El Programming Language
echo.
echo El Programming Language v{__version__}
echo Type 'el --help' for help
echo.
echo Adding El to PATH for this session...
set PATH=%~dp0;%PATH%
echo.
cmd /k
"""
        with open(portable_dir / "el-console.bat", "w") as f:
            f.write(batch_content)
        print("✅ Created el-console.bat")
        
    elif config['system'] in ['darwin', 'linux']:
        # Unix shell script
        exe_path = "./el/el" if Path(portable_dir / "el").is_dir() else "./el"
        
        shell_content = f"""#!/bin/bash
# El Programming Language Launcher

echo "El Programming Language v{__version__}"
echo "Type '{exe_path} --help' for help"
echo ""

# Make executable if needed
chmod +x {exe_path}

# Add current directory to PATH
export PATH="$PWD:$PATH"

# Start interactive shell
exec bash
"""
        launcher_path = portable_dir / "el-console.sh"
        with open(launcher_path, "w") as f:
            f.write(shell_content)
        os.chmod(launcher_path, 0o755)
        print("✅ Created el-console.sh")

def create_zip(portable_dir, config):
    """Create ZIP archive"""
    print("🗜️ Creating ZIP archive...")
    
    zip_name = f"el-portable-{config['system']}-{config['arch']}-v{__version__}"
    
    # Create ZIP
    shutil.make_archive(
        str(Path("dist") / zip_name),
        "zip",
        str(portable_dir.parent),
        portable_dir.name
    )
    
    zip_path = Path("dist") / f"{zip_name}.zip"
    if zip_path.exists():
        size_mb = zip_path.stat().st_size / 1024 / 1024
        print(f"✅ Created: {zip_name}.zip ({size_mb:.1f} MB)")
        return True
    
    return False

def show_summary(config):
    """Show build summary"""
    print("\n" + "="*60)
    print(f"🎉 BUILD COMPLETED FOR {config['name'].upper()}!")
    print("="*60)
    
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("\n📦 Generated files:")
        total_size = 0
        
        for item in sorted(dist_dir.iterdir()):
            if item.is_file():
                size = item.stat().st_size
                total_size += size
                size_mb = size / 1024 / 1024
                
                if item.suffix == ".zip":
                    emoji = "📦"
                elif item.name == config['executable']:
                    emoji = "⚡"
                else:
                    emoji = "📄"
                
                print(f"  {emoji} {item.name} ({size_mb:.1f} MB)")
            elif item.is_dir():
                # Count files in directory
                file_count = len(list(item.rglob("*")))
                print(f"  📁 {item.name}/ ({file_count} files)")
        
        print(f"\n📊 Total size: {total_size / 1024 / 1024:.1f} MB")
    
    print(f"\n🖥️ Platform: {config['name']} {config['arch']}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    print(f"\n🚀 Ready for distribution!")
    
    # Platform-specific test commands
    if config['system'] == 'darwin' and Path("dist/el").is_dir():
        test_cmd = "./dist/el/el --version"
    else:
        test_cmd = f"./dist/{config['executable']} --version"
    
    print(f"  - Test: {test_cmd}")
    print(f"  - Distribute: dist/el-portable-{config['system']}-{config['arch']}-v{__version__}.zip")

def main():
    """Main build function"""
    parser = argparse.ArgumentParser(description='El Programming Language Universal Builder')
    parser.add_argument('--clean', action='store_true', help='Clean build before starting')
    parser.add_argument('--no-test', action='store_true', help='Skip testing executable')
    parser.add_argument('--no-package', action='store_true', help='Skip creating portable package')
    
    args = parser.parse_args()
    
    print("🌍 EL PROGRAMMING LANGUAGE - UNIVERSAL BUILDER")
    print("="*60)
    
    # Detect platform
    config = detect_platform()
    if not config:
        return 1
    
    print(f"🖥️ Building for: {config['name']} ({config['arch']})")
    
    try:
        # Check dependencies
        if not check_dependencies():
            return 1
        
        # Clean if requested
        if args.clean:
            clean_build()
        
        # Create examples
        create_examples()
        
        # Build executable
        if not build_executable(config):
            print("❌ Build failed!")
            return 1
        
        print("✅ Build successful!")
        
        # Test executable
        if not args.no_test:
            if not test_executable(config):
                print("⚠️ Executable test failed, but continuing...")
        
        # Create portable package
        if not args.no_package:
            if create_portable_package(config):
                print("✅ Portable package created!")
            else:
                print("⚠️ Failed to create portable package")
        
        # Show summary
        show_summary(config)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Build interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())