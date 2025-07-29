#!/usr/bin/env python3
"""
Script de construction pour El Programming Language
Crée un exécutable distributable
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Exécuter une commande système"""
    print(f"🔧 Exécution: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Erreur: {result.stderr}")
        return False
    if result.stdout.strip():
        print(f"📝 {result.stdout}")
    return True

def check_dependencies():
    """Vérifier que les dépendances sont installées"""
    print("🔍 Vérification des dépendances...")
    
    dependencies = ['pyinstaller']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} installé")
        except ImportError:
            missing.append(dep)
            print(f"❌ {dep} manquant")
    
    if missing:
        print(f"\n📦 Installation des dépendances manquantes...")
        for dep in missing:
            if not run_command(f"pip install {dep}"):
                print(f"Impossible d'installer {dep}")
                return False
    
    return True

def clean_build():
    """Nettoyer les anciens builds"""
    print("🧹 Nettoyage des anciens builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️  Supprimé: {dir_name}")
    
    # Nettoyer les fichiers .pyc récursivement
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def create_examples():
    """Créer des fichiers d'exemple"""
    print("📝 Création des fichiers d'exemple...")
    
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    # Hello World
    hello_world = """program hello_world {
    show "Hello, World!";
    show "Bienvenue dans El Programming Language!";
}"""
    
    # Calculatrice
    calculator = """program calculator {
    function add(a: integer, b: integer): integer {
        return a + b;
    }
    
    function multiply(a: integer, b: integer): integer {
        return a * b;
    }
    
    var x: integer = 10;
    var y: integer = 5;
    
    show "Calculatrice El";
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
    
    show "Séquence de Fibonacci:";
    for i: integer = 0; i < 10; i = i + 1 {
        show "F(" + i + ") = " + fib(i);
    }
}"""
    
    # Écrire les exemples
    examples = {
        "hello_world.el": hello_world,
        "calculator.el": calculator,
        "fibonacci.el": fibonacci
    }
    
    for filename, content in examples.items():
        with open(examples_dir / filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Créé: examples/{filename}")

def build_executable():
    """Construire l'exécutable avec PyInstaller"""
    print("🏗️  Construction de l'exécutable...")
    
    system = platform.system().lower()
    
    # Commande PyInstaller adaptée au système
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
    
    cmd = " ".join(base_cmd)
    return run_command(cmd)

def create_portable_package():
    """Créer un package portable"""
    print("📦 Création du package portable...")
    
    # Créer le dossier portable
    portable_dir = Path("dist/el-portable")
    portable_dir.mkdir(exist_ok=True)
    
    # Déterminer le nom de l'exécutable
    exe_name = "el.exe" if platform.system().lower() == "windows" else "el"
    exe_path = Path("dist") / exe_name
    
    if exe_path.exists():
        # Copier l'exécutable
        shutil.copy(exe_path, portable_dir)
        print(f"✅ Copié: {exe_name}")
        
        # Copier les exemples
        if Path("examples").exists():
            shutil.copytree("examples", portable_dir / "examples", dirs_exist_ok=True)
            print("✅ Copié: examples/")
        
        # Créer le README
        readme_content = f"""# El Programming Language - Version Portable v1.0.0

## 🚀 Installation
1. Extrayez ce dossier où vous voulez sur votre ordinateur
2. (Optionnel) Ajoutez le dossier à votre variable PATH
3. Utilisez {exe_name} depuis la ligne de commande

## 📖 Utilisation

### Commandes de base:
- `{exe_name} --help`              : Afficher l'aide
- `{exe_name} --version`           : Afficher la version
- `{exe_name} fichier.el`          : Exécuter un fichier El
- `{exe_name} -i`                  : Mode interactif (REPL)
- `{exe_name} -c "code"`           : Exécuter du code directement

### Exemples:
```bash
# Exécuter un exemple
{exe_name} examples/hello_world.el

# Mode interactif
{exe_name} -i

# Code en ligne de commande
{exe_name} -c "program test {{ show 'Hello El!'; }}"
```

## 📝 Syntaxe El Language

### Variables:
```el
var nom: string = "El";
var age: integer = 1;
var prix: float = 19.99;
var actif: boolean = true;
```

### Fonctions:
```el
function saluer(nom: string): string {{
    return "Bonjour " + nom + "!";
}}
```

### Boucles:
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
    show "x est grand";
}} elif x === 5 {{
    show "x égale 5";
}} else {{
    show "x est petit";
}}
```

## 📚 Exemples inclus
- `hello_world.el` : Programme "Hello World"
- `calculator.el`  : Calculatrice simple
- `fibonacci.el`   : Séquence de Fibonacci

## 🌐 Documentation et Support
- GitHub:https://github.com/Daftyon/Easier-language
- Documentation: https://el-language.org
- Issues:https://github.com/Daftyon/Easier-language/issues

## 📄 Licence
El Programming Language est distribué sous licence MIT.

---
Créé avec ❤️ par l'équipe El Language
"""
        
        with open(portable_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("✅ Créé: README.txt")
        
        # Créer le script de lancement (Windows)
        if platform.system().lower() == "windows":
            batch_content = f"""@echo off
echo El Programming Language - Portable
echo Tapez 'el --help' pour l'aide
echo.
cmd /k
"""
            with open(portable_dir / "el-console.bat", "w") as f:
                f.write(batch_content)
            print("✅ Créé: el-console.bat")
        
        # Créer le ZIP portable
        print("🗜️  Création de l'archive ZIP...")
        zip_name = f"el-portable-{platform.system().lower()}-{platform.machine().lower()}"
        shutil.make_archive(f"dist/{zip_name}", "zip", "dist", "el-portable")
        print(f"✅ Archive créée: dist/{zip_name}.zip")
        
        return True
    else:
        print(f"❌ Exécutable non trouvé: {exe_path}")
        return False

def create_installer_script():
    """Créer un script d'installation pour Windows"""
    if platform.system().lower() != "windows":
        return True
    
    print("📋 Création du script d'installation Windows...")
    
    install_script = """@echo off
echo ================================
echo   El Programming Language
echo   Installation Windows
echo ================================
echo.

REM Vérifier les privilèges administrateur
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ATTENTION: Privilèges administrateur requis pour installation système
    echo Installation dans le répertoire utilisateur...
    set "INSTALL_DIR=%USERPROFILE%\\El"
) else (
    set "INSTALL_DIR=C:\\Program Files\\El"
)

echo Installation vers: %INSTALL_DIR%
echo.

REM Créer le répertoire
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copier les fichiers
copy "el.exe" "%INSTALL_DIR%\\" >nul
xcopy "examples" "%INSTALL_DIR%\\examples\\" /E /I /Q >nul
copy "README.txt" "%INSTALL_DIR%\\" >nul

REM Ajouter au PATH utilisateur
echo Ajout au PATH...
setx PATH "%PATH%;%INSTALL_DIR%" >nul

echo.
echo ================================
echo   Installation terminée!
echo ================================
echo.
echo El est maintenant installé dans: %INSTALL_DIR%
echo Redémarrez votre invite de commande et tapez 'el --version'
echo.
pause
"""
    
    with open("dist/install-windows.bat", "w") as f:
        f.write(install_script)
    print("✅ Créé: install-windows.bat")
    
    return True

def show_build_summary():
    """Afficher un résumé de la construction"""
    print("\n" + "="*50)
    print("🎉 CONSTRUCTION TERMINÉE AVEC SUCCÈS!")
    print("="*50)
    
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("\n📦 Fichiers créés:")
        total_size = 0
        
        for file_path in sorted(dist_dir.rglob("*")):
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                size_mb = size / 1024 / 1024
                
                # Emoji selon le type de fichier
                if file_path.suffix == ".exe":
                    emoji = "⚡"
                elif file_path.suffix == ".zip":
                    emoji = "📦"
                elif file_path.suffix == ".bat":
                    emoji = "🔧"
                else:
                    emoji = "📄"
                
                print(f"  {emoji} {file_path.name} ({size_mb:.1f} MB)")
        
        print(f"\n📊 Taille totale: {total_size / 1024 / 1024:.1f} MB")
    
    print(f"\n🖥️  Plateforme: {platform.system()} {platform.machine()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    print("\n🚀 Prêt pour distribution!")
    print("   - Testez l'exécutable: dist/el.exe --version")
    print("   - Distribuez le ZIP portable")
    print("   - Partagez avec vos utilisateurs!")

def main():
    """Fonction principale"""
    print("🏗️  CONSTRUCTION D'EL PROGRAMMING LANGUAGE")
    print("="*50)
    
    # Vérifications préliminaires
    if not check_dependencies():
        print("❌ Impossible de continuer sans les dépendances")
        return 1
    
    # Nettoyer
    clean_build()
    
    # Créer les exemples
    create_examples()
    
    # Construire l'exécutable
    if not build_executable():
        print("❌ Échec de la construction de l'exécutable")
        return 1
    
    # Créer le package portable
    if not create_portable_package():
        print("❌ Échec de la création du package portable")
        return 1
    
    # Créer le script d'installation
    create_installer_script()
    
    # Afficher le résumé
    show_build_summary()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Construction interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
