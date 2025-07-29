#!/usr/bin/env python3
"""
Construction directe d'El Language avec PyInstaller via Python
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess

def create_examples():
    """Créer les fichiers d'exemple"""
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
    
    var x: integer = 10;
    var y: integer = 5;
    
    show "Calculatrice El";
    show x + " + " + y + " = " + add(x, y);
}"""
    
    # Fibonacci
    fibonacci = """program fibonacci {
    function fib(n: integer): integer {
        if n <= 1 {
            return n;
        }
        return fib(n - 1) + fib(n - 2);
    }
    
    show "Fibonacci: " + fib(7);
}"""
    
    examples = {
        "hello_world.el": hello_world,
        "calculator.el": calculator,
        "fibonacci.el": fibonacci
    }
    
    for filename, content in examples.items():
        with open(examples_dir / filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Créé: {filename}")

def clean_build():
    """Nettoyer les anciens builds"""
    print("🧹 Nettoyage...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ Supprimé: {dir_name}")

def build_with_python():
    """Construire avec python -m PyInstaller"""
    print("🏗️ Construction de l'exécutable...")
    
    # Vérifier que el_standalone.py existe
    if not Path("el_standalone.py").exists():
        print("❌ Fichier el_standalone.py manquant!")
        print("Créez d'abord ce fichier avec le code fourni.")
        return False
    
    # Commande PyInstaller via Python
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "el",
        "--console",
        "--add-data", "compiler;compiler",
        "--add-data", "utils;utils", 
        "--add-data", "system;system",
        "--add-data", "examples;examples",
        "--hidden-import", "compiler",
        "--hidden-import", "utils",
        "--hidden-import", "system",
        "el_standalone.py"
    ]
    
    print("🔧 Exécution de PyInstaller...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Construction réussie!")
            return True
        else:
            print("❌ Erreur lors de la construction:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_executable():
    """Tester l'exécutable créé"""
    exe_path = Path("dist/el.exe")
    if exe_path.exists():
        print("🧪 Test de l'exécutable...")
        
        try:
            # Test version
            result = subprocess.run([str(exe_path), "--version"], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Test version réussi!")
                print(result.stdout)
            else:
                print("❌ Test version échoué")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
    else:
        print("❌ Exécutable non trouvé")

def create_readme():
    """Créer un README pour la distribution"""
    readme_content = """# El Programming Language v1.0.0

## 🚀 Utilisation

### Commandes de base:
- `el.exe --version`           : Afficher la version
- `el.exe --help`              : Afficher l'aide
- `el.exe fichier.el`          : Exécuter un fichier El
- `el.exe -i`                  : Mode interactif (REPL)
- `el.exe -c "code"`           : Exécuter du code directement

### Exemples:
```bash
# Exécuter un exemple
el.exe examples\\hello_world.el

# Mode interactif
el.exe -i

# Code direct
el.exe -c "program test { show 'Hello El!'; }"
```

## 📝 Syntaxe El

```el
program mon_programme {
    var nom: string = "El";
    var age: integer = 1;
    
    show "Bonjour " + nom + "!";
    
    function saluer(nom: string): string {
        return "Salut " + nom + "!";
    }
    
    show saluer("Développeur");
}
```

## 📚 Exemples inclus
- `hello_world.el` : Programme Hello World
- `calculator.el`  : Calculatrice simple  
- `fibonacci.el`   : Suite de Fibonacci

Créé par l'équipe El Language
"""
    
    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ README créé")

def main():
    """Fonction principale"""
    print("🚀 CONSTRUCTION EL LANGUAGE")
    print("=" * 40)
    
    # Nettoyer
    clean_build()
    
    # Créer les exemples
    create_examples()
    
    # Construire
    if build_with_python():
        # Tester
        test_executable()
        
        # Créer README
        create_readme()
        
        # Résumé
        print("\n🎉 CONSTRUCTION TERMINÉE!")
        print("=" * 40)
        
        dist_dir = Path("dist")
        if dist_dir.exists():
            print("📦 Fichiers créés:")
            for file_path in dist_dir.iterdir():
                if file_path.is_file():
                    size = file_path.stat().st_size / 1024 / 1024
                    print(f"  📄 {file_path.name} ({size:.1f} MB)")
        
        print("\n✅ El Language est prêt!")
        print("   - Exécutable: dist\\el.exe")
        print("   - Test: dist\\el.exe --version")
        print("   - Exemples: dist\\el.exe examples\\hello_world.el")
        
        return True
    else:
        print("❌ Échec de la construction")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Construction interrompue")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
