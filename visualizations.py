import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.offline as pyo
from plotly.subplots import make_subplots
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
from utils import snapper_puissance_catalogue


def generate_knn_plot(surface, budget, zone_utilisateur, centrales_data, conso_mensuelle, production_reelle):
    # 1. Calculs Projet Utilisateur (Point Blanc)
    p_theo_u = (surface / 2.2) * 0.5
    p_comm_u = snapper_puissance_catalogue(p_theo_u)
    prod_an_u = production_reelle
    taux_u = (prod_an_u / (conso_mensuelle * 12)) * 100 if conso_mensuelle > 0 else 0
    budget_u_clean = int(budget)

    # 2. Simulation du Nuage de points
    all_surfaces, all_budgets, all_hovers = [], [], []
    np.random.seed(42)
    
    ratio_prod_m2 = production_reelle / surface if surface > 0 else 2000
    ratio_prix_m2 = 1733 / 2.2 

    for s_sim in np.linspace(10, 100, 80):
        s_val = s_sim * np.random.uniform(0.95, 1.05)
        b_val_sim = int(s_val * ratio_prix_m2 * np.random.uniform(0.9, 1.1))
        
        p_an_s = s_val * ratio_prod_m2
        p_comm_s = snapper_puissance_catalogue((s_val / 2.2) * 0.5)
        
        p_mens_s = p_an_s / 12
        p_jour_s = p_an_s / 365
        t_co_s = (p_an_s / (conso_mensuelle * 12)) * 100 if conso_mensuelle > 0 else 0
        
        all_surfaces.append(s_val)
        all_budgets.append(b_val_sim)
        
        # Étiquette Nuage : Style double fond simulé (Clair/Sombre)
        all_hovers.append(
            f"<span style='color: #F0C300; font-family: Montserrat; font-weight: bold;'> PARAMÈTRES</span><br>"
            f" Surface : <b>{s_val:.1f} m²</b><br>"
            f" Budget : <b>{b_val_sim} €</b><br>"
            f"<br>"
            f"<span style='color: #999999; font-family: Montserrat; font-weight: bold;'> ANALYSE COMPARATIVE</span><br>"
            f"Modèle : <b>{p_comm_s} kWc</b><br>"
            f"Année : <b>{p_an_s:.0f} kWh/an</b><br>"
            f"Mois : <b>{p_mens_s:.0f} kWh/m</b><br>"
            f"Jour : <b>{p_jour_s:.1f} kWh/j</b><br>"
            f"Couverture : <b>{t_co_s:.1f}%</b>"
        )

    # 3. Construction du Graphique
    fig = go.Figure()

    # Nuage
    fig.add_trace(go.Scatter(
        x=all_surfaces, y=all_budgets,
        mode='markers', text=all_hovers, hoverinfo='text',
        marker=dict(
            size=7, color=all_budgets, colorscale='YlOrBr', opacity=0.6,
            line=dict(width=0.5, color='white')
        )
    ))

    # Point Projet (Étiquette contrastée)
    hover_projet = (
        f"<span style='color: #FFFFFF; font-family: Montserrat; font-weight: bold;'> VOTRE POSITION</span><br>"
        f" Surface : <b>{surface:.1f} m²</b><br>"
        f" Budget : <b>{budget_u_clean} €</b><br>"
        f"<br>"
        f"<span style='color: #F0C300; font-family: Montserrat; font-weight: bold;'> VOTRE SOLUTION</span><br>"
        f"Modèle : <b>{p_comm_u} kWc</b><br>"
        f"Année : <b>{prod_an_u:.0f} kWh/an</b><br>"
        f"Mois : <b>{prod_an_u/12:.0f} kWh/m</b><br>"
        f"Jour : <b>{prod_an_u/365:.1f} kWh/j</b><br>"
        f"Couverture : <b>{taux_u:.1f}%</b>"
    )

    fig.add_trace(go.Scatter(
        x=[surface], y=[budget],
        mode='markers', text=hover_projet, hoverinfo='text',
        marker=dict(
            size=15, color='#FFFFFF', symbol='circle',
            line=dict(width=5, color='#F0C300') 
        )
    ))

    # 4. Layout
    fig.update_layout(
        paper_bgcolor='#000000', plot_bgcolor='#000000',
        font_family="Montserrat",
        xaxis=dict(title="Surface (m²)", color='white', gridcolor='#333', zeroline=False),
        yaxis=dict(title="Budget (€)", color='white', gridcolor='#333', zeroline=False),
        margin=dict(l=60, r=40, t=50, b=60),
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#111827", 
            font_size=12, 
            font_color="white", 
            bordercolor="#F0C300",
            align="left"
        )
    )

    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})
   

def courbes_data(surface, budget, consommation_estimee, production_annuelle, capacite_batterie, puissance_kwc):
    """Génère les courbes 24h cohérentes avec la puissance du projet avec remplissages translucides."""
    heures = [f"{h:02d}:00" for h in range(24)]
    
    # 1. PRODUCTION : Pic calé sur la puissance installée (Facteur 0.85 pour pertes réelles)
    p_peak_watt = puissance_kwc * 1000 * 0.85
    radiation = [max(0, np.sin((h - 6.5) * np.pi / 11.5)) if 6.5 <= h <= 18 else 0 for h in range(24)]
    prod_h = [r * p_peak_watt for r in radiation]

    # 2. CONSOMMATION : Profil type Réunion lissé sur l'année
    moyenne_conso_w = consommation_estimee / 8.76
    cons_h = []
    for h in range(24):
        if 7 <= h <= 9: coeff = 1.7
        elif 18 <= h <= 22: coeff = 2.5
        elif 0 <= h <= 6: coeff = 0.4
        else: coeff = 0.8
        cons_h.append(moyenne_conso_w * coeff)

    # 3. CALCUL SOC BATTERIE
    soc = []
    capa_wh = max(1, capacite_batterie) * 1000
    current_charge = capa_wh * 0.2
    for p, c in zip(prod_h, cons_h):
        delta = p - c
        current_charge = max(capa_wh * 0.1, min(capa_wh, current_charge + delta))
        soc.append((current_charge / capa_wh) * 100)

    # --- STYLE COMMUN (Austral Dark) ---
    layout_dark = dict(
        paper_bgcolor='#000000',
        plot_bgcolor='#000000',
        font=dict(family="Montserrat", color="white"),
        xaxis=dict(gridcolor='#222', zeroline=False, tickfont=dict(size=7)),
        yaxis=dict(gridcolor='#222', zeroline=False, title="Puissance (W)"),
        margin=dict(l=50, r=20, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    # --- G1 : ÉQUILIBRE ÉNERGÉTIQUE ---
    fig_p = go.Figure()
    
    # Production PV (Jaune-Ambre) - Inchangé
    fig_p.add_trace(go.Scatter(
        x=heures, y=prod_h, name="Production PV", 
        fill='tozeroy', 
        line=dict(color='#F59E0B', width=3),
        fillcolor='rgba(245, 158, 11, 0.15)'
    ))
    
    # Consommation (Modifiée en Rouge, Ligne Pleine, Remplissage Translucide)
    fig_p.add_trace(go.Scatter(
        x=heures, y=cons_h, 
        name="Consommation", 
        fill='tozeroy',
        line=dict(
            color='#FF0000',  # Rouge vif
            width=3           # Épaisseur légèrement augmentée pour la lisibilité
        ),
        fillcolor='rgba(255, 0, 0, 0.15)' # Rouge très translucide (15% d'opacité)
    ))
    
    fig_p.update_layout(title="Équilibre Énergétique (24h)", **layout_dark)

    # --- G2 : ÉTAT DE LA BATTERIE ---
    fig_soc = go.Figure()
    fig_soc.add_trace(go.Scatter(
        x=heures, y=soc, name="Batterie (%)", 
        fill='tozeroy', 
        line=dict(color='#00FF88', width=2),
        fillcolor='rgba(0, 255, 136, 0.12)'
    ))
    fig_soc.update_layout(title="État de Charge Batterie", **layout_dark)
    fig_soc.update_yaxes(range=[0, 105], ticksuffix="%", title="Charge (%)")

    # --- G3 : FLUX ENTRANTS/SORTANTS ---
    fig_flux = go.Figure()
    # Injection (Ambre)
    fig_flux.add_trace(go.Bar(
        x=heures, y=prod_h, name="Injection", 
        marker_color='#F59E0B', opacity=0.8
    ))
    # Soutirage (Rouge)
    fig_flux.add_trace(go.Bar(
        x=heures, y=[-v for v in cons_h], name="Soutirage", 
        marker_color='#DC2626', opacity=0.8
    ))
    fig_flux.update_layout(barmode='overlay', title="Flux Entrants/Sortants", **layout_dark)

    return {
        "plot_puissance": pio.to_html(fig_p, full_html=False, config={'displayModeBar': False}),
        "plot_soc": pio.to_html(fig_soc, full_html=False, config={'displayModeBar': False}),
        "plot_flux": pio.to_html(fig_flux, full_html=False, config={'displayModeBar': False})
    }


def trace_courbes(df, C_bat, puissance_borne_ve, heures_ve, p_centrale_kwc=6.0):
    SOC = [80.0]
    P_bat, P_edf = [], []

    # --- 1. CONFIGURATION PHYSIQUE ---
    Vmp_unitaire = 37.47
    Pmax_panneau = 500

    nb_total = int((p_centrale_kwc * 1000) / Pmax_panneau)
    nb_strings = 2 if p_centrale_kwc > 6 else 1
    panneaux_par_string = nb_total / nb_strings

    # Puissance crête totale
    Pmax_centrale = nb_total * Pmax_panneau

    # --- 1B. FACTEUR DE PERFORMANCE (PR) ---
    # Valeurs réalistes basées sur tes exemples
    if p_centrale_kwc <= 3:
        PR = 0.92     # ≈ 2800 W pour 3 kWc
    elif p_centrale_kwc <= 8:
        PR = 0.96     # ≈ 7700 W pour 8 kWc
    else:
        PR = 0.97

    # Puissance max réellement atteignable
    Pmax_reel = Pmax_centrale * PR

    # --- 1C. CORRECTION DE LA PRODUCTION PV ---
    df['Ppv_corr'] = df['Ppv'].clip(upper=Pmax_reel)

    # Recalcul tension/courant cohérents
    Vmp = panneaux_par_string * Vmp_unitaire
    Imp = Pmax_centrale / Vmp

    df['Vdc'] = [Vmp if p > 0 else 0 for p in df['Ppv_corr']]
    df['Idc'] = [min(p / Vmp, Imp) if Vmp > 0 else 0 for p in df['Ppv_corr']]
    df['Ppv_corr'] = df['Vdc'] * df['Idc']

    # --- 2. SIMULATION BATTERIE ---
    for t in range(len(df)):
        surplus = df['Ppv_corr'].iloc[t] - df['Pload_totale'].iloc[t]
        soc_actuel = SOC[-1]

        if surplus > 0:
            charge = min(surplus, (100 - soc_actuel) * (C_bat / 100))
            SOC.append(soc_actuel + (charge / C_bat * 100))
            P_bat.append(charge)
            P_edf.append(0)
        else:
            besoin = -surplus
            decharge = min(besoin, (soc_actuel - 12) * (C_bat / 100))
            SOC.append(soc_actuel - (decharge / C_bat * 100))
            P_bat.append(-decharge)
            P_edf.append(besoin - decharge)

    df['SOC'] = SOC[:-1]
    df['P_bat'] = P_bat

    # --- 3. GRAPHIQUES ---

    # G1: ÉQUILIBRE ÉNERGÉTIQUE
    fig_equilibre = go.Figure()
    fig_equilibre.add_trace(go.Scatter(
        x=df['Datetime'], y=df['Ppv_corr'], name="Production PV",
        fill='tozeroy', line=dict(color='#F59E0B', width=3),
        fillcolor='rgba(245, 158, 11, 0.15)'
    ))
    fig_equilibre.add_trace(go.Scatter(
        x=df['Datetime'], y=df['Pload_totale'], name="Demande Totale",
        fill='tozeroy', line=dict(color='#dc2626', width=3, dash='dash'),
        fillcolor='rgba(220, 38, 38, 0.1)'
    ))
    fig_equilibre.update_layout(
        title=dict(text="Équilibre Énergétique : Production vs Demande", x=0.5, y=0.95),
        margin=dict(t=120), template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    # G2: DÉTAIL DE LA CHARGE
    fig_load = go.Figure(go.Scatter(
        x=df['Datetime'], y=df['Pload_totale'], name="Consommation Totale",
        fill='tozeroy', line=dict(color='#FF0000'),
        fillcolor='rgba(255, 0, 0, 0.15)'
    ))
    fig_load.update_layout(
        title=dict(text="Détail de la Charge (Bâtiment + VE)", x=0.5, y=0.95),
        margin=dict(t=120), template="plotly_white", hovermode="x unified"
    )

    # G3: SYNTHÈSE DES FLUX
    fig_flux = make_subplots(specs=[[{"secondary_y": True}]])

    fig_flux.add_trace(go.Scatter(
        x=df['Datetime'], y=df['Ppv_corr'], name="Prod PV (W)", fill='tozeroy',
        line=dict(color='#F59E0B', width=2), fillcolor='rgba(245, 158, 11, 0.1)'
    ), secondary_y=False)

    fig_flux.add_trace(go.Scatter(
        x=df['Datetime'], y=df['Pload_totale'], name="Conso (W)", fill='tozeroy',
        line=dict(color='red', width=2), fillcolor='rgba(255, 0, 0, 0.05)'
    ), secondary_y=False)

    fig_flux.add_trace(go.Scatter(
        x=df['Datetime'], y=P_edf, name="Import Réseau (W)", fill='tozeroy',
        line=dict(color='blue', width=1.5), fillcolor='rgba(0, 0, 255, 0.05)'
    ), secondary_y=False)

    fig_flux.add_trace(go.Scatter(
        x=df['Datetime'], y=df['P_bat'], name="Flux Bat (W)", fill='tozeroy',
        line=dict(color='purple', width=2, dash='dash'), fillcolor='rgba(128, 0, 128, 0.05)'
    ), secondary_y=False)

    fig_flux.add_trace(go.Scatter(
        x=df['Datetime'], y=df['SOC'], name="SOC Batterie (%)", fill='tozeroy',
        line=dict(color='#006400', width=3), fillcolor='rgba(0, 100, 0, 0.1)'
    ), secondary_y=True)

    fig_flux.update_layout(
        title=dict(text="Synthèse Énergétique : Flux & État de Charge", x=0.5, y=0.95),
        margin=dict(t=120), template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    fig_flux.update_yaxes(title_text="Puissance (Watts)", secondary_y=False)
    fig_flux.update_yaxes(title_text="SOC (%)", range=[0, 105], secondary_y=True, color="#006400")

    # G4: TENSION & COURANT DC
    fig_elec = make_subplots(specs=[[{"secondary_y": True}]])
    fig_elec.add_trace(go.Scatter(
        x=df['Datetime'], y=df['Vdc'], name="Tension DC (V)", fill='tozeroy',
        line=dict(color='#FFA500', width=3), fillcolor='rgba(255, 165, 0, 0.1)'
    ), secondary_y=False)

    fig_elec.add_trace(go.Scatter(
        x=df['Datetime'], y=df['Idc'], name="Courant DC (A)", fill='tozeroy',
        line=dict(color='#0000FF', width=3, dash='dot'), fillcolor='rgba(0, 0, 255, 0.05)'
    ), secondary_y=True)

    fig_elec.update_layout(
        title=dict(text=f"Caractéristiques Électriques DC ({int(panneaux_par_string)} pan./chaine)", x=0.5, y=0.95),
        margin=dict(t=120), template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    fig_elec.update_yaxes(title_text="Tension (Volts)", secondary_y=False, color="#FFA500")
    fig_elec.update_yaxes(title_text="Courant (Ampères)", secondary_y=True, color="#0000FF")

    return (
        pio.to_html(fig_equilibre, full_html=False, config={'displayModeBar': False}),
        pio.to_html(fig_load, full_html=False, config={'displayModeBar': False}),
        pio.to_html(fig_flux, full_html=False, config={'displayModeBar': False}),
        pio.to_html(fig_elec, full_html=False, config={'displayModeBar': False})
    )



def courbe_iv_pv(panneau):
    """
    Génère le graphique interactif IV/PV fidèle aux specs STC.
    Inclut Vmp, Imp, Voc, Isc et Pmax dans les étiquettes de survol.
    """
    p = {k.upper(): v for k, v in panneau.items()}
    
    try:
        # 1. Récupération des données exactes de la Config
        PMAX_STC = p.get('PMAX', 500)
        VMP_STC = p.get('VMP', 37.47)
        IMP_STC = p.get('IMP', 13.34)
        VOC_STC = p.get('VOC', 43.58)
        ISC_STC = p.get('ISC', 14.31)

        # 2. Modélisation mathématique fidèle
        # Pour que la courbe passe par (Vmp, Imp), on calcule l'exposant 'n' réel
        # Basé sur la relation : Imp = Isc * (1 - (Vmp/Voc)^n)
        n_ajuste = np.log(1 - (IMP_STC / ISC_STC)) / np.log(VMP_STC / VOC_STC)
        
        v_vec = np.linspace(0, VOC_STC, 100)
        i_vec = np.maximum(0, ISC_STC * (1 - (v_vec / VOC_STC)**n_ajuste))
        p_vec = v_vec * i_vec

        # 3. Création du graphique
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # --- TRACE : COURBE I-V ---
        fig.add_trace(go.Scatter(
            x=v_vec, y=i_vec, 
            name="Courant (A)", 
            mode='lines',
            line=dict(color='#2563eb', width=4),
            fill='tozeroy',
            fillcolor='rgba(37, 99, 235, 0.12)',
            customdata=p_vec,
            hovertemplate=(
                "<b>Tension :</b> %{x:.2f} V<br>" +
                "<b>Courant :</b> %{y:.2f} A<br>" +
                "<b>Puissance :</b> %{customdata:.1f} W<extra></extra>"
            )
        ), secondary_y=False)
        
        # --- TRACE : COURBE P-V ---
        fig.add_trace(go.Scatter(
            x=v_vec, y=p_vec, 
            name="Puissance (W)", 
            mode='lines',
            line=dict(color='#e11d48', width=4), 
            fill='tozeroy',
            fillcolor='rgba(225, 29, 72, 0.12)',
            customdata=i_vec,
            hovertemplate=(
                "<b>Tension :</b> %{x:.2f} V<br>" +
                "<b>Puissance :</b> %{y:.1f} W<br>" +
                "<b>Courant :</b> %{customdata:.2f} A<extra></extra>"
            )
        ), secondary_y=True)

        # --- POINT PMAX (MPP) ---
        fig.add_trace(go.Scatter(
            x=[VMP_STC], y=[PMAX_STC],
            mode="markers+text",
            marker=dict(color='#facc15', size=14, symbol='star', line=dict(color='black', width=1)),
            name="Point MPP",
            # On force l'affichage des specs exactes au survol du point
            hovertemplate=(
                "<b>POINT DE PUISSANCE MAX (STC)</b><br>" +
                "Pmax : " + str(PMAX_STC) + " Wc<br>" +
                "Vmp : " + str(VMP_STC) + " V<br>" +
                "Imp : " + str(IMP_STC) + " A<extra></extra>"
            )
        ), secondary_y=True)

        # 4. Annotations et Badges
        fig.add_annotation(
            xref="paper", yref="paper", x=0.02, y=0.96,
            text=f"☀️ <b>STC : 25°C</b><br>Isc: {ISC_STC}A | Voc: {VOC_STC}V",
            showarrow=False, bgcolor="#eff6ff", bordercolor="#3b82f6",
            borderpad=6, font=dict(size=11, color="#1e40af")
        )

        # 5. Configuration Layout
        fig.update_layout(
            title=dict(text=f"Caractéristique Réelle : {PMAX_STC}Wc", x=0.5, font=dict(size=18)),
            template="plotly_white",
            hovermode="x unified",
            xaxis=dict(title="Tension (V)", showspikes=True, spikethickness=1, gridcolor="#f0f0f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=100, b=20)
        )

        fig.update_yaxes(title_text="Courant (A)", color="#2563eb", secondary_y=False, range=[0, ISC_STC * 1.1])
        fig.update_yaxes(title_text="Puissance (W)", color="#e11d48", secondary_y=True, range=[0, PMAX_STC * 1.1])

        return pio.to_html(fig, full_html=False, config={'displayModeBar': False}), None, None, None

    except Exception as e:
        return f"<div style='color:red;'>Erreur : {str(e)}</div>", None, None, None