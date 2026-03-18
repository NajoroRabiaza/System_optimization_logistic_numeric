# =============================================================
#  optimizer.py — Couche optimisation
#
#  Résout le problème de programmation linéaire avec
#  scipy.optimize.linprog (méthode HiGHS).
#
#  extensions ajoutees :
#    - Extension A : prise en compte de la contrainte énergétique
#    - Extension B : prise en compte de la contrainte de latence
# =============================================================

from scipy.optimize import linprog
from model import construire_matrices_avec_extra


def resoudre(
    demandes, capacites, couts, regions, centres,
    centre_indisponible=None,
    interdire_C3_R4=False,
    # ── Paramètres Extension A : énergie ──
    activer_contrainte_energie=False,
    energie=None,
    emax=None,
    # ── Paramètres Extension B : latence ──
    activer_contrainte_latence=False,
    latences=None,
    latence_max=35,
):
    """
    Résout le problème de transport et retourne la solution optimale.
    Accepte maintenant des paramètres pour les contraintes avancées.
    """
    nb_centres = len(centres)

    # ── 1. Construire les matrices ────────────────────────────
    matrices = construire_matrices_avec_extra(
        regions, centres, demandes, capacites, couts,
        centre_indisponible=centre_indisponible,
        interdire_C3_R4=interdire_C3_R4,
        activer_contrainte_energie=activer_contrainte_energie,
        energie=energie,
        emax=emax,
        activer_contrainte_latence=activer_contrainte_latence,
        latences=latences,
        latence_max=latence_max,
    )

    c      = matrices['c']
    A_ub   = matrices['A_ub']
    b_ub   = matrices['b_ub']
    A_eq   = matrices['A_eq']
    b_eq   = matrices['b_eq']
    bornes = matrices.get('bornes', [(0, None)] * matrices['nb_vars'])

    # ── 2. Appeler le solveur ─────────────────────────────────
    resultat = linprog(
        c,
        A_ub=A_ub, b_ub=b_ub,
        A_eq=A_eq, b_eq=b_eq,
        bounds=bornes,
        method='highs',
    )

    # ── 3. Vérifier si une solution existe ────────────────────
    if not resultat.success:
        return {
            'statut':        'Infaisable',
            'cout_total':    None,
            'flux':          [],
            'utilisation':   [],
            'tableau_couts': [],
            'energie_totale': None,
            'message_erreur': (
                "Le solveur n'a pas trouvé de solution. "
                "Les contraintes sont peut-être trop restrictives."
            ),
        }

    # ── 4. Extraire les valeurs optimales ─────────────────────
    x_sol      = resultat.x
    cout_total = round(resultat.fun)

    # ── 5. Construire la liste des flux ───────────────────────
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

    # ── 6. Calculer l'utilisation des centres ─────────────────
    utilisation = []
    for j, centre in enumerate(centres):
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

    # ── 7. Tableau récapitulatif des coûts ────────────────────
    tableau_couts = []
    for ligne in flux:
        r  = ligne['region']
        c_ = ligne['centre']
        q  = ligne['quantite']
        cu = couts[c_][r]
        tableau_couts.append({
            'region':           r,
            'centre':           c_,
            'quantite':         q,
            'cout_unitaire':    cu,
            'cout_total_ligne': cu * q,
        })

    # ── 8. EXTENSION A : Calculer l'énergie totale consommée ──
    # On calcule l'énergie même si la contrainte n'est pas activée
    # pour toujours l'afficher dans les résultats.
    energie_totale = 0
    if energie:
        for ligne in flux:
            energie_totale += energie[ligne['centre']] * ligne['quantite']
    energie_totale = round(energie_totale, 1)

    return {
        'statut':         'Optimal',
        'cout_total':     cout_total,
        'flux':           flux,
        'utilisation':    utilisation,
        'tableau_couts':  tableau_couts,
        'energie_totale': energie_totale,
        'emax':           emax,
        'message_erreur': None,
    }


def verifier_contraintes(solution, demandes, capacites, regions, centres):
    """
    Vérifie que la solution respecte toutes les contraintes.
    Retourne une liste de violations (vide = tout est correct).
    """
    violations = []
    flux = solution.get('flux', [])

    quantites = {r: {c: 0 for c in centres} for r in regions}
    for ligne in flux:
        quantites[ligne['region']][ligne['centre']] = ligne['quantite']

    for r in regions:
        total = sum(quantites[r][c] for c in centres)
        if abs(total - demandes[r]) > 1:
            violations.append(
                f"Demande non satisfaite pour {r} : "
                f"{total} traité ≠ {demandes[r]} demandé."
            )

    for c in centres:
        total = sum(quantites[r][c] for r in regions)
        if total > capacites[c] + 1:
            violations.append(
                f"Capacité dépassée pour {c} : {total} > {capacites[c]}."
            )

    return violations
