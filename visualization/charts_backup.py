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

    valeurs = {
        'C1': [0, 0, 0, 0],
        'C2': [0, 0, 0, 0],
        'C3': [0, 0, 0, 0],
    }

    for ligne in donnees_flux:
        region_index = regions.index(ligne['region'])
        valeurs[ligne['centre']][region_index] = ligne['quantite']

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


def generer_graphique_capacites(donnees_utilisation, chemin_sortie):
    """
    Génère un graphique en barres horizontales montrant la charge
    de chaque centre par rapport à sa capacité maximale.
    Sauvegarde l'image en PNG dans chemin_sortie.
    """

    centres = [ligne['centre'] for ligne in donnees_utilisation]
    charges = [ligne['charge'] for ligne in donnees_utilisation]
    capacites = [ligne['capacite'] for ligne in donnees_utilisation]
    pourcentages = [ligne['pourcentage'] for ligne in donnees_utilisation]

    # Couleur de chaque barre selon le taux d'utilisation
    couleurs = []
    for pct in pourcentages:
        if pct >= 90:
            couleurs.append('#e74c3c')
        elif pct >= 70:
            couleurs.append('#f39c12')
        else:
            couleurs.append('#2ecc71')

    x = np.arange(len(centres))
    largeur = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))

    # Barres de capacité maximale en gris en arrière-plan
    ax.bar(
        x,
        capacites,
        largeur + 0.2,
        label='Capacité maximale',
        color='#ecf0f1',
        edgecolor='#bdc3c7',
        zorder=1,
    )

    # Barres de charge par-dessus
    ax.bar(
        x,
        charges,
        largeur,
        label='Charge actuelle',
        color=couleurs,
        zorder=2,
    )

    # Afficher le pourcentage au-dessus de chaque barre
    for i, (charge, pct) in enumerate(zip(charges, pourcentages)):
        ax.text(
            i,
            charge + 20,
            f'{pct}%',
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=11,
        )

    ax.set_title('Utilisation des capacités par centre')
    ax.set_xlabel('Centres de traitement')
    ax.set_ylabel('Nombre de requêtes')
    ax.set_xticks(x)
    ax.set_xticklabels(centres)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(chemin_sortie, dpi=100)
    plt.close()