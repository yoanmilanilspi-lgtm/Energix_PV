/* ENERGIX PV */
console.log("🚀 Java.js chargé par Flask");
const rawLieux = document.getElementById("data-lieux")?.textContent;
let DATA_LIEUX = {};
let ALL_LIEUX = [];
if (rawLieux) {
    DATA_LIEUX = JSON.parse(rawLieux);
    ALL_LIEUX = [
        ...DATA_LIEUX.ville,
        ...DATA_LIEUX.intercommunalite,
        ...DATA_LIEUX.code_postal,
        ...DATA_LIEUX.zone
    ];
} else {
    console.warn("DATA_LIEUX non présent (normal hors index)");
}
console.log(DATA_LIEUX);
document.addEventListener('DOMContentLoaded', function () {
    const conso = document.getElementById('consommation_mensuelle');
    const nb = document.getElementById('nb_occupants');
    const catSelect = document.getElementById('categorie');
    const zoneInput = document.getElementById('zone_ville_cp');
    const zoneList = document.getElementById('zone-list');
    function toggleInputs() {
        if (conso.value) {
            nb.disabled = true;
            nb.closest('.form-group').classList.add('grayed');
        } else if (nb.value) {
            conso.disabled = true;
            conso.closest('.form-group').classList.add('grayed');
        } else {
            nb.disabled = false;
            conso.disabled = false;
            nb.closest('.form-group').classList.remove('grayed');
            conso.closest('.form-group').classList.remove('grayed');
        }
    }
    if (conso && nb) {
        conso.addEventListener('input', toggleInputs);
        nb.addEventListener('input', toggleInputs);
    }
    if (catSelect && zoneList) {
        catSelect.addEventListener('change', function() {
            const cat = this.value;
            zoneList.innerHTML = '';
            const options = cat ? DATA_LIEUX[cat] : ALL_LIEUX;
            const sortedOptions = [...options].sort();
            sortedOptions.forEach(opt => {
                const el = document.createElement('option');
                el.value = opt;
                zoneList.appendChild(el);
            });
        });
        catSelect.dispatchEvent(new Event('change'));
    }
});
const panel = document.querySelector('.mix-float-panel');
const trigger = document.querySelector('.mix-float-trigger');
const card = document.querySelector('.mix-card');
if (trigger && panel && card) {
    trigger.addEventListener('click', () => {
        panel.classList.toggle('open');
        trigger.classList.toggle('open');
    });

    panel.addEventListener('click', (e) => {
        if (!card.contains(e.target)) {
            panel.classList.remove('open');
            trigger.classList.remove('open');
        }
    });
}
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    console.log("✅ PWA Ready : L'événement d'installation est capturé !");
});
window.showIosInstructions = function() {
    const message = "Pour installer EnergiX PV sur votre iPhone :\n\n" +
                    "1. Appuyez sur le bouton 'Partager' en bas de Safari.\n" +
                    "2. Appuyez sur 'Sur l'écran d'accueil'.\n" +
                    "3. Appuyez sur 'Ajouter'.";

    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    if (!isIOS) {
        alert("Cette option est optimisée pour Safari sur iPhone/iPad.");
    } else {
        alert(message);
    }
};
document.addEventListener('DOMContentLoaded', function() {
    console.log("📂 DOM Ready - Initialisation globale");
    const downloadSection = document.querySelector('.app-download-section');
    if (downloadSection && window.innerWidth > 992) {
        downloadSection.addEventListener('mouseenter', () => downloadSection.setAttribute('open', ''));
        downloadSection.addEventListener('mouseleave', () => downloadSection.removeAttribute('open'));
    }
    const btnAndroid = document.getElementById('btn-android');
    if (btnAndroid) {
        btnAndroid.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const link = document.createElement('a');
            link.href = "/static/downloads/energix.apk";
            link.download = "energix.apk";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }
    const btnWindows = document.getElementById('btn-windows');
    if (btnWindows) {
        btnWindows.addEventListener('click', async () => {
            if (window.deferredPrompt) {
                window.deferredPrompt.prompt();
                await window.deferredPrompt.userChoice;
                window.deferredPrompt = null;
            } else {
                alert("Installation PWA impossible.\nUtilisez Chrome/Edge ou vérifiez que vous êtes en HTTPS.");
            }
        });
    }
    const btnMac = document.getElementById('btn-mac');
    if (btnMac) btnMac.onclick = () => window.location.href = "/static/downloads/energix.dmg";
    const btnLinux = document.getElementById('btn-linux');
    if (btnLinux) btnLinux.onclick = () => window.location.href = "/static/downloads/energix.deb";
    const btnWinZip = document.getElementById('btn-win');
    if (btnWinZip) btnWinZip.onclick = () => window.location.href = "/static/downloads/EnergiX_Solaire_Reunion.zip";
    const btnIos = document.getElementById('btn-ios');
    if (btnIos) btnIos.onclick = () => window.showIosInstructions();
    document.querySelectorAll('details').forEach((el) => {
        el.addEventListener('toggle', () => {
            if (el.open) {
                setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
            }
        });
    });
    const veCheckbox = document.getElementById("enable_ve");
    const veOptions = document.getElementById("ve_options");
    if (veCheckbox && veOptions) {
        const toggleVeOptions = () => {
            if (veCheckbox.checked) {
                veOptions.style.display = "flex";
                veOptions.style.opacity = "0";
                veOptions.style.transform = "translateY(-10px)";
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
        if (veCheckbox.checked) veOptions.style.display = "flex";
    }
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
    const remoteTrigger = document.querySelector('.remote-trigger');
    const remoteTab = document.querySelector('.report-remote-tab');
    if (remoteTrigger && remoteTab) {
        remoteTrigger.addEventListener('click', () => {
            remoteTab.classList.toggle('active');
        });
    }
});
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
function updateClock() {
    const timeEl = document.getElementById('energi-time');
    const dateEl = document.getElementById('energi-date');
    if (!timeEl || !dateEl) return;
    const now = new Date();
    const optionsTime = { hour: '2-digit', minute: '2-digit', timeZone: 'Indian/Reunion' };
    const optionsDate = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Indian/Reunion' };
    timeEl.textContent = now.toLocaleTimeString('fr-FR', optionsTime);
    dateEl.textContent = capitalize(now.toLocaleDateString('fr-FR', optionsDate));
}
async function updateBattery() {
    const batteryEl = document.getElementById('energi-battery');
    if (!batteryEl) return;

    if (!navigator.getBattery) {
        batteryEl.textContent = "🔋";
        return;
    }
    const battery = await navigator.getBattery();
    const level = Math.round(battery.level * 100);

    batteryEl.innerHTML = `
        <div class="battery-icon">
            <div class="battery-level" style="width:${level}%;"></div>
        </div>
        ${level}%
    `;
}
document.addEventListener("DOMContentLoaded", () => {
    updateClock();
    updateBattery();
    setInterval(updateClock, 1000);
    setInterval(updateBattery, 5000);
});
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        fetch('https://energix-pv.goatcounter.com/counter/total.json')
            .then(response => response.json())
            .then(data => {
                const textElement = document.getElementById('visitor-text-pv');
                if (textElement) {
                    const n = data.count || 0;
                    const label = n > 1 ? "VUES" : "VUE";
                    textElement.innerText = n > 0
                        ? `${n.toLocaleString()} ${label}`
                        : "EN LIGNE";
                }
            })
            .catch(() => {
                const textElement = document.getElementById('visitor-text-pv');
                if (textElement) {
                    textElement.innerText = `15 Visites`;
                }
                console.log("Stats PV en attente ou bloquées");
            });
    }, 1000);
});
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Java.js chargé par Flask");

    const bloc = document.getElementById('secteurs-collapse');
    const header = bloc ? bloc.querySelector('.energiX-collapse-header') : null;
    if (!bloc || !header) return;
    header.addEventListener('click', () => {
        bloc.classList.toggle('open');
    });
});
document.addEventListener("DOMContentLoaded", () => {
    if (document.body.id !== "page-recommandation") return;
    const rec = document.querySelector("#recommandation-principale");
    if (!rec) return;
    const details = rec.closest("details");
    if (!details) return;
    const content = details.querySelector(".result-content");
    if (!content) return;
    const updateSelection = () => {
        const raw = content.innerText.trim();
        if (raw.length < 20) return;
        const text = raw
            .normalize("NFKD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/\s+/g, " ")
            .trim();
        const match = text.match(/Puissance conseillee\s*:\s*(\d+)\s*kWc/i);
        if (!match) return;
        const puissance = parseInt(match[1]);
        document.querySelectorAll(".pv-table tr").forEach(tr => {
            const rowText = tr.innerText
                .normalize("NFKD")
                .replace(/[\u0300-\u036f]/g, "")
                .replace(/\s+/g, " ")
                .trim();
            const regex = new RegExp(`\\b${puissance}\\s*kWc\\b`, "i");
            tr.classList.toggle("selected", regex.test(rowText));
        });
    };
    details.addEventListener("toggle", () => {
        if (details.open) setTimeout(updateSelection, 50);
    });
    setTimeout(updateSelection, 250);
    const tableDetails = document.querySelector("#tailles-centrales")?.closest("details");
    if (tableDetails) {
        tableDetails.addEventListener("toggle", () => {
            if (tableDetails.open) setTimeout(updateSelection, 50);
        });
    }
});
document.addEventListener("DOMContentLoaded", function () {
    function openCollapseFromHash() {
        const hash = window.location.hash;
        if (!hash) return;
        const target = document.querySelector(hash);
        if (!target) return;
        if (target.tagName.toLowerCase() === "details") {
            target.setAttribute("open", "open");
            setTimeout(() => {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 150);
        }
    }
    openCollapseFromHash();
    document.querySelectorAll('.remote-nav a[href^="#"]').forEach(link => {
        link.addEventListener("click", function () {
            const id = this.getAttribute("href");
            const target = document.querySelector(id);

            if (target && target.tagName.toLowerCase() === "details") {
                target.setAttribute("open", "open");
                setTimeout(() => {
                    target.scrollIntoView({ behavior: "smooth", block: "start" });
                }, 150);
            }
        });
    });
    const link = document.querySelector('a[href="#config-form"]');
    const summary = document.getElementById("config-summary");

    if (link && summary) {
        link.addEventListener("click", function () {
            setTimeout(() => {
                summary.setAttribute("open", "open");
            }, 200);
        });
    }
    const veCheckbox = document.getElementById("enable_ve");
    const veOptions = document.getElementById("ve_options");

    if (veCheckbox && veOptions) {
        veCheckbox.addEventListener("change", function () {
            veOptions.style.display = this.checked ? "block" : "none";
        });
    }
});
document.addEventListener("DOMContentLoaded", () => {
    const intro = document.getElementById("intro-video-container");
    const video = document.getElementById("intro-video");
	const introEnabled = document.body.dataset.intro === "True";
    let inactivityTimer;
    const INACTIVITY_DELAY = 60000; // 1 minute
    function showIntro() {
        intro.style.display = "flex";
        intro.style.opacity = "1";
        video.currentTime = 0;
        video.play();
    }
    function hideIntro() {
        intro.style.opacity = "0";
        setTimeout(() => {
            intro.style.display = "none";
        }, 800);
    }
    function resetInactivityTimer() {
        clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(showIntro, INACTIVITY_DELAY);
    }
    if (introEnabled) {
        showIntro();
    }
    resetInactivityTimer();
    ["mousemove", "keydown", "click", "scroll", "touchstart"].forEach(evt => {
        window.addEventListener(evt, resetInactivityTimer);
    });
    intro.addEventListener("click", hideIntro);
	window.addEventListener("keydown", hideIntro);
    window.addEventListener("scroll", () => {
        if (window.scrollY > 20) hideIntro();
    });
});






























