document.addEventListener("DOMContentLoaded", () => {

    const left = document.querySelector(".left-arrow");
    const right = document.querySelector(".right-arrow");

    if (!left || !right) return;

    // Normalisation du chemin (supprime les paramètres GET)
    let path = window.location.pathname.split("?")[0];

    const routes = {
        "/recommendation": { left: "/",               right: "/conso_prod" },
        "/conso_prod":     { left: "/recommendation", right: "/graph" },
        "/graph":          { left: "/conso_prod",     right: "/dashboard" },
        "/dashboard":      { left: "/graph",          right: null }
    };

    const current = routes[path];
    if (!current) return;

    // Flèche gauche
    if (current.left === null) {
        left.style.pointerEvents = "none";
        left.style.opacity = "0.25";
    } else {
        left.addEventListener("click", () => {
            window.location.href = current.left;
        });
    }

    // Flèche droite
    if (current.right === null) {
        right.style.pointerEvents = "none";
        right.style.opacity = "0";
    } else {
        right.addEventListener("click", () => {
            window.location.href = current.right;
        });
    }
});
document.querySelector(".left-hover-zone")?.addEventListener("click", () => {
    document.querySelector(".left-arrow")?.click();
});

document.querySelector(".right-hover-zone")?.addEventListener("click", () => {
    document.querySelector(".right-arrow")?.click();
});
