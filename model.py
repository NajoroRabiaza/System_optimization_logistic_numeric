# =============================================================
#  model.py — Couche modélisation mathématique
#
#  Ce fichier traduit le problème logistique en matrices
#  pour que scipy puisse le résoudre.
#
#  EXTENSIONS AJOUTÉES (Jour 5-6) :
#    - Extension A : contrainte énergétique (nouvelle ligne dans A_ub)
#    - Extension B : contrainte de latence (bornes forcées à 0)
# =============================================================

import numpy as np


def construire_matrices(regions, centres, demandes, capacites, couts):
    """
    Construit les matrices de base du problème LP.

    Variables x[i][j] : requêtes de Ri vers Cj
    Index linéaire    : k = i * nb_centres + j

    Retourne : c, A_ub, b_ub, A_eq, b_eq, nb_vars
    """
    nb_regions = len(regions)
    nb_centres = len(centres)
    nb_vars    = nb_regions * nb_centres

    # ── Vecteur des coûts ────────────────────────────────────
    c = np.zeros(nb_vars)
    for i, region in enumerate(regions):
        for j, centre in enumerate(centres):
            k = i * nb_centres + j
            c[k] = couts[centre][region]

    # ── Contraintes de capacité (inégalités ≤) ───────────────
    # Pour chaque centre j : Σ_i x[i][j] ≤ capacite[j]
    A_ub = np.zeros((nb_centres, nb_vars))
    for j, centre in enumerate(centres):
        for i in range(nb_regions):
            k = i * nb_centres + j
            A_ub[j][k] = 1.0

    b_ub = np.array([capacites[c] for c in centres], dtype=float)

    # ── Contraintes de demande (égalités =) ──────────────────
    # Pour chaque région i : Σ_j x[i][j] = demandes[i]
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


def construire_matrices_avec_extra(
    regions, centres, demandes, capacites, couts,
    centre_indisponible=None,
    interdire_C3_R4=False,
    activer_contrainte_energie=False,
    energie=None,
    emax=None,
    activer_contrainte_latence=False,
    latences=None,
    latence_max=35,
):
    """
    Construit les matrices du problème avec les contraintes avancées.

    Paramètres supplémentaires (extensions jour 5-6) :
      activer_contrainte_energie : True = ajouter la contrainte énergétique
      energie                    : dict {centre: conso par requête}
      emax                       : limite globale d'énergie
      activer_contrainte_latence : True = interdire les flux trop lents
      latences                   : dict {region: {centre: latence ms}}
      latence_max                : seuil maximal acceptable (ms)
    """
    nb_regions = len(regions)
    nb_centres = len(centres)

    # Partir des matrices de base
    matrices = construire_matrices(regions, centres, demandes, capacites, couts)

    A_ub   = matrices['A_ub']
    b_ub   = matrices['b_ub']
    nb_vars = matrices['nb_vars']

    # Bornes initiales : x[k] >= 0, pas de maximum
    bornes = [(0, None)] * nb_vars

    # ── Centre indisponible → forcer toutes ses variables à 0 ─
    if centre_indisponible and centre_indisponible in centres:
        j = centres.index(centre_indisponible)
        for i in range(nb_regions):
            k = i * nb_centres + j
            bornes[k] = (0, 0)

    # ── Interdire C3 pour R4 ──────────────────────────────────
    if interdire_C3_R4 and 'C3' in centres and 'R4' in regions:
        i = regions.index('R4')
        j = centres.index('C3')
        k = i * nb_centres + j
        bornes[k] = (0, 0)

    # ────────────────────────────────────────────────────────────
    # EXTENSION A : Contrainte énergétique
    # ────────────────────────────────────────────────────────────
    # La contrainte dit : la somme de toute l'énergie consommée
    # par tous les flux ne doit pas dépasser Emax.
    #
    # Formule : Σ_i Σ_j  energie[j] * x[i][j]  ≤  Emax
    #
    # On ajoute UNE NOUVELLE LIGNE à la fin de A_ub.
    # Cette ligne contient le coefficient énergétique de chaque variable.
    # ────────────────────────────────────────────────────────────
    if activer_contrainte_energie and energie and emax:

        # Créer le vecteur de la nouvelle contrainte (une ligne)
        ligne_energie = np.zeros(nb_vars)
        for i in range(nb_regions):
            for j, centre in enumerate(centres):
                k = i * nb_centres + j
                # Coefficient = consommation énergétique du centre j
                ligne_energie[k] = energie[centre]

        # Ajouter cette ligne à A_ub (empiler verticalement)
        A_ub = np.vstack([A_ub, ligne_energie])
        # Ajouter la limite Emax à b_ub
        b_ub = np.append(b_ub, float(emax))

    # ────────────────────────────────────────────────────────────
    # EXTENSION B : Contrainte de latence
    # ────────────────────────────────────────────────────────────
    # Pour chaque paire (region, centre), si la latence dépasse
    # latence_max, on INTERDIT ce flux en forçant x[i][j] = 0.
    #
    # C'est exactement le même mécanisme que centre_indisponible
    # mais appliqué paire par paire.
    # ────────────────────────────────────────────────────────────
    if activer_contrainte_latence and latences:

        for i, region in enumerate(regions):
            for j, centre in enumerate(centres):
                latence = latences.get(region, {}).get(centre, 0)
                if latence > latence_max:
                    k = i * nb_centres + j
                    bornes[k] = (0, 0)  # flux interdit
                    # Pour le débogage : on peut voir quels flux sont bloqués
                    # print(f"LATENCE: {region}→{centre} = {latence}ms > {latence_max}ms → bloqué")

    matrices['A_ub']   = A_ub
    matrices['b_ub']   = b_ub
    matrices['bornes'] = bornes
    return matrices
