import math
from functools import lru_cache
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

def safe_float(value, default=0.0):
    """Convertit en float de manière sécurisée pour éviter les crashs sur formulaires vides."""
    try:
        if value is None or str(value).strip() == "":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Convertit en int de manière sécurisée."""
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(float(value)) # Gère aussi le cas "1.0"
    except (ValueError, TypeError):
        return default

@lru_cache(maxsize=32) # ✅ Correction ici : max_iter remplacé par maxsize
def estimer_consommation(nb_occupants):
    """
    Calcule la consommation mensuelle moyenne (kWh/mois).
    Utilise LRU Cache pour mémoriser les résultats fréquents.
    """
    nb_occupants = max(0, safe_int(nb_occupants))
    
    if nb_occupants < 1:
        return 0.0
    
    if nb_occupants == 1:
        # Moyenne réunionnaise pour une personne seule
        return (120 + 300) / 2
    
    elif nb_occupants == 4:
        # Moyenne pour une famille standard
        return (350 + 550) / 2
    
    else:
        # Estimation linéaire pour les autres cas
        consommation_par_personne = 140.0
        return consommation_par_personne * nb_occupants

def calculer_facteur_orientation(inclinaison, orientation):
    """
    Calcule le rendement selon la position des panneaux.
    Optimisé pour l'hémisphère Sud (La Réunion).
    """
    # Pénalité si on s'éloigne du Nord (0°)
    orientation_penalty = max(0, abs(orientation) - 30) * 0.003
    # Pénalité si on s'éloigne de l'inclinaison idéale (22°)
    inclinaison_penalty = max(0, abs(inclinaison - 22)) * 0.005
    
    facteur = 1 - orientation_penalty - inclinaison_penalty
    return max(0.85, min(1.0, facteur))

def obtenir_nb_panneaux(puissance_kwc, pmax_panneau=500):
    """Calcule le nombre de panneaux physiques nécessaires."""
    if puissance_kwc <= 0:
        return 0
    return math.ceil((puissance_kwc * 1000) / pmax_panneau)
    
def snapper_puissance_catalogue(p_theorique):
    """
    Règle Austral Solar : Convertit la puissance théorique en paliers réels.
    Exemple : 4.6 kWc -> 6 kWc
    """
    paliers = [3, 6, 9, 12, 15, 18]
    if p_theorique <= 3.0: return 3
    
    for i in range(len(paliers) - 1):
        p_actuel = paliers[i]
        p_suivant = paliers[i+1]
        # Seuil de bascule à +1 kWc après le palier
        if p_theorique <= (p_actuel + 1.0):
            return p_actuel
        elif p_theorique < p_suivant:
            return p_suivant
    return paliers[-1]
    

def histogramme_flux_data(consommation_annuelle, production_annuelle, puissance_kwc):
    """
    Simulation optimiste pour toutes tailles de centrales (3 à 18 kWc).
    Prend en compte la puissance crête installée pour le pic visuel.
    """
    mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc']
    heures = [f"{h:02d}:00" for h in range(24)]
    
    # --- 1. SAISONNALITÉ RÉUNIONNAISE (kWh) ---
    coeff_prod = [1.15, 1.10, 1.05, 0.90, 0.85, 0.75, 0.80, 0.90, 1.05, 1.15, 1.20, 1.10]
    coeff_conso = [1.30, 1.25, 1.10, 0.90, 0.85, 0.95, 1.00, 0.90, 0.85, 0.90, 1.00, 1.10]

    p_mensuelle = [(production_annuelle / 12) * (c / (sum(coeff_prod)/12)) for c in coeff_prod]
    c_mensuelle = [(consommation_annuelle / 12) * (c / (sum(coeff_conso)/12)) for c in coeff_conso]

    # --- 2. CALCUL DU PIC OPTIMISTE (Watts) ---
    # On simule un pic à 85% de la puissance crête (Performance Ratio optimiste)
    # Ex: 3 kWc -> 2550 W | 6 kWc -> 5100 W | 9 kWc -> 7650 W
    pic_reel_watts = puissance_kwc * 1000 * 0.85
    
    # Forme de la cloche solaire (sinusoïde accentuée pour l'aspect tropical)
    rad = [max(0, np.sin((h - 6.5) * np.pi / 11.5))**1.4 if 6.5 <= h <= 18 else 0 for h in range(24)]
    prod_h = [r * pic_reel_watts for r in rad] 
    
    # Consommation journalière (Basée sur l'entrée utilisateur)
    conso_j_avg = consommation_annuelle / 365
    coeffs_c = [0.4, 0.4, 0.4, 0.4, 0.4, 0.6, 1.8, 1.8, 1.2, 0.8, 0.7, 0.7, 
                1.2, 0.8, 0.7, 0.7, 1.2, 1.8, 2.4, 2.4, 2.4, 1.8, 0.8, 0.4]
    cons_h = [c * (conso_j_avg * 1000 / sum(coeffs_c)) for c in coeffs_c]

    # --- 3. CRÉATION DU GRAPHIQUE ---
    fig = go.Figure()

    # JOURNALIER (Aires)
    fig.add_trace(go.Scatter(
        x=heures, y=prod_h, name=f"Production {puissance_kwc}kWc (W)",
        mode='lines', line=dict(width=3, color='#F59E0B'),
        fill='tozeroy', fillcolor='rgba(245, 158, 11, 0.3)',
        visible=True
    ))
    fig.add_trace(go.Scatter(
        x=heures, y=cons_h, name="Consommation Maison (W)",
        mode='lines', line=dict(width=3, color='#334155'),
        fill='tozeroy', fillcolor='rgba(51, 65, 85, 0.2)',
        visible=True
    ))

    # MENSUEL (Bars)
    fig.add_trace(go.Bar(x=mois, y=p_mensuelle, name="Production (kWh)", marker_color='#F59E0B', visible=False))
    fig.add_trace(go.Bar(x=mois, y=c_mensuelle, name="Consommation (kWh)", marker_color='#334155', visible=False))

    # ANNUEL (Bars)
    fig.add_trace(go.Bar(x=['Bilan Annuel'], y=[production_annuelle], name="Prod (kWh)", marker_color='#F59E0B', visible=False))
    fig.add_trace(go.Bar(x=['Bilan Annuel'], y=[consommation_annuelle], name="Conso (kWh)", marker_color='#334155', visible=False))

    # --- 4. LAYOUT ---
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons", direction="right", x=0.5, y=1.2, xanchor="center",
                buttons=[
                    dict(label="Journalier", method="update", args=[{"visible": [True, True, False, False, False, False]}, {"yaxis": {"title": "Watts (W)"}}]),
                    dict(label="Mensuel", method="update", args=[{"visible": [False, False, True, True, False, False]}, {"yaxis": {"title": "kWh"}, "barmode": "group", "bargap": 0.3}]),
                    dict(label="Annuel", method="update", args=[{"visible": [False, False, False, False, True, True]}, {"yaxis": {"title": "kWh"}, "barmode": "group"}])
                ]
            )
        ],
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=20, t=100, b=50),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
        hovermode="x unified"
    )

    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})