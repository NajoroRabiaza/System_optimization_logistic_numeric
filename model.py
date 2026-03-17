# =============================================================
#  model.py — Couche modélisation mathématique
#
#  Ce fichier décrit le problème sous forme mathématique.
#  Il ne résout rien — il explique juste la structure du modèle.
#
#  Problème de transport (programmation linéaire) :
#
#  Variables de décision :
#    x[i][j] = nombre de requêtes de la région Ri
#               envoyées au centre Cj
#
#  Fonction objectif (on veut minimiser le coût total) :
#    min  Σ_i Σ_j  couts[j][i] * x[i][j]
#
#  Contraintes de demande (chaque région doit être entièrement servie) :
#    Pour chaque région Ri :  Σ_j  x[i][j]  =  demandes[i]
#
#  Contraintes de capacité (chaque centre a une limite) :
#    Pour chaque centre Cj :  Σ_i  x[i][j]  ≤  capacites[j]
#
#  Contraintes de non-négativité (on ne peut pas traiter un nombre négatif) :
#    x[i][j]  ≥  0  pour tout i, j
# =============================================================

import numpy as np


def construire_matrices(regions, centres, demandes, capacites, couts):
    """
    Construit les matrices du problème de programmation linéaire.

    On ordonne les variables x[i][j] ainsi :
      index = i * nb_centres + j
      où i = index de la région, j = index du centre

    Retourne un dict avec :
      - c       : vecteur des coûts (fonction objectif)
      - A_ub    : matrice des contraintes de capacité (inégalités ≤)
      - b_ub    : vecteur des capacités
      - A_eq    : matrice des contraintes de demande (égalités =)
      - b_eq    : vecteur des demandes
      - nb_vars : nombre total de variables
    """
    nb_regions = len(regions)
    nb_centres = len(centres)
    nb_vars    = nb_regions * nb_centres  # ex: 4*3 = 12 variables

    # ── Vecteur des coûts c ──────────────────────────────────
    # c[k] = coût unitaire pour la variable k = x[i][j]
    c = np.zeros(nb_vars)
    for i, region in enumerate(regions):
        for j, centre in enumerate(centres):
            k = i * nb_centres + j
            c[k] = couts[centre][region]

    # ── Matrice A_ub (capacités) ─────────────────────────────
    # Pour chaque centre j :  Σ_i x[i][j] <= capacite[j]
    # Une ligne par centre
    A_ub = np.zeros((nb_centres, nb_vars))
    for j, centre in enumerate(centres):
        for i in range(nb_regions):
            k = i * nb_centres + j
            A_ub[j][k] = 1.0

    b_ub = np.array([capacites[c] for c in centres], dtype=float)

    # ── Matrice A_eq (demandes) ──────────────────────────────
    # Pour chaque région i :  Σ_j x[i][j] = demandes[i]
    # Une ligne par région
    A_eq = np.zeros((nb_regions, nb_vars))
    for i, region in enumerate(regions):
        for j in range(nb_centres):
            k = i * nb_centres + j
            A_eq[i][k] = 1.0

    b_eq = np.array([demandes[r] for r in regions], dtype=float)

    return {
        'c':       c,
        'A_ub':    A_ub,
        'b_ub':    b_ub,
        'A_eq':    A_eq,
        'b_eq':    b_eq,
        'nb_vars': nb_vars,
    }


def afficher_modele_dans_terminal(regions, centres, demandes, capacites, couts):
    """
    Affiche le modèle mathématique complet dans le terminal.
    Pratique pour déboguer ou vérifier le modèle à la main.
    """
    print("=" * 60)
    print("  MODÉLISATION MATHÉMATIQUE — PROBLÈME DE TRANSPORT")
    print("=" * 60)

    print("\n-- Variables de décision --")
    print("  x[Ri][Cj] = requêtes de Ri traitées par Cj (≥ 0)")
    print(f"  Nombre total de variables : {len(regions)} × {len(centres)} = {len(regions)*len(centres)}")

    print("\n-- Matrice des coûts unitaires --")
    header = f"{'':6}" + "".join(f"{c:8}" for c in centres)
    print("  " + header)
    for r in regions:
        ligne = f"  {r:6}" + "".join(f"{couts[c][r]:8}" for c in centres)
        print(ligne)

    print("\n-- Fonction objectif (minimiser) --")
    termes = []
    for r in regions:
        for c in centres:
            termes.append(f"{couts[c][r]}·x[{r}][{c}]")
    print("  min  " + " + ".join(termes))

    print("\n-- Contraintes de demande (égalités) --")
    for r in regions:
        eq = " + ".join([f"x[{r}][{c}]" for c in centres])
        print(f"  {eq}  =  {demandes[r]}")

    print("\n-- Contraintes de capacité (inégalités) --")
    for c in centres:
        ineq = " + ".join([f"x[{r}][{c}]" for r in regions])
        print(f"  {ineq}  ≤  {capacites[c]}")

    print("\n-- Non-négativité --")
    print("  x[Ri][Cj] ≥ 0  pour tout i, j")
    print("=" * 60)


def construire_matrices_avec_extra(regions, centres, demandes, capacites, couts,
                                   centre_indisponible=None, interdire_C3_R4=False):
    """
    Même chose que construire_matrices, mais avec des contraintes supplémentaires
    pour les scénarios.

    centre_indisponible : nom du centre à forcer à 0 (ex: 'C2')
    interdire_C3_R4     : si True, x[R4][C3] = 0
    """
    nb_regions = len(regions)
    nb_centres = len(centres)

    matrices = construire_matrices(regions, centres, demandes, capacites, couts)

    # Liste des bornes : par défaut (0, None) = x >= 0, pas de max
    bornes = [(0, None)] * matrices['nb_vars']

    # Si un centre est indisponible → forcer toutes ses variables à 0
    if centre_indisponible and centre_indisponible in centres:
        j = centres.index(centre_indisponible)
        for i in range(nb_regions):
            k = i * nb_centres + j
            bornes[k] = (0, 0)  # x[i][j] = 0

    # Si C3 ne peut pas traiter R4 → forcer x[R4][C3] = 0
    if interdire_C3_R4 and 'C3' in centres and 'R4' in regions:
        i = regions.index('R4')
        j = centres.index('C3')
        k = i * nb_centres + j
        bornes[k] = (0, 0)

    matrices['bornes'] = bornes
    return matrices
