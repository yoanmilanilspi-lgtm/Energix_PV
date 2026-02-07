/**
 * AUSTRAL SOLAR - Client-side Logic
 * Optimisé pour le nouveau thème Premium
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // === 1. ACCORDÉONS & GRAPHIQUES ===
    // On cible tous les détails (menu, recommandation, graphiques)
    const detailsElements = document.querySelectorAll('details');
    detailsElements.forEach((el) => {
        el.addEventListener('toggle', () => {
            if (el.open) {
                // Si l'accordéon contient un graphique Plotly, on force le redimensionnement
                setTimeout(() => {
                    window.dispatchEvent(new Event('resize'));
                }, 50);
            }
        });
    });

    // === 2. FORMULAIRE DYNAMIQUE (BORNE VE) ===
    const veCheckbox = document.getElementById("enable_ve");
    const veOptions = document.getElementById("ve_options");

    if (veCheckbox && veOptions) {
        const toggleVeOptions = () => {
            if (veCheckbox.checked) {
                veOptions.style.display = "flex"; // "flex" pour l'alignement du nouveau thème
                veOptions.style.opacity = "0";
                veOptions.style.transform = "translateY(-10px)";
                
                // Animation fluide
                setTimeout(() => {
                    veOptions.style.transition = "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)";
                    veOptions.style.opacity = "1";
                    veOptions.style.transform = "translateY(0)";
                }, 10);
            } else {
                veOptions.style.display = "none";
            }
        };
        veCheckbox.addEventListener("change", toggleVeOptions);
        // Initialisation sans animation au chargement
        if (veCheckbox.checked) veOptions.style.display = "flex";
    }

    // === 3. ANIMATION DU BOUTON DE SOUMISSION ===
    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', function() {
            const btn = this.querySelector('button[type="submit"]');
            if (btn) {
                btn.innerHTML = '⚡ <span style="margin-left:8px">Calcul en cours...</span>';
                btn.style.pointerEvents = "none";
                btn.style.filter = "grayscale(0.5)";
            }
        });
    }

    // === 4. MENU REMOTE (NAVIGATION) ===
    const remoteTrigger = document.querySelector('.remote-trigger');
    const remoteTab = document.querySelector('.report-remote-tab');
    if (remoteTrigger && remoteTab) {
        remoteTrigger.addEventListener('click', () => {
            remoteTab.classList.toggle('active');
        });
    }

    // === 5. BANDEAU DYNAMIQUE (ACCUEIL) ===
    const triggerZone = document.getElementById('trigger-zone');
    const band = document.getElementById('collapsible-band');
    const arrow = document.getElementById('state-arrow');

    if (triggerZone && band) {
        triggerZone.onclick = function(e) {
            e.preventDefault();
            const isClosed = band.style.maxHeight === "0px" || band.style.maxHeight === "";
            
            if (isClosed) {
                band.style.maxHeight = "60px";
                band.style.opacity = "1";
                band.style.marginTop = "8px";
                if (arrow) arrow.style.transform = "rotate(180deg)";
            } else {
                band.style.maxHeight = "0px";
                band.style.opacity = "0";
                band.style.marginTop = "0px";
                if (arrow) arrow.style.transform = "rotate(0deg)";
            }
        };
    }
});