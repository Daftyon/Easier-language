#!/usr/bin/env python3
"""
Build script for El Programming Language
Creates a distributable executable
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from requests import *
from bring_parser import *
def run_command(cmd, cwd=None):
    """Execute a system command"""
    print(f"🔧 Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    if result.stdout.strip():
        print(f"📝 {result.stdout}")
    return True

def check_dependencies():
    """Check that dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    dependencies = ['pyinstaller', 'requests', 'compiler', 'utils', 'system','bring_parser']
    optional_dependencies = ['PIL']  # Pillow for icon handling
    missing = []
    missing_optional = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} installed")
        except ImportError:
            missing.append(dep)
            print(f"❌ {dep} missing")
    
    for dep in optional_dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} (Pillow) installed")
        except ImportError:
            missing_optional.append('pillow')
            print(f"⚠️  {dep} (Pillow) missing - needed for icon support")
    
    if missing:
        print(f"\n📦 Installing missing dependencies...")
        for dep in missing:
            if not run_command(f"pip install {dep}"):
                print(f"Unable to install {dep}")
                return False
    
    if missing_optional:
        print(f"\n📦 Installing optional dependencies for icon support...")
        for dep in missing_optional:
            if not run_command(f"pip install {dep}"):
                print(f"⚠️  Unable to install {dep} - will build without icon")
    
    return True

def clean_build():
    """Clean old builds"""
    print("🧹 Cleaning old builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️  Removed: {dir_name}")
    
    # Clean .pyc files recursively
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def create_examples():
    """Create example files"""
    print("📝 Creating example files...")
    
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    # Hello World
    hello_world = """program hello_world {
    show "Hello, World!";
    show "Welcome to El Programming Language!";
}"""
    
    # Calculator
    calculator = """program calculator {
    function add(a: integer, b: integer): integer {
        return a + b;
    }
    
    function multiply(a: integer, b: integer): integer {
        return a * b;
    }
    
    var x: integer = 10;
    var y: integer = 5;
    
    show "El Calculator";
    show x + " + " + y + " = " + add(x, y);
    show x + " * " + y + " = " + multiply(x, y);
}"""
    
    # Fibonacci
    fibonacci = """program fibonacci {
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
}"""
    axiomatic_method="""

ALGORITHM testfix {
    theorem simple: true;
        definition even: true;                    // x is even if x mod 2 = 0 (simplified)

        axiom identity: true === true;
 axiom excludedmiddle: true or ! true;
    proof simple {
        hypothesis h1: false;
        test t1: h1: realistic;
        realistic;
        QED;
    }
    
    SHOW("Fixed!");
}"""
    # Write examples
    examples = {
        "hello_world.el": hello_world,
        "calculator.el": calculator,
        "fibonacci.el": fibonacci,
        "axiomatic_method.el":axiomatic_method,
    }
    
    for filename, content in examples.items():
        with open(examples_dir / filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: examples/{filename}")

def build_executable():
    """Build executable with PyInstaller"""
    print("🏗️  Building executable...")
    
    system = platform.system().lower()
    
    # Check if icon exists and is valid
    icon_path = Path("el_icone.ico")
    icon_option = []
    
    if icon_path.exists():
        try:
            # Try to verify if Pillow is available for icon processing
            import PIL
            icon_option = ["--icon", str(icon_path)]
            print(f"✅ Using icon: {icon_path}")
        except ImportError:
            print("⚠️  Pillow not available - building without icon")
            print("   Run 'pip install pillow' to enable icon support")
    else:
        print("⚠️  Icon file 'el_icone.ico' not found, building without icon")

    # PyInstaller command adapted to system
    base_cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "el",
        "--console",
        "--add-data", "compiler;compiler" if system == "windows" else "compiler:compiler",
        "--add-data", "utils;utils" if system == "windows" else "utils:utils", 
        "--add-data", "system;system" if system == "windows" else "system:system",
        "--add-data", "examples;examples" if system == "windows" else "examples:examples",
        "--hidden-import", "compiler",
        "--hidden-import", "utils", 
        "--hidden-import", "system",
        "el_standalone.py"
    ]
    
    # Add icon if available
    base_cmd.extend(icon_option)
    
    cmd = " ".join(base_cmd)
    
    # Try building with icon first, fallback without icon if it fails
    if icon_option:
        print("🔧 Attempting build with icon...")
        if run_command(cmd):
            return True
        else:
            print("⚠️  Build with icon failed, retrying without icon...")
            # Remove icon option and try again
            base_cmd = [arg for arg in base_cmd if not arg.startswith("--icon") and not arg.endswith(".ico")]
            cmd = " ".join(base_cmd)
    
    return run_command(cmd)

def create_portable_package():
    """Create portable package"""
    print("📦 Creating portable package...")
    
    # Create portable folder
    portable_dir = Path("dist/el-portable")
    portable_dir.mkdir(exist_ok=True)
    
    # Determine executable name
    exe_name = "el.exe" if platform.system().lower() == "windows" else "el"
    exe_path = Path("dist") / exe_name
    
    if exe_path.exists():
        # Copy executable
        shutil.copy(exe_path, portable_dir)
        print(f"✅ Copied: {exe_name}")
        
        # Copy examples
        if Path("examples").exists():
            shutil.copytree("examples", portable_dir / "examples", dirs_exist_ok=True)
            print("✅ Copied: examples/")
        
        # Create README
        readme_content = f"""# El Programming Language - Portable Version v1.0.0

## 🚀 Installation
1. Extract this folder anywhere on your computer
2. (Optional) Add the folder to your PATH variable
3. Use {exe_name} from the command line

## 📖 Usage

### Basic commands:
- `{exe_name} --help`              : Show help
- `{exe_name} --version`           : Show version
- `{exe_name} file.el`             : Execute an El file
- `{exe_name} -i`                  : Interactive mode (REPL)
- `{exe_name} -c "code"`           : Execute code directly

### Examples:
```bash
# Execute an example
{exe_name} examples/hello_world.el

# Interactive mode
{exe_name} -i

# Command line code
{exe_name} -c "program test {{ show 'Hello El!'; }}"
```

## 📝 El Language Syntax

### Variables:
```el
var name: string = "El";
var age: integer = 1;
var price: float = 19.99;
var active: boolean = true;
```

### Functions:
```el
function greet(name: string): string {{
    return "Hello " + name + "!";
}}
```

### Loops:
```el
for i: integer = 0; i < 5; i = i + 1 {{
    show i;
}}

while condition do {{
    // code
}}
```

### Conditions:
```el
if x > 5 {{
    show "x is large";
}} elif x === 5 {{
    show "x equals 5";
}} else {{
    show "x is small";
}}
```

## 📚 Included Examples
- `hello_world.el` : "Hello World" program
- `calculator.el`  : Simple calculator
- `fibonacci.el`   : Fibonacci sequence

## 🌐 Documentation and Support
- GitHub: https://github.com/Daftyon/Easier-language
- Documentation: https://el-language.org
- Issues: https://github.com/Daftyon/Easier-language/issues

## 📄 License
El Programming Language is distributed under the MIT license.

---
Created with ❤️ by the El Language team
"""
        
        with open(portable_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("✅ Created: README.txt")
        
        # Create launch script (Windows)
        if platform.system().lower() == "windows":
            batch_content = f"""@echo off
echo El Programming Language - Portable
echo Type 'el --help' for help
echo.
cmd /k
"""
            with open(portable_dir / "el-console.bat", "w") as f:
                f.write(batch_content)
            print("✅ Created: el-console.bat")
        
        # Create portable ZIP
        print("🗜️  Creating ZIP archive...")
        zip_name = f"el-portable-{platform.system().lower()}-{platform.machine().lower()}"
        shutil.make_archive(f"dist/{zip_name}", "zip", "dist", "el-portable")
        print(f"✅ Archive created: dist/{zip_name}.zip")
        
        return True
    else:
        print(f"❌ Executable not found: {exe_path}")
        return False

def create_installer_script():
    """Create Windows installation script"""
    if platform.system().lower() != "windows":
        return True
    
    print("📋 Creating Windows installation script...")
    
    install_script = """@echo off
echo ================================
echo   El Programming Language
echo   Windows Installation
echo ================================
echo.

REM Check administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Administrator privileges required for system installation
    echo Installing to user directory...
    set "INSTALL_DIR=%USERPROFILE%\\El"
) else (
    set "INSTALL_DIR=C:\\Program Files\\El"
)

echo Installing to: %INSTALL_DIR%
echo.

REM Create directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
copy "el.exe" "%INSTALL_DIR%\\" >nul
xcopy "examples" "%INSTALL_DIR%\\examples\\" /E /I /Q >nul
copy "README.txt" "%INSTALL_DIR%\\" >nul

REM Add to user PATH
echo Adding to PATH...
setx PATH "%PATH%;%INSTALL_DIR%" >nul

echo.
echo ================================
echo   Installation Complete!
echo ================================
echo.
echo El is now installed in: %INSTALL_DIR%
echo Restart your command prompt and type 'el --version'
echo.
pause
"""
    
    with open("dist/install-windows.bat", "w") as f:
        f.write(install_script)
    print("✅ Created: install-windows.bat")
    
    return True

def show_build_summary():
    """Show build summary"""
    print("\n" + "="*50)
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("="*50)
    
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("\n📦 Files created:")
        total_size = 0
        
        for file_path in sorted(dist_dir.rglob("*")):
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                size_mb = size / 1024 / 1024
                
                # Emoji by file type
                if file_path.suffix == ".exe":
                    emoji = "⚡"
                elif file_path.suffix == ".zip":
                    emoji = "📦"
                elif file_path.suffix == ".bat":
                    emoji = "🔧"
                else:
                    emoji = "📄"
                
                print(f"  {emoji} {file_path.name} ({size_mb:.1f} MB)")
        
        print(f"\n📊 Total size: {total_size / 1024 / 1024:.1f} MB")
    
    print(f"\n🖥️  Platform: {platform.system()} {platform.machine()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    print("\n🚀 Ready for distribution!")
    print("   - Test executable: dist/el.exe --version")
    print("   - Distribute the portable ZIP")
    print("   - Share with your users!")

def main():
    """Main function"""
    print("🏗️  BUILDING EL PROGRAMMING LANGUAGE")
    print("="*50)
    
    # Preliminary checks
    if not check_dependencies():
        print("❌ Cannot continue without dependencies")
        return 1
    
    # Clean
    clean_build()
    
    # Create examples
    create_examples()
    
    # Build executable
    if not build_executable():
        print("❌ Failed to build executable")
        return 1
    
    # Create portable package
    if not create_portable_package():
        print("❌ Failed to create portable package")
        return 1
    
    # Create installation script
    create_installer_script()
    
    # Show summary
    show_build_summary()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
