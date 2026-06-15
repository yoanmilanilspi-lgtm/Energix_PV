@echo off

:: Chemin du projet
set "PROJECT_PATH=%~dp0"
cd /d "%PROJECT_PATH%"

title Serveur Energix_PV

echo -----------------------------------------------------
echo [+] Lancement du serveur Energix_PV
echo -----------------------------------------------------

:: 1. Vérification Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe.
    pause
    exit /b
)

:: 2. Ouverture du navigateur AVANT le lancement du serveur
echo [+] Ouverture de l'interface web...
start "" "http://127.0.0.1:5000"

:: 3. Lancement du serveur Flask dans CETTE fenêtre
echo [+] Demarrage du serveur Flask (routes.py)...
python routes.py

echo -----------------------------------------------------
echo  Serveur en cours d'execution
echo -----------------------------------------------------
pause
