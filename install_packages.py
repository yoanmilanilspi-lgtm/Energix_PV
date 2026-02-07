import os
import subprocess
import sys
from pathlib import Path

def read_requirements(file_path="requirements.txt"):
    """Lit requirements.txt et retourne la liste des packages."""
    requirements_path = Path(file_path)
    if not requirements_path.exists():
        print(f"❌ {file_path} introuvable !")
        return []
    
    packages = []
    with open(requirements_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Ignore commentaires/vides
                # Prend nom package (avant == ou espaces)
                package = line.split('==')[0].split('>')[0].split('<')[0].split(' ')[0]
                packages.append(package)
    return packages

def check_and_install(package):
    """Vérifie si package installé, sinon installe."""
    try:
        __import__(package.replace('-', '_'))  # plotly → plotly
        print(f"✔️ '{package}' déjà installé")
        return True
    except ImportError:
        print(f"⚠️ '{package}' manquant → Installation...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ '{package}' installé !")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur installation {package}: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Installation automatique Calculatrice 4")
    
    # Lit requirements.txt optimisé
    dependencies = read_requirements("requirements.txt")
    print(f"📦 {len(dependencies)} packages à vérifier...")
    
    success_count = 0
    for package in dependencies:
        if check_and_install(package):
            success_count += 1
    
    print(f"\n🎉 {success_count}/{len(dependencies)} packages OK !")
    print("🔥 Lancez: python routes.py")
