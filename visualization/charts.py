import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os


def generer_graphique_flux(donnees_flux, chemin_sortie):
    """
    Génère un graphique en barres groupées de la répartition des flux.
    Sauvegarde l'image en PNG dans chemin_sortie.
    """

    regions = ['R1', 'R2', 'R3', 'R4']
    centres = ['C1', 'C2', 'C3']
    couleurs = ['#2980b9', '#27ae60', '#e67e22']

    # Construire la matrice de flux : valeurs[centre][region]
    valeurs = {
        'C1': [0, 0, 0, 0],
        'C2': [0, 0, 0, 0],
        'C3': [0, 0, 0, 0],
    }

    for ligne in donnees_flux:
        region_index = regions.index(ligne['region'])
        valeurs[ligne['centre']][region_index] = ligne['quantite']

    # Paramètres du graphique
    x = np.arange(len(regions))
    largeur = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))

    for i, centre in enumerate(centres):
        ax.bar(
            x + i * largeur,
            valeurs[centre],
            largeur,
            label=centre,
            color=couleurs[i],
        )

    ax.set_title('Répartition des flux par région et par centre')
    ax.set_xlabel('Régions')
    ax.set_ylabel('Nombre de requêtes')
    ax.set_xticks(x + largeur)
    ax.set_xticklabels(regions)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(chemin_sortie, dpi=100)
    plt.close()