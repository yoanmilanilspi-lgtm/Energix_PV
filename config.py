import os
import subprocess
import sys
import pkg_resources

# --- GESTION DES DÉPENDANCES ---
dependencies = [
    "flask==3.1.0", "numpy==2.2.2", "pandas==2.2.3", "scikit-learn==1.5.2", 
    "plotly==5.24.1", "gunicorn==23.0.0", "Jinja2==3.1.5"
]

def check_and_install(package):
    try:
        pkg_resources.get_distribution(package.split('==')[0])
    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except Exception as e:
            print(f"⚠️ Erreur installation {package}: {e}")

for dep in dependencies: 
    check_and_install(dep)

# --- CLASSE DE CONFIGURATION ---

class Config:
    # --- CONFIGURATION FLASK ---
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-2026')
    DEBUG = True
    
    # --- PARAMÈTRES TECHNIQUES PANNEAU 500W ---
    PMAX = 500
    VMP = 37.47
    IMP = 13.34
    ISC = 14.31
    VOC = 43.58
    EFFICIENCY = 22.61
    SURFACE_PV = 2.21  # m²
    
    # --- PARAMÈTRES COMMERCIAUX ---
    PRIX_POSE_UNITAIRE = 1733  # Tarif de référence par panneau
    
    # --- UTILITAIRE POUR LES VISUALISATIONS ---
    # Ce dictionnaire permet de passer toutes les infos d'un coup à courbe_iv_pv
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

print("🚀 Config Flask et dépendances prêtes !")