# =============================================================
#  data.py — Couche données
#  Contient toutes les données initiales du problème logistique.
#  On peut modifier ces valeurs sans toucher au reste du code.
#
#  extensions ajoutees :
#    - ENERGIE     : consommation énergétique par requête par centre
#    - EMAX        : limite globale d'énergie autorisée
#    - LATENCES    : latence réseau entre chaque région et chaque centre
#    - LATENCE_MAX : latence maximale acceptable (en ms)
# =============================================================

# Liste des régions qui envoient des requêtes
REGIONS = ['R1', 'R2', 'R3', 'R4']

# Liste des centres de traitement
CENTRES = ['C1', 'C2', 'C3']

# Nombre de requêtes à traiter pour chaque région
DEMANDES_INITIALES = {
    'R1': 1200,
    'R2': 900,
    'R3': 700,
    'R4': 600,
}

# Capacité maximale de chaque centre
CAPACITES_INITIALES = {
    'C1': 1500,
    'C2': 1200,
    'C3': 1000,
}

# Coût unitaire de traitement : COUTS[centre][region] = coût par requête
COUTS_INITIAUX = {
    'C1': {'R1': 5, 'R2': 6, 'R3': 7, 'R4': 8},
    'C2': {'R1': 4, 'R2': 5, 'R3': 6, 'R4': 7},
    'C3': {'R1': 6, 'R2': 4, 'R3': 5, 'R4': 6},
}

# ── EXTENSION A : Contrainte énergétique ──────────────────────
# Chaque centre consomme un certain nombre d'unités d'énergie
# par requête traitée (donné dans le sujet).
ENERGIE_PAR_REQUETE = {
    'C1': 2.0,    # C1 consomme 2 unités d'énergie par requête
    'C2': 1.5,    # C2 consomme 1.5 unités
    'C3': 2.5,    # C3 consomme 2.5 unités (le plus énergivore)
}

# Limite globale d'énergie : la somme de toute l'énergie consommée
# par tous les centres ne doit pas dépasser cette valeur.
# Calcul : si on utilisait tous les centres à fond →
#   C1: 1500*2=3000, C2: 1200*1.5=1800, C3: 1000*2.5=2500 → total max = 7300
# On fixe Emax à 7000 pour que la contrainte soit légèrement restrictive.
EMAX = 7000

# ── EXTENSION B : Contrainte de latence ───────────────────────
# Latence réseau (en ms) entre chaque région et chaque centre.
# Source : tableau du sujet (section 3.1).
# LATENCES[region][centre] = latence en millisecondes
LATENCES = {
    'R1': {'C1': 20, 'C2': 30, 'C3': 40},
    'R2': {'C1': 25, 'C2': 15, 'C3': 35},
    'R3': {'C1': 30, 'C2': 20, 'C3': 25},
    'R4': {'C1': 50, 'C2': 30, 'C3': 15},
}

# Latence maximale acceptable : les flux qui dépassent cette limite
# sont INTERDITS (la variable x[i][j] est forcée à 0).
LATENCE_MAX = 35  # en millisecondes


def get_donnees_initiales():
    """
    Retourne une copie des données initiales du problème.
    On retourne des copies pour éviter de modifier l'original.
    """
    import copy
    return {
        'regions':   list(REGIONS),
        'centres':   list(CENTRES),
        'demandes':  copy.deepcopy(DEMANDES_INITIALES),
        'capacites': copy.deepcopy(CAPACITES_INITIALES),
        'couts':     copy.deepcopy(COUTS_INITIAUX),
        'energie':   copy.deepcopy(ENERGIE_PAR_REQUETE),
        'emax':      EMAX,
        'latences':  copy.deepcopy(LATENCES),
        'latence_max': LATENCE_MAX,
    }
