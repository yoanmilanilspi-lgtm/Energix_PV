@echo off
set "PROJECT_PATH=%~dp0"
cd /d "%PROJECT_PATH%"

title Serveur Austral Solar - Calculatrice PV

echo -----------------------------------------------------
echo 🔍 Verification de l'environnement Austral Solar...
echo -----------------------------------------------------

:: 1. Verification de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH.
    pause
    exit
)

:: 2. Activation de l'environnement virtuel
if exist "venv\Scripts\activate.bat" (
    echo [1/3] Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
) else (
    echo [ERREUR] Dossier venv introuvable. Verifiez l'installation.
    pause
    exit
)

:: 3. Installation des dependances (Rapide si deja installees)
echo [2/3] Verification des bibliotheques (Calculs PV, Plotly, Flask)...
pip install -r requirements.txt --quiet

:: 4. Lancement du serveur (Ajusté sur routes.py)
echo [3/3] Demarrage du moteur de calcul (routes.py)...
:: On lance sans le /b pour que vous puissiez voir les erreurs Flask dans la console si besoin
start "AustralSolarServer" python routes.py

:: 5. Ouverture du navigateur
echo 🚀 Preparation de l'interface...
timeout /t 5 >nul
start "" "http://127.0.0.1:5000"

echo -----------------------------------------------------
echo ✅ L'application est en cours d'execution sur http://127.0.0.1:5000
echo 💡 Gardez cette fenetre ouverte tant que vous utilisez l'outil.
echo -----------------------------------------------------
pause