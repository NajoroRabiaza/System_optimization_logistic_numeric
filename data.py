# =============================================================
#  data.py — Couche données
#  Contient les données initiales du problème logistique.
#  On peut modifier ces valeurs sans toucher au reste du code.
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

# Capacité maximale de chaque centre (nombre de requêtes qu'il peut traiter)
CAPACITES_INITIALES = {
    'C1': 1500,
    'C2': 1200,
    'C3': 1000,
}

# Coût unitaire de traitement : COUTS[centre][region] = coût par requête
# Exemple : COUTS['C1']['R1'] = 5  signifie que C1 facture 5 par requête de R1
COUTS_INITIAUX = {
    'C1': {'R1': 5, 'R2': 6, 'R3': 7, 'R4': 8},
    'C2': {'R1': 4, 'R2': 5, 'R3': 6, 'R4': 7},
    'C3': {'R1': 6, 'R2': 4, 'R3': 5, 'R4': 6},
}


def get_donnees_initiales():
    """
    Retourne une copie des données initiales du problème.
    On retourne des copies pour éviter de modifier l'original.
    """
    import copy
    return {
        'regions': list(REGIONS),
        'centres': list(CENTRES),
        'demandes': copy.deepcopy(DEMANDES_INITIALES),
        'capacites': copy.deepcopy(CAPACITES_INITIALES),
        'couts': copy.deepcopy(COUTS_INITIAUX),
    }
