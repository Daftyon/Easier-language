@echo off
REM Script de construction rapide pour El Language
echo ================================
echo   El Language - Construction
echo ================================

REM Vérifier Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERREUR: Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

echo ✅ Python détecté

REM Installer PyInstaller si nécessaire
echo 📦 Installation de PyInstaller...
pip install pyinstaller

REM Créer les fichiers nécessaires si ils n'existent pas
if not exist "el_standalone.py" (
    echo ❌ Fichier el_standalone.py manquant
    echo Créez d'abord ce fichier avec le code fourni
    pause
    exit /b 1
)

REM Nettoyer les anciens builds
echo 🧹 Nettoyage...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Créer le dossier examples
if not exist "examples" mkdir "examples"

REM Créer hello_world.el
echo program hello_world { > examples\hello_world.el
echo     show "Hello, World!"; >> examples\hello_world.el
echo     show "Bienvenue dans El Programming Language!"; >> examples\hello_world.el
echo } >> examples\hello_world.el

echo ✅ Exemple créé: examples\hello_world.el

REM Construire l'exécutable
echo 🏗️  Construction de l'exécutable...
pyinstaller --onefile --name el --console --add-data "compiler;compiler" --add-data "utils;utils" --add-data "system;system" --add-data "examples;examples" el_standalone.py

if exist "dist\el.exe" (
    echo ✅ Construction réussie!
    echo.
    echo 📦 Fichiers créés:
    dir /b dist\
    echo.
    echo 🚀 Test de l'exécutable:
    echo.
    dist\el.exe --version
    echo.
    echo ✅ El Language est prêt!
    echo    - Exécutable: dist\el.exe
    echo    - Test: dist\el.exe examples\hello_world.el
    echo    - REPL: dist\el.exe -i
) else (
    echo ❌ Échec de la construction
)

echo.
echo Appuyez sur une touche pour continuer...
pause >nul
