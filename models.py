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

        self.centrales_legacy = [
            {"taille": 15, "puissance": 3, "production_min": (4500, 5500)},
            {"taille": 30, "puissance": 6, "production_min": (9000, 11000)},
            {"taille": 45, "puissance": 9, "production_min": (13500, 16500)},
            {"taille": 60, "puissance": 12, "production_min": (18000, 22000)},
            {"taille": 75, "puissance": 15, "production_min": (22500, 27500)},
            {"taille": 90, "puissance": 18, "production_min": (27000, 33000)}
        ]

        self.prix_min_centrale_pose = 8000
    
    def facteur_orientation(self, inclinaison, orientation):
        orientation_penalty = max(0, abs(orientation) - 30) * 0.003
        inclinaison_penalty = max(0, abs(inclinaison - 22)) * 0.005
        facteur = 1 - orientation_penalty - inclinaison_penalty
        return max(0.85, min(1.0, facteur))

    def get_zone_from_input(self, lieu_saisi):
        # Nettoyage de la saisie
        lieu_saisi = (lieu_saisi or "").strip().upper()
        
        if not lieu_saisi:
            return "Zone 1 (Ouest)", "Toute l'île", "Non spécifiée"

        villes_trouvees = []
        zone_detectee = None
        interco_detectee = None

        # On parcourt notre base de données
        for commune, infos in self.lieux_infos.items():
            # Variables de comparaison
            commune_upper = commune.upper()
            cp = infos["code_postal"]
            interco = infos["intercommunalite"].upper()
            zone_name = infos["zone"].upper()

            # TEST DE CORRESPONDANCE :
            # Si la saisie est dans le nom de la ville, le CP, l'interco ou le nom de la zone
            if (lieu_saisi in commune_upper or 
                lieu_saisi == cp or 
                lieu_saisi == interco or 
                lieu_saisi in zone_name):
                
                villes_trouvees.append(commune)
                
                # On mémorise la zone et l'interco du premier résultat trouvé
                if not zone_detectee:
                    zone_detectee = infos["zone"]
                    interco_detectee = infos["intercommunalite"]

        # Si on a trouvé des villes
        if villes_trouvees:
            villes_trouvees.sort()
            # On limite l'affichage pour éviter de casser le design si la liste est trop longue
            if len(villes_trouvees) > 15:
                description = " • ".join(villes_trouvees[:15]) + " ... (et autres)"
            else:
                description = " • ".join(villes_trouvees)
                
            return zone_detectee, description, interco_detectee

        # 3. Fallback définitif si vraiment rien n'est trouvé
        return "Zone 1 (Ouest)", "Lieu non répertorié", "TCO"
    
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
        meilleure = self.centrales[0] # Par défaut 3 kWc
        
        for c in self.centrales:
            # Calcul du prix estimé pour cette centrale
            nb_panneaux = int((c['puissance'] * 1000) / 500)
            prix_estim_total = nb_panneaux * (400 + 1333) # Matériel + Pose
            
            if c['taille'] <= surface_dispo and prix_estim_total <= budget_max:
                meilleure = c
        
        # Données calculées pour le retour
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
        
    def recommend_pv(self, surface, consommation_mensuelle, budget, zone):
        # 1. Logique de sélection (3 kWc ou 6 kWc)
        p_centrale = 6 if surface >= 30 else 3
        
        # 2. Récupération des données de production selon la zone
        centrale_data = next((c for c in self.centrales if c['puissance'] == p_centrale), self.centrales[0])
        p_annuelle = centrale_data.get(zone, 4536)

        # 3. Calculs financiers et techniques détaillés
        nb_panneaux = int((p_centrale * 1000) / 500)
        surface_reelle = nb_panneaux * 2.2
        
        # Détail des prix
        prix_materiel_seul = int(nb_panneaux * 400)
        prix_total_pose = int(nb_panneaux * 1733)
        
        # Calculs de production
        p_mensuelle = round(p_annuelle / 12, 1)
        p_journaliere = round(p_annuelle / 365, 1)
        taux_couverture = round((p_mensuelle / consommation_mensuelle) * 100)

        # 4. Génération du HTML (Version épurée pour intégration)
        # Contenu épuré (Python)
        html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; color: #4B5563; padding: 10px 5px;">
            
            <div style="border-bottom: 2px solid #F0C300; margin-bottom: 15px; padding-bottom: 8px;">
                <p style="margin:0; color: #92400E; font-weight: bold; text-transform: uppercase; font-size: 0.8em; letter-spacing: 0.5px;">Fiche Technique</p>
            </div>

            <ul style="list-style:none; padding-left:0; font-size: 0.95em; line-height: 1.6; margin-bottom: 20px;">
                <li>📍 <b>Secteur :</b> {zone}</li>
                <li>🔌 <b>Besoin :</b> {consommation_mensuelle} kWh/mois</li>
                <li>📏 <b>Surface :</b> {surface} m² | 💰 <b>Budget :</b> {budget} €</li>
            </ul>
            
            <p style="color: #92400E; font-weight: bold; font-size: 1em; margin: 15px 0; text-align: center;">
                Puissance conseillée : {p_centrale} kWc
            </p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                <div style="background: #FFFBEB; padding: 12px; border-radius: 10px; border: 1px solid #FEF3C7; text-align: center;">
                    <span style="font-size: 0.75em; color: #B45309; font-weight: bold;">MATÉRIEL</span><br>
                    <b style="font-size: 1em;">{nb_panneaux} panneaux</b>
                </div>
                <div style="background: #FFFBEB; padding: 12px; border-radius: 10px; border: 1px solid #FEF3C7; text-align: center;">
                    <span style="font-size: 0.75em; color: #B45309; font-weight: bold;">BUDGET ESTIMÉ</span><br>
                    <b style="font-size: 1em;">{prix_total_pose} €</b>
                </div>
            </div>

            <div style="display: flex; justify-content: center; width: 100%; padding: 10px 0;">
    
                <div style="background: #1a1a1a; padding: 7px 25px; border-radius: 20px; color: #F0C300; display: flex; align-items: center; gap: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05); font-family: sans-serif;">
                    
                    <div style="border-right: 2px solid #F0C300; padding-right: 20px; font-weight: 700; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px; white-space: nowrap;">
                      Rendement Estimé
                    </div>

                    <div style="text-align: center;">
                        <div style="color: #8E8E8E; font-size: 0.7em; text-transform: uppercase; margin-bottom: 2px;">Annuel</div>
                        <div style="color: #FFF; font-weight: bold; font-size: 1.1em;">{p_annuelle} <small style="font-weight: normal; color: #8E8E8E; font-size: 0.7em;">kWh</small></div>
                    </div>

                    <div style="height: 25px; width: 1px; background: rgba(255,255,255,0.1);"></div>

                    <div style="text-align: center;">
                        <div style="color: #8E8E8E; font-size: 0.7em; text-transform: uppercase; margin-bottom: 2px;">Mensuel</div>
                        <div style="color: #FFF; font-weight: bold; font-size: 1.1em;">{p_mensuelle} <small style="font-weight: normal; color: #8E8E8E; font-size: 0.7em;">kWh</small></div>
                    </div>

                    <div style="height: 25px; width: 1px; background: rgba(255,255,255,0.1);"></div>

                    <div style="text-align: center;">
                        <div style="color: #8E8E8E; font-size: 0.7em; text-transform: uppercase; margin-bottom: 2px;">Journalier</div>
                        <div style="color: #F0C300; font-weight: 900; font-size: 1.1em;">{p_journaliere} <small style="font-weight: normal; color: #8E8E8E; font-size: 0.7em;">kWh</small></div>
                    </div>

                </div>
            </div>
            
            <p style="font-size: 0.85em; color: #4B5563; margin-top: 15px; padding: 10px; border-left: 3px solid #F0C300; background: #FFF9E3;">
                💡 <b>Couverture :</b> Ce système assure <b>{taux_couverture}%</b> de votre autonomie.
            </p>
        </div>
        """
        return html, p_centrale, p_annuelle, p_mensuelle, p_journaliere


    