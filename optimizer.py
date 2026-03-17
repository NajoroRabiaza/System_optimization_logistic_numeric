# =============================================================
#  optimizer.py — Couche optimisation
#
#  Résout le problème de programmation linéaire avec
#  scipy.optimize.linprog (méthode du simplexe révisé).
#
#  On importe les fonctions de model.py pour construire
#  les matrices, puis on appelle le solveur scipy.
# =============================================================

from scipy.optimize import linprog
from model import construire_matrices_avec_extra


def resoudre(demandes, capacites, couts, regions, centres,
             centre_indisponible=None, interdire_C3_R4=False):
    """
    Résout le problème de transport et retourne la solution optimale.

    Paramètres :
      demandes           : dict {region: nb_requetes}
      capacites          : dict {centre: capacite_max}
      couts              : dict {centre: {region: cout_unitaire}}
      regions            : liste ['R1', 'R2', 'R3', 'R4']
      centres            : liste ['C1', 'C2', 'C3']
      centre_indisponible: nom d'un centre à désactiver (ex: 'C2') ou None
      interdire_C3_R4    : True si C3 ne peut pas traiter R4

    Retourne un dict avec :
      statut        : 'Optimal' ou 'Infaisable'
      cout_total    : coût minimum trouvé (entier) ou None
      flux          : liste de {region, centre, quantite}
      utilisation   : liste de {centre, charge, capacite, pourcentage}
      tableau_couts : liste de {region, centre, quantite, cout_unitaire, cout_total_ligne}
      message_erreur: texte si infaisable, sinon None
    """

    nb_centres = len(centres)

    # ── 1. Construire les matrices du modèle ──────────────────
    matrices = construire_matrices_avec_extra(
        regions, centres, demandes, capacites, couts,
        centre_indisponible=centre_indisponible,
        interdire_C3_R4=interdire_C3_R4,
    )

    c      = matrices['c']       # vecteur des coûts
    A_ub   = matrices['A_ub']    # matrice des capacités (inégalités ≤)
    b_ub   = matrices['b_ub']    # vecteur des capacités
    A_eq   = matrices['A_eq']    # matrice des demandes (égalités =)
    b_eq   = matrices['b_eq']    # vecteur des demandes
    bornes = matrices.get('bornes', [(0, None)] * matrices['nb_vars'])

    # ── 2. Appeler le solveur scipy ───────────────────────────
    # method='highs' est le plus fiable et le plus rapide
    resultat = linprog(
        c,
        A_ub=A_ub, b_ub=b_ub,
        A_eq=A_eq, b_eq=b_eq,
        bounds=bornes,
        method='highs',
    )

    # ── 3. Vérifier si une solution a été trouvée ─────────────
    if not resultat.success:
        return {
            'statut':        'Infaisable',
            'cout_total':    None,
            'flux':          [],
            'utilisation':   [],
            'tableau_couts': [],
            'message_erreur': (
                "Le solveur n'a pas trouvé de solution. "
                "Vérifiez que la capacité totale est suffisante."
            ),
        }

    # ── 4. Extraire les valeurs des variables x[i][j] ─────────
    x_sol = resultat.x  # tableau numpy des valeurs optimales

    # Coût total optimal (on arrondit car le solveur peut donner 19400.0000001)
    cout_total = round(resultat.fun)

    # ── 5. Construire la liste des flux ───────────────────────
    # Un flux = une affectation non nulle (region → centre, quantité)
    flux = []
    for i, region in enumerate(regions):
        for j, centre in enumerate(centres):
            k = i * nb_centres + j
            quantite = round(x_sol[k])
            if quantite > 0:
                flux.append({
                    'region':   region,
                    'centre':   centre,
                    'quantite': quantite,
                })

    # ── 6. Calculer l'utilisation de chaque centre ────────────
    utilisation = []
    for j, centre in enumerate(centres):
        # Charge = somme des requêtes envoyées à ce centre
        charge = sum(
            round(x_sol[i * nb_centres + j])
            for i in range(len(regions))
        )
        cap = capacites[centre]
        pourcentage = round(charge / cap * 100) if cap > 0 else 0

        utilisation.append({
            'centre':      centre,
            'charge':      charge,
            'capacite':    cap,
            'pourcentage': pourcentage,
        })

    # ── 7. Construire le tableau récapitulatif des coûts ──────
    tableau_couts = []
    for ligne in flux:
        r  = ligne['region']
        c_ = ligne['centre']
        q  = ligne['quantite']
        cu = couts[c_][r]
        tableau_couts.append({
            'region':          r,
            'centre':          c_,
            'quantite':        q,
            'cout_unitaire':   cu,
            'cout_total_ligne': cu * q,
        })

    return {
        'statut':        'Optimal',
        'cout_total':    cout_total,
        'flux':          flux,
        'utilisation':   utilisation,
        'tableau_couts': tableau_couts,
        'message_erreur': None,
    }


def verifier_contraintes(solution, demandes, capacites, regions, centres):
    """
    Vérifie automatiquement que la solution respecte toutes les contraintes.
    Retourne une liste de messages (vide = tout est correct).
    """
    violations = []
    flux = solution.get('flux', [])

    # Construire un dictionnaire quantite[region][centre]
    quantites = {r: {c: 0 for c in centres} for r in regions}
    for ligne in flux:
        quantites[ligne['region']][ligne['centre']] = ligne['quantite']

    # Vérifier les contraintes de demande
    for r in regions:
        total = sum(quantites[r][c] for c in centres)
        if abs(total - demandes[r]) > 1:  # tolérance de 1 requête (arrondi)
            violations.append(
                f"Demande non satisfaite pour {r} : "
                f"{total} traité ≠ {demandes[r]} demandé."
            )

    # Vérifier les contraintes de capacité
    for c in centres:
        total = sum(quantites[r][c] for r in regions)
        if total > capacites[c] + 1:  # tolérance de 1
            violations.append(
                f"Capacité dépassée pour {c} : "
                f"{total} > {capacites[c]}."
            )

    return violations
