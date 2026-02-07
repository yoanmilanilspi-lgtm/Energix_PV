import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, session, redirect, url_for, flash
from models import PVRecommender, FORM_DATA

# Configuration globale
from config import Config
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY  

# Utils et métier (imports uniques)
from utils import (
    safe_float, safe_int, estimer_consommation, obtenir_nb_panneaux,
    histogramme_flux_data, snapper_puissance_catalogue
)
from models import PVRecommender
from visualizations import (
    generate_knn_plot, courbes_data, trace_courbes, courbe_iv_pv
)

# Instance globale
recommender = PVRecommender()

@app.route('/', methods=['GET', 'POST'])
def index():
    # Préparation des suggestions pour le datalist (Ville + CP)
    suggestions = FORM_DATA["lieux"]["ville"] + FORM_DATA["lieux"]["code_postal"]

    if request.method == 'POST':
        try:
            # Récupération brute des données du formulaire
            surface = safe_float(request.form.get('surface'))
            budget = safe_float(request.form.get('budget'))
            lieu_saisi = request.form.get('zone_ville_cp', '').strip()
            nb_occ = safe_int(request.form.get('nb_occupants'))
            cons_saisie = safe_float(request.form.get('consommation_mensuelle'))

            # LOGIQUE : Priorité à la consommation, sinon estimation par habitants
            if cons_saisie > 0:
                cons_finale = cons_saisie
            elif nb_occ > 0:
                cons_finale = estimer_consommation(nb_occ)
            else:
                # Si rien n'est saisi, on met une valeur par défaut pour éviter le crash
                cons_finale = 300.0

            # Détermination de la zone géographique
            zone, lieu_nom, interco = recommender.get_zone_from_input(lieu_saisi)

            # Appel du moteur de recommandation (bien capturer les 5 variables !)
            reco_html, p_centrale, p_annuelle, p_mensuelle, p_journaliere = \
                recommender.recommend_pv(surface, cons_finale, budget, zone)

            # Enregistrement propre en session
            session['user_data'] = {
                'surface': surface,
                'budget': budget,
                'cons_mensuelle': cons_finale,
                'nb_occupants': nb_occ,
                'zone': zone,
                'lieu': lieu_nom,
                'intercommunalite': interco,
                'puissance_centrale': p_centrale,
                'prod_annuelle': p_annuelle,
                'prod_mensuelle': p_mensuelle,
                'prod_journaliere': p_journaliere,
                'nb_panneaux': obtenir_nb_panneaux(p_centrale),
                'recommendation': reco_html
            }

            flash("Analyse réussie !", "success")
            return redirect(url_for('show_recommendation'))

        except Exception as e:
            # CRUCIAL : On renvoie l'index avec le message d'erreur
            flash(f"Erreur lors du traitement : {str(e)}", "error")
            return render_template('index.html', data=FORM_DATA, suggestions=suggestions)

    # Cas GET (chargement initial de la page)
    return render_template('index.html', data=FORM_DATA, suggestions=suggestions)

@app.route('/recommendation')
def show_recommendation():
    data = session.get('user_data')
    if not data:
        flash("Aucune donnée. Saisissez un formulaire.", "warning")
        return redirect(url_for('index'))
    return render_template('result.html', **data)

@app.route('/conso_prod')
def show_conso_prod():
    data = session.get('user_data', {})
    if not data:
        flash("Faites une recommandation d'abord.", "warning")
        return redirect(url_for('index'))

    conso_mensuelle_kwh = safe_float(data.get('cons_mensuelle'), 300.0)
    prod_annuelle_kwh = safe_float(data.get('prod_annuelle'), 4536.0)
    capa_bat_kwh = safe_float(data.get('capacite_batterie'), 5.0)
    p_kwc = safe_float(data.get('puissance_centrale'), 3.0)

    graph_histogramme = histogramme_flux_data(
        consommation_annuelle=conso_mensuelle_kwh * 12,
        production_annuelle=prod_annuelle_kwh,
        puissance_kwc=p_kwc
    )

    stats = {
        'consommation_production_plot': graph_histogramme,
        'production_estimee': round(prod_annuelle_kwh, 0),
        'production_annuelle': round(prod_annuelle_kwh, 0),
        'production_mensuelle': round(prod_annuelle_kwh / 12, 0),
        'production_journaliere': round(prod_annuelle_kwh / 365, 0),
        'consommation_estimee': round(conso_mensuelle_kwh, 0),
        'consommation_annuelle': round(conso_mensuelle_kwh * 12, 0),
        'consommation_mensuelle': round(conso_mensuelle_kwh, 0),
        'consommation_journaliere': round(conso_mensuelle_kwh / 30, 0),
        'puissance_centrale': p_kwc,
        'capacite_batterie': capa_bat_kwh
    }
    return render_template('conso_prod.html', **{**data, **stats})

@app.route('/graph')
def show_graph():
    data = session.get('user_data')
    if not data:
        flash("Données manquantes.", "warning")
        return redirect(url_for('index'))

    surf = safe_float(data.get('surface'))
    budg = safe_float(data.get('budget'))
    cons_mens = safe_float(data.get('cons_mensuelle'))
    prod_reelle = safe_float(data.get('prod_annuelle'))
    zone_user = data.get('zone', 'Zone 1 (Ouest)')

    p_theo_u = (surf / 2.2) * 0.5
    puissance_centrale_kwc = snapper_puissance_catalogue(p_theo_u)

    knn_plot = generate_knn_plot(
        surface=surf, budget=budg, zone_utilisateur=zone_user,
        centrales_data=None, conso_mensuelle=cons_mens, production_reelle=prod_reelle
    )

    mapping_batterie = {3: 3.1, 6: 6.1, 9: 9.2, 12: 12.3}
    cap_bat = mapping_batterie.get(int(puissance_centrale_kwc), 6.1)

    plots = courbes_data(
        surface=surf, budget=budg, consommation_estimee=cons_mens * 12,
        production_annuelle=prod_reelle, capacite_batterie=cap_bat, puissance_kwc=puissance_centrale_kwc
    )

    stats_affichage = {
        'production_estimee': prod_reelle, 'consommation_estimee_an': cons_mens * 12,
        'cap_bat': cap_bat, 'puissance_centrale_kwc': puissance_centrale_kwc,
        'production_mensuelle': prod_reelle / 12, 'production_journaliere': prod_reelle / 365,
        'consommation_journaliere': (cons_mens * 12) / 365, 'predicted_production': prod_reelle
    }

    return render_template('graph.html', knn_plot=knn_plot, **plots, **stats_affichage, **data)

@app.route('/dashboard')
def dashboard():
    try:
        nav_params = {k: request.args.get(k) for k in [
            'surface', 'budget', 'nb_occupants', 'consommation_estimee', 'production_estimee',
            'lieu', 'zone', 'intercommunalite'
        ]}
        is_ve_enabled = request.args.get('enable_ve') == '1'
        puissance_centrale = safe_float(request.args.get('puissance_centrale'), 6.0)
        capacite_batterie_kwh = safe_float(request.args.get('capacite_batterie'), 6.1)
        borne_ve_val = safe_float(request.args.get('borne_ve'), 7.2)

        C_bat_wh = capacite_batterie_kwh * 1000
        puissance_reelle_ve = borne_ve_val * 1000 if is_ve_enabled else 0
        heures_ve = list(range(8, 18)) if is_ve_enabled else []

        # DataFrame (de Config.PANNEAU_DATA)
        data = {
            'Datetime': pd.date_range("2026-01-01 06:00:00", periods=15, freq="H"),
            'Radiation_W_m2': [0.0, 0.0, 293.1, 424.7, 620.3, 986.4, 1300.0, 1299.1, 888.4, 788.9, 816.7, 357.8, 221.7, 0.0, 0.0]
        }
        df = pd.DataFrame(data)
        df['Heure'] = df['Datetime'].dt.hour

        p_data = Config().PANNEAU_DATA  # Ou import global
        nb_panneaux = int((puissance_centrale * 1000) / p_data['PMAX'])
        surface_totale_reelle = nb_panneaux * p_data['SURFACE_PV']
        df['Ppv'] = (p_data['EFFICIENCY'] / 100) * surface_totale_reelle * df['Radiation_W_m2']
        df['Pload'] = np.random.uniform(600, 3000, len(df))
        df['P_ve'] = 0
        if is_ve_enabled:
            df.loc[df['Heure'].isin(heures_ve), 'P_ve'] = puissance_reelle_ve
        df['Pload_totale'] = df['Pload'] + df['P_ve']

        g_equilibre, g_load, g_flux, elec_plot = trace_courbes(df, C_bat_wh, puissance_reelle_ve, heures_ve, p_centrale_kwc=puissance_centrale)
        iv_plot_combined, _, _, _ = courbe_iv_pv(p_data)

        return render_template(
            'dashboard.html',
            graph_p=g_equilibre, graph_load=g_load, graph_flux=g_flux, elec_plot=elec_plot, iv_plot=iv_plot_combined,
            puissance_centrale=puissance_centrale, capacite_batterie=capacite_batterie_kwh, borne_ve=borne_ve_val,
            nb_panneaux=nb_panneaux, surface_reelle=round(surface_totale_reelle, 2), enable_ve=is_ve_enabled,
            **nav_params
        )
    except Exception as e:
        flash(f"Erreur dashboard : {str(e)}", "error")
        return redirect(url_for('index'), code=302)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
