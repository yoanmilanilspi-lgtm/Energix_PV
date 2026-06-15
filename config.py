import os
import subprocess
import sys
import importlib.metadata

# --- GESTION DES DÉPENDANCES ---
dependencies = [
    "flask==3.1.0", "numpy==2.2.2", "pandas==2.2.3", "scikit-learn==1.5.2",
    "plotly==5.24.1", "gunicorn==23.0.0", "Jinja2==3.1.5"
]

def check_and_install(package):
    pkg_name = package.split("==")[0]
    try:
        # Vérifie si le package est installé
        importlib.metadata.version(pkg_name)
    except importlib.metadata.PackageNotFoundError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except Exception as e:
            print(f"⚠️ Erreur installation {package}: {e}")

for dep in dependencies:
    check_and_install(dep)

# --- CLASSE DE CONFIGURATION ---

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-2026')
    DEBUG = True

    PMAX = 500
    VMP = 37.47
    IMP = 13.34
    ISC = 14.31
    VOC = 43.58
    EFFICIENCY = 22.61
    SURFACE_PV = 2.21

    PRIX_POSE_UNITAIRE = 1733

    @property
    def PANNEAU_DATA(self):
        return {
            'PMAX': self.PMAX,
            'VMP': self.VMP,
            'IMP': self.IMP,
            'ISC': self.ISC,
            'VOC': self.VOC,
            'EFFICIENCY': self.EFFICIENCY,
            'SURFACE_PV': self.SURFACE_PV
        }

print("✨ Config Flask et dépendances prêtes !")
