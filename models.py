from utils import safe_float, safe_int
import math
# Données pour les datalists (synchronisées avec PVRecommender)
FORM_DATA = {
    "consommation": [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1500, 2000],
    "occupants": range(1, 11),
    "surface": range(10, 105, 5),
    "budget": range(8000, 51000, 1000),
    "lieux": {
        "intercommunalite": ["CINOR", "CIREST", "CIVIS", "TCO", "CASUD"],
        "zone": ["Zone 1 (Ouest)", "Zone 2 (Est)", "Zone 3 (Les Hauts)", "Zone 4 (Altitude >800m)", "Zone 5 (Nord)", "Zone 6 (Sud)"],
        "ville": [
            "Bagatelle (97441)", "Bois-Blanc (97439)", "Bois-de-Nèfles Saint-Paul (97460)", 
            "Bras-Fusil (97470)", "Bras-Panon (97412)", "Bras-Pistolet (97441)", 
            "Cambuston (97440)", "Cilaos (97413)", "Deux-Rives (97441)", 
            "Entre-Deux (97414)", "Grand-Bois (97410)", "Grand Îlet (97433)", 
            "Grande-Chaloupe (97419)", "Hell-Bourg (97433)", "L'Étang-Salé (97427)", 
            "La Bretagne (97490)", "La Chaloupe (97436)", "La Montagne (97417)", 
            "La Plaine-des-Palmistes (97431)", "La Possession (97419)", "La Rivière (97421)", 
            "La Rivière des Galets (97420)", "La Saline-les-Bains (97422)", "Le Petit Tampon (97430)", 
            "Le Port (97420)", "Le Tampon (97430)", "Les Avirons (97425)", 
            "Les Trois-Bassins (97426)", "Mafate (97419)", "Mont Vert Les Bas (97430)", 
            "Mont Vert Les Hauts (97430)", "Petite-Île (97429)", "Plaine des Cafres (97418)", 
            "Plaine des Grègues (97480)", "Quartier-Français (97441)", "Saint-André (97440)", 
            "Saint-Benoît (97470)", "Saint-Denis (97400)", "Saint-Gilles-les-Bains (97434)", 
            "Saint-Gilles-les-Hauts (97435)", "Saint-Joseph (97480)", "Saint-Leu (97436)", 
            "Saint-Louis (97450)", "Saint-Paul (97460)", "Saint-Philippe (97442)", 
            "Saint-Pierre (97410)", "Sainte-Anne (97470)", "Sainte-Clotilde (97490)", 
            "Sainte-Marie (97438)", "Sainte-Rose (97439)", "Sainte-Suzanne (97441)", 
            "Terre-Sainte (97410)", "Trois Mares (97430)"
        ],
        "code_postal": [
            "97400", "97410", "97412", "97413", "97414", "97417", "97418", "97419", 
            "97420", "97421", "97422", "97425", "97426", "97427", "97429", "97430", 
            "97431", "97433", "97434", "97435", "97436", "97438", "97439", "97440", 
            "97441", "97442", "97450", "97460", "97470", "97480", "97490"
        ]
    }
}
class PVRecommender:
    def __init__(self):
        self.lieux_infos = {
            # --- CINOR (NORD) ---
            "Saint-Denis (97400)":            {"code_postal": "97400", "intercommunalite": "CINOR", "zone": "Zone 5 (Nord)"},
            "Sainte-Clotilde (97490)":        {"code_postal": "97490", "intercommunalite": "CINOR", "zone": "Zone 5 (Nord)"},
            "La Montagne (97417)":            {"code_postal": "97417", "intercommunalite": "CINOR", "zone": "Zone 5 (Nord)"},
            "La Bretagne (97490)":            {"code_postal": "97490", "intercommunalite": "CINOR", "zone": "Zone 5 (Nord)"},
            "Sainte-Marie (97438)":           {"code_postal": "97438", "intercommunalite": "CINOR", "zone": "Zone 5 (Nord)"},
            "Sainte-Suzanne (97441)":         {"code_postal": "97441", "intercommunalite": "CINOR", "zone": "Zone 5 (Nord)"},
            "Bagatelle (97441)":              {"code_postal": "97441", "intercommunalite": "CINOR", "zone": "Zone 5 (Nord)"},
            "Deux-Rives (97441)":             {"code_postal": "97441", "intercommunalite": "CINOR", "zone": "Zone 5 (Nord)"},
            "Bras-Pistolet (97441)":          {"code_postal": "97441", "intercommunalite": "CINOR", "zone": "Zone 5 (Nord)"},
            "Quartier-Français (97441)":      {"code_postal": "97441", "intercommunalite": "CINOR", "zone": "Zone 5 (Nord)"},
            # --- CIREST (EST & CIRQUES) ---
            "Saint-André (97440)":            {"code_postal": "97440", "intercommunalite": "CIREST", "zone": "Zone 2 (Est)"},
            "Cambuston (97440)":              {"code_postal": "97440", "intercommunalite": "CIREST", "zone": "Zone 2 (Est)"},
            "Bras-Panon (97412)":             {"code_postal": "97412", "intercommunalite": "CIREST", "zone": "Zone 2 (Est)"},
            "Saint-Benoît (97470)":           {"code_postal": "97470", "intercommunalite": "CIREST", "zone": "Zone 2 (Est)"},
            "Bras-Fusil (97470)":             {"code_postal": "97470", "intercommunalite": "CIREST", "zone": "Zone 2 (Est)"},
            "Sainte-Anne (97470)":            {"code_postal": "97470", "intercommunalite": "CIREST", "zone": "Zone 2 (Est)"},
            "Sainte-Rose (97439)":            {"code_postal": "97439", "intercommunalite": "CIREST", "zone": "Zone 2 (Est)"},
            "Bois-Blanc (97439)":             {"code_postal": "97439", "intercommunalite": "CIREST", "zone": "Zone 2 (Est)"},
            "La Plaine-des-Palmistes (97431)":{"code_postal": "97431", "intercommunalite": "CIREST", "zone": "Zone 4 (Altitude >800m)"},
            "Salazie (97433)":                {"code_postal": "97433", "intercommunalite": "CIREST", "zone": "Zone 3 (Les Hauts)"},
            "Hell-Bourg (97433)":             {"code_postal": "97433", "intercommunalite": "CIREST", "zone": "Zone 3 (Les Hauts)"},
            "Grand Îlet (97433)":             {"code_postal": "97433", "intercommunalite": "CIREST", "zone": "Zone 3 (Les Hauts)"},
            # --- TCO (OUEST) ---
            "Le Port (97420)":                {"code_postal": "97420", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "La Possession (97419)":          {"code_postal": "97419", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "Grande-Chaloupe (97419)":        {"code_postal": "97419", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "Mafate (97419)":                 {"code_postal": "97419", "intercommunalite": "TCO", "zone": "Zone 3 (Les Hauts)"},
            "La Rivière des Galets (97420)":  {"code_postal": "97420", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "Saint-Paul (97460)":             {"code_postal": "97460", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "Bois-de-Nèfles Saint-Paul (97460)":{"code_postal": "97460", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "Saint-Gilles-les-Bains (97434)": {"code_postal": "97434", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "Saint-Gilles-les-Hauts (97435)": {"code_postal": "97435", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "La Saline-les-Bains (97422)":    {"code_postal": "97422", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "Les Trois-Bassins (97426)":      {"code_postal": "97426", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "Saint-Leu (97436)":              {"code_postal": "97436", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "La Chaloupe (97436)":            {"code_postal": "97436", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            "Les Avirons (97425)":            {"code_postal": "97425", "intercommunalite": "TCO", "zone": "Zone 3 (Les Hauts)"},
            "L'Étang-Salé (97427)":           {"code_postal": "97427", "intercommunalite": "TCO", "zone": "Zone 1 (Ouest)"},
            # --- CIVIS (SUD) ---
            "Saint-Louis (97450)":            {"code_postal": "97450", "intercommunalite": "CIVIS", "zone": "Zone 6 (Sud)"},
            "La Rivière (97421)":             {"code_postal": "97421", "intercommunalite": "CIVIS", "zone": "Zone 6 (Sud)"},
            "Cilaos (97413)":                 {"code_postal": "97413", "intercommunalite": "CIVIS", "zone": "Zone 3 (Les Hauts)"},
            "Saint-Pierre (97410)":           {"code_postal": "97410", "intercommunalite": "CIVIS", "zone": "Zone 6 (Sud)"},
            "Grand-Bois (97410)":             {"code_postal": "97410", "intercommunalite": "CIVIS", "zone": "Zone 6 (Sud)"},
            "Terre-Sainte (97410)":           {"code_postal": "97410", "intercommunalite": "CIVIS", "zone": "Zone 6 (Sud)"},
            "Petite-Île (97429)":             {"code_postal": "97429", "intercommunalite": "CIVIS", "zone": "Zone 6 (Sud)"},
            # --- CASUD (SUD) ---
            "Entre-Deux (97414)":             {"code_postal": "97414", "intercommunalite": "CASUD", "zone": "Zone 6 (Sud)"},
            "Le Tampon (97430)":              {"code_postal": "97430", "intercommunalite": "CASUD", "zone": "Zone 4 (Altitude >800m)"},
            "Le Petit Tampon (97430)":        {"code_postal": "97430", "intercommunalite": "CASUD", "zone": "Zone 4 (Altitude >800m)"},
            "Trois Mares (97430)":            {"code_postal": "97430", "intercommunalite": "CASUD", "zone": "Zone 4 (Altitude >800m)"},
            "Mont Vert Les Hauts (97430)":    {"code_postal": "97430", "intercommunalite": "CASUD", "zone": "Zone 4 (Altitude >800m)"},
            "Mont Vert Les Bas (97430)":      {"code_postal": "97430", "intercommunalite": "CASUD", "zone": "Zone 6 (Sud)"},
            "Plaine des Cafres (97418)":      {"code_postal": "97418", "intercommunalite": "CASUD", "zone": "Zone 4 (Altitude >800m)"},
            "Saint-Joseph (97480)":           {"code_postal": "97480", "intercommunalite": "CASUD", "zone": "Zone 6 (Sud)"},
            "Plaine des Grègues (97480)":     {"code_postal": "97480", "intercommunalite": "CASUD", "zone": "Zone 6 (Sud)"},
            "Saint-Philippe (97442)":         {"code_postal": "97442", "intercommunalite": "CASUD", "zone": "Zone 6 (Sud)"}
        }
        self.panneaux = [
            {"puissance": 500, "surface": 2.2, "prix_materiel": 800, "prix_pose": 1400}
        ]
        self.centrales = [
            {"taille": 15, "puissance": 3, "Zone 1 (Ouest)": 4536, "Zone 2 (Est)": 3942, "Zone 3 (Les Hauts)": 3750,
             "Zone 4 (Altitude >800m)": 4146, "Zone 5 (Nord)": 4398, "Zone 6 (Sud)": 4188},
            {"taille": 30, "puissance": 6, "Zone 1 (Ouest)": 9072, "Zone 2 (Est)": 7884, "Zone 3 (Les Hauts)": 7500,
             "Zone 4 (Altitude >800m)": 8292, "Zone 5 (Nord)": 8796, "Zone 6 (Sud)": 8376},
            {"taille": 45, "puissance": 9, "Zone 1 (Ouest)": 13608, "Zone 2 (Est)": 11826, "Zone 3 (Les Hauts)": 11250,
             "Zone 4 (Altitude >800m)": 12438, "Zone 5 (Nord)": 13194, "Zone 6 (Sud)": 12564},
            {"taille": 60, "puissance": 12, "Zone 1 (Ouest)": 18144, "Zone 2 (Est)": 15768, "Zone 3 (Les Hauts)": 15000,
             "Zone 4 (Altitude >800m)": 16584, "Zone 5 (Nord)": 17592, "Zone 6 (Sud)": 16752},
            {"taille": 75, "puissance": 15, "Zone 1 (Ouest)": 22680, "Zone 2 (Est)": 19710, "Zone 3 (Les Hauts)": 18750,
             "Zone 4 (Altitude >800m)": 20730, "Zone 5 (Nord)": 21990, "Zone 6 (Sud)": 20940},
            {"taille": 90, "puissance": 18, "Zone 1 (Ouest)": 27216, "Zone 2 (Est)": 23652, "Zone 3 (Les Hauts)": 22500,
             "Zone 4 (Altitude >800m)": 24876, "Zone 5 (Nord)": 26388, "Zone 6 (Sud)": 25128}
        ]
        self.references = {
            "zone": {
                "Zone 1 (Ouest)": "https://re.jrc.ec.europa.eu/pvg_tools/en/#PVP",
                "Zone 2 (Est)": "https://re.jrc.ec.europa.eu/pvg_tools/en/#PVP",
                "Zone 3 (Les Hauts)": "https://re.jrc.ec.europa.eu/pvg_tools/en/#PVP",
                "Zone 4 (Altitude >800m)": "https://re.jrc.ec.europa.eu/pvg_tools/en/#PVP",
                "Zone 5 (Nord)": "https://re.jrc.ec.europa.eu/pvg_tools/en/#PVP",
                "Zone 6 (Sud)": "https://re.jrc.ec.europa.eu/pvg_tools/en/#PVP"
            },
            "intercommunalite": {
                "CINOR": "https://www.cinor.fr",
                "CIREST": "https://www.cirest.fr",
                "TCO": "https://www.tco.re",
                "CIVIS": "https://www.civis.re",
                "CASUD": "https://www.casud.re"
            },
            "region": {
                "Nord": "https://www.saintdenis.re",
                "Sud": "https://www.sudreunion.fr",
                "Est": "https://www.estreunion.fr",
                "Ouest": "https://www.ouest-lareunion.com",
                "Les Hauts": "https://www.reunion.fr"
            },
            "ile": {
                "La Réunion": "https://fr.wikipedia.org/wiki/La_Réunion"
            }
        }  
    def get_references(self, lieu):
        if lieu in ["Toute l'île", "La Réunion", None, "", "Multi-secteurs"]:
            return {
                "zone": {
                    "label": "Toute l'île",
                    "url": "https://re.jrc.ec.europa.eu/pvg_tools/en/#PVP"
                },
                "intercommunalite": {
                    "label": "Multi-secteurs",
                    "url": "https://fr.wikipedia.org/wiki/La_Réunion"
                },
                "region": {
                    "label": "Île entière",
                    "url": "https://www.reunion.fr"
                },
                "ile": {
                    "label": "La Réunion",
                    "url": self.references["ile"]["La Réunion"]
                }
            }
        if lieu not in self.lieux_infos:
            return {}
        info = self.lieux_infos[lieu]
        zone = info["zone"]
        interco = info["intercommunalite"]
        if "Nord" in zone:
            region = "Nord"
        elif "Sud" in zone:
            region = "Sud"
        elif "Est" in zone:
            region = "Est"
        elif "Ouest" in zone:
            region = "Ouest"
        else:
            region = "Les Hauts"
        return {
            "zone": {
                "label": zone,
                "url": self.references["zone"].get(zone)
            },
            "intercommunalite": {
                "label": interco,
                "url": self.references["intercommunalite"].get(interco)
            },
            "region": {
                "label": region,
                "url": self.references["region"].get(region)
            },
            "ile": {
                "label": "La Réunion",
                "url": self.references["ile"]["La Réunion"]
            }
        }
    def calculer_moyenne_reunion(self, p_centrale):
        """Calcule la moyenne de production pour toutes les zones pour une puissance donnée."""
        centrale_data = next((c for c in self.centrales if c['puissance'] == p_centrale), self.centrales[0])
        
        zones_cles = [
            "Zone 1 (Ouest)", "Zone 2 (Est)", "Zone 3 (Les Hauts)", 
            "Zone 4 (Altitude >800m)", "Zone 5 (Nord)", "Zone 6 (Sud)"
        ]
        valeurs = []
        for zone in zones_cles:
            if zone in centrale_data:
                valeurs.append(centrale_data[zone])
        
        if not valeurs:
            return 4160 # Valeur de secours par défaut si rien n'est trouvé
        return int(sum(valeurs) / len(valeurs))
    def facteur_orientation(self, inclinaison, orientation):
        orientation_penalty = max(0, abs(orientation) - 30) * 0.003
        inclinaison_penalty = max(0, abs(inclinaison - 22)) * 0.005
        facteur = 1 - orientation_penalty - inclinaison_penalty
        return max(0.85, min(1.0, facteur))
    def get_zone_from_input(self, lieu_saisi):
        lieu_saisi = (lieu_saisi or "").strip().upper()
        if not lieu_saisi:
            return "La Réunion", "Toute l'île", "Multi-secteurs"
        villes_trouvees = []
        zone_detectee = None
        interco_detectee = None
        for commune, infos in self.lieux_infos.items():
            commune_upper = commune.upper()
            cp = infos["code_postal"]
            interco = infos["intercommunalite"].upper()
            zone_name = infos["zone"].upper()
            if (lieu_saisi in commune_upper or 
                lieu_saisi == cp or 
                lieu_saisi == interco or 
                lieu_saisi in zone_name):
                villes_trouvees.append(commune)
                if not zone_detectee:
                    zone_detectee = infos["zone"]
                    interco_detectee = infos["intercommunalite"]
        if villes_trouvees:
            villes_trouvees.sort()
            if len(villes_trouvees) > 15:
                description = " • ".join(villes_trouvees[:15]) + " ... (et autres)"
            else:
                description = " • ".join(villes_trouvees)
            return zone_detectee, description, interco_detectee
        return "La Réunion", "Toute l'île", "Multi-secteurs"
    
    def get_details_by_group(self, type_group, valeur):
        """
        Renvoie la liste des villes et la zone associée pour un groupe donné.
        type_group: 'intercommunalite' ou 'zone'
        """
        villes_trouvees = []
        zone_detectee = None
        valeur_clean = valeur.strip().upper()
        
        for ville, infos in self.lieux_infos.items():
            if infos[type_group].upper() == valeur_clean or infos[type_group].upper() in valeur_clean:
                villes_trouvees.append(ville)
                zone_detectee = infos['zone']
        return villes_trouvees, zone_detectee
    def calculer_recommandation(self, surface_dispo, budget_max, conso_mensuelle, zone):
        """Détermine la meilleure centrale selon les contraintes."""
        meilleure = self.centrales[0] 
        for c in self.centrales:
            nb_panneaux = int((c['puissance'] * 1000) / 500)
            prix_estim_total = nb_panneaux * (400 + 1333) # Matériel + Pose
            if c['taille'] <= surface_dispo and prix_estim_total <= budget_max:
                meilleure = c
        nb_p = int((meilleure['puissance'] * 1000) / 500)
        prod_a = meilleure.get(zone, 4536)
        return {
            "puissance": meilleure['puissance'],
            "nb_panneaux": nb_p,
            "surface_requise": nb_p * 2.2,
            "prix_total": int(nb_p * 1733),
            "prix_materiel": int(nb_p * 400),
            "prod_annuelle": prod_a,
            "conso_mensuelle": conso_mensuelle
        }
    def consommation_estimee(self, surface, budget):
        """
        Détermine la consommation mensuelle cible (kWh) en croisant 
        le budget disponible et la surface exploitable.
        """
        nb_panneaux_budget = int(budget / 1733)
        puissance_budget = (nb_panneaux_budget * 500) / 1000
        puissance_surface = (surface / 15) * 3
        puissance_cible = min(puissance_budget, puissance_surface)
        consommation_cible = puissance_cible * 115
        return round(consommation_cible, 1)
    def recommend_pv(self, surface, consommation_mensuelle, budget, zone):
        if consommation_mensuelle <= 300:
            besoin_reel = self.consommation_estimee(surface, budget)
        else:
            besoin_reel = consommation_mensuelle
        meilleure_centrale = self.centrales[0]
        for c in self.centrales:
            nb_p_test = int((c['puissance'] * 1000) / 500)
            prix_test = nb_p_test * 1033
            if c['taille'] <= surface and prix_test <= budget:
                meilleure_centrale = c
        p_centrale = meilleure_centrale['puissance']
        if zone == "La Réunion":
            p_annuelle = self.calculer_moyenne_reunion(p_centrale)
        else:
            p_annuelle = meilleure_centrale.get(zone, 4160)
        nb_panneaux = int((p_centrale * 1000) / 500)
        surface_reelle = round(nb_panneaux * 2.2, 1)
        prix_total_pose = int(nb_panneaux * 1733)
        p_mensuelle = round(p_annuelle / 12, 1)
        p_journaliere = round(p_annuelle / 365, 1)
        taux_couverture = round((p_mensuelle / besoin_reel) * 100)
        html = f"""
        <div class='energiX-tech-card'>
            <div class='energiX-tech-title'>Fiche Technique</div>
            <ul class='energiX-tech-list'>
                <li>📍 Secteur : {zone}</li>
                <li>🔌 Besoin : {besoin_reel} kWh/mois</li>
                <li>📏 Surface : {surface} m² | 💰 Budget : {budget} €</li>
            </ul>
            <p class='energiX-tech-highlight'>
                Puissance conseillée : {p_centrale} kWc
            </p>
            <div class='energiX-tech-grid'>
                <div class='energiX-tech-box'>
                    <span>MATÉRIEL</span><br>
                    <b>{nb_panneaux} panneaux</b>
                </div>
                <div class='energiX-tech-box'>
                    <span>BUDGET ESTIMÉ</span><br>
                    <b>{prix_total_pose} €</b>
                </div>
            </div>
            <div class='energiX-tech-performance'>
                <div class='energiX-perf-title'>Rendement estimé</div>

                <div class='energiX-perf-block'>
                    <div class='energiX-perf-label'>Année</div>
                    <div class='energiX-perf-value'>{p_annuelle} kWh</div>
                </div>
                <div class='energiX-perf-sep'></div>

                <div class='energiX-perf-block'>
                    <div class='energiX-perf-label'>Mois</div>
                    <div class='energiX-perf-value'>{p_mensuelle} kWh</div>
                </div>
                <div class='energiX-perf-sep'></div>
                <div class='energiX-perf-block'>
                    <div class='energiX-perf-label'>Jour</div>
                    <div class='energiX-perf-value'>{p_journaliere} kWh</div>
                </div>
            </div>
            <div class='energiX-tech-footer'>
                💡 <em>Couverture : Cette centrale assure {taux_couverture}% de votre autonomie.<br>
                Recommandation principale basée sur vos contraintes.</em>
            </div>
        </div>
        """
        return html, p_centrale, p_annuelle, p_mensuelle, p_journaliere, besoin_reel


