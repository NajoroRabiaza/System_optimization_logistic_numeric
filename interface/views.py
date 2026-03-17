# =============================================================
#  views.py — Couche IHM (vues Django)
#
#  Chaque fonction est une "vue" = une page de l'application.
#  Quand l'utilisateur clique sur quelque chose, Django appelle
#  la vue correspondante et renvoie une page HTML.
#
#  On importe les modules d'optimisation pour faire de vrais calculs.
#  On utilise la session Django pour mémoriser l'historique.
# =============================================================

import sys
import os

# Ajouter le dossier racine du projet au chemin Python
# pour pouvoir importer data.py, model.py, optimizer.py, validator.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import DonneesForm

# Importation de nos modules d'optimisation
from data      import get_donnees_initiales, REGIONS, CENTRES
from validator import valider_donnees
from optimizer import resoudre, verifier_contraintes


# =============================================================
#  Fonctions utilitaires (privées, pas des vues)
# =============================================================

def _lire_historique(request):
    """Lit l'historique stocké dans la session Django."""
    return request.session.get('historique', [])


def _sauvegarder_dans_historique(request, nom, resultat, donnees):
    """
    Ajoute un calcul à l'historique de la session.
    On stocke le nom, la date, le statut, le coût et les données utilisées.
    """
    historique = _lire_historique(request)

    numero = len(historique) + 1
    date   = timezone.now().strftime('%d/%m/%Y %H:%M')

    entree = {
        'numero':    numero,
        'nom':       nom,
        'date':      date,
        'statut':    resultat['statut'],
        'cout_total': resultat['cout_total'],
        # On sauvegarde aussi les détails pour la comparaison
        'flux':        resultat.get('flux', []),
        'utilisation': resultat.get('utilisation', []),
        'donnees_utilisees': {
            'demandes':  donnees['demandes'],
            'capacites': donnees['capacites'],
        },
    }

    historique.append(entree)
    request.session['historique'] = historique
    # Forcer Django a sauvegarder la session (important !)
    request.session.modified = True

    return entree


def _extraire_donnees_du_formulaire(form_data):
    """
    Lit les données saisies dans le formulaire et les retourne
    sous forme de dicts utilisables par l'optimizer.
    """
    demandes = {
        'R1': form_data['demande_R1'],
        'R2': form_data['demande_R2'],
        'R3': form_data['demande_R3'],
        'R4': form_data['demande_R4'],
    }
    capacites = {
        'C1': form_data['capacite_C1'],
        'C2': form_data['capacite_C2'],
        'C3': form_data['capacite_C3'],
    }
    couts = {
        'C1': {
            'R1': form_data['cout_C1_R1'],
            'R2': form_data['cout_C1_R2'],
            'R3': form_data['cout_C1_R3'],
            'R4': form_data['cout_C1_R4'],
        },
        'C2': {
            'R1': form_data['cout_C2_R1'],
            'R2': form_data['cout_C2_R2'],
            'R3': form_data['cout_C2_R3'],
            'R4': form_data['cout_C2_R4'],
        },
        'C3': {
            'R1': form_data['cout_C3_R1'],
            'R2': form_data['cout_C3_R2'],
            'R3': form_data['cout_C3_R3'],
            'R4': form_data['cout_C3_R4'],
        },
    }
    return demandes, capacites, couts


# =============================================================
#  Vue 1 : Accueil — saisie des données
# =============================================================

@login_required
def index(request):
    """
    Page d'accueil : affiche le formulaire avec les données initiales.
    L'utilisateur peut modifier les valeurs et lancer l'optimisation.
    """
    donnees = get_donnees_initiales()

    form = DonneesForm(initial={
        'demande_R1': donnees['demandes']['R1'],
        'demande_R2': donnees['demandes']['R2'],
        'demande_R3': donnees['demandes']['R3'],
        'demande_R4': donnees['demandes']['R4'],
        'capacite_C1': donnees['capacites']['C1'],
        'capacite_C2': donnees['capacites']['C2'],
        'capacite_C3': donnees['capacites']['C3'],
        'cout_C1_R1': donnees['couts']['C1']['R1'],
        'cout_C1_R2': donnees['couts']['C1']['R2'],
        'cout_C1_R3': donnees['couts']['C1']['R3'],
        'cout_C1_R4': donnees['couts']['C1']['R4'],
        'cout_C2_R1': donnees['couts']['C2']['R1'],
        'cout_C2_R2': donnees['couts']['C2']['R2'],
        'cout_C2_R3': donnees['couts']['C2']['R3'],
        'cout_C2_R4': donnees['couts']['C2']['R4'],
        'cout_C3_R1': donnees['couts']['C3']['R1'],
        'cout_C3_R2': donnees['couts']['C3']['R2'],
        'cout_C3_R3': donnees['couts']['C3']['R3'],
        'cout_C3_R4': donnees['couts']['C3']['R4'],
    })
    return render(request, 'interface/index.html', {'form': form})


# =============================================================
#  Vue 2 : Résultats — optimisation réelle
# =============================================================

@login_required
def resultats(request):
    """
    Page des résultats.
    Reçoit les données du formulaire (POST), lance le vrai solveur,
    affiche les résultats, et sauvegarde dans l'historique.
    """
    if request.method != 'POST':
        return redirect('interface:index')

    form = DonneesForm(request.POST)

    if not form.is_valid():
        return render(request, 'interface/index.html', {'form': form})

    # ── 1. Lire les données du formulaire ──────────────────
    demandes, capacites, couts = _extraire_donnees_du_formulaire(form.cleaned_data)
    regions = REGIONS
    centres = CENTRES

    # ── 2. Valider les données ─────────────────────────────
    est_valide, erreurs = valider_donnees(demandes, capacites, couts, regions, centres)

    if not est_valide:
        return render(request, 'interface/index.html', {
            'form': form,
            'erreurs_validation': erreurs,
        })

    # ── 3. Lancer l'optimisation ───────────────────────────
    solution = resoudre(demandes, capacites, couts, regions, centres)

    # ── 4. Vérifier les contraintes (contrôle qualité) ─────
    violations = verifier_contraintes(solution, demandes, capacites, regions, centres)
    solution['violations'] = violations

    # ── 5. Sauvegarder dans l'historique ──────────────────
    donnees_init = get_donnees_initiales()
    if demandes == donnees_init['demandes'] and capacites == donnees_init['capacites']:
        nom_calcul = "Situation initiale"
    else:
        nom_calcul = "Situation personnalisée"

    _sauvegarder_dans_historique(
        request,
        nom=nom_calcul,
        resultat=solution,
        donnees={'demandes': demandes, 'capacites': capacites},
    )

    return render(request, 'interface/resultats.html', {
        'resultats':    solution,
        'violations':   violations,
        'nom_scenario': nom_calcul,
    })


# =============================================================
#  Vue 3 : Scénarios — liste + boutons fonctionnels
# =============================================================

@login_required
def scenarios(request):
    """
    Page des scénarios.
    Affiche la liste des scénarios prédéfinis avec des boutons fonctionnels.
    """
    liste_scenarios = [
        {
            'numero':      1,
            'titre':       'Augmentation des requêtes (+20%)',
            'description': 'Toutes les demandes par région augmentent de 20%.',
            'impact':      "Les centres risquent d'être saturés. Le coût va augmenter.",
        },
        {
            'numero':      2,
            'titre':       'Réduction capacité C2 (−25%)',
            'description': 'La capacité du centre C2 est réduite de 25%.',
            'impact':      'Le flux doit être redistribué vers C1 et C3.',
        },
        {
            'numero':      3,
            'titre':       'Augmentation coûts C3 (+30%)',
            'description': 'Les coûts unitaires du centre C3 augmentent de 30%.',
            'impact':      'C3 devient moins attractif ; le solveur préférera C1 et C2.',
        },
        {
            'numero':      4,
            'titre':       'Indisponibilité de C2',
            'description': 'Le centre C2 est temporairement hors service (capacité = 0).',
            'impact':      'Toute la charge de C2 est absorbée par C1 et C3.',
        },
        {
            'numero':      5,
            'titre':       'Contrainte métier : C3 interdit pour R4',
            'description': 'Le centre C3 ne peut pas traiter les requêtes de la région R4.',
            'impact':      'Les requêtes de R4 seront traitées uniquement par C1 ou C2.',
        },
    ]
    return render(request, 'interface/scenarios.html', {'scenarios': liste_scenarios})


# =============================================================
#  Vue 4 : Lancer un scénario
# =============================================================

@login_required
def lancer_scenario(request, numero):
    """
    Lance l'optimisation pour un scénario donné.
    Modifie les données initiales selon les règles du scénario,
    appelle le solveur, sauvegarde dans l'historique, et affiche les résultats.
    """
    donnees = get_donnees_initiales()
    regions  = donnees['regions']
    centres  = donnees['centres']
    demandes  = donnees['demandes']
    capacites = donnees['capacites']
    couts     = donnees['couts']

    centre_indisponible = None
    interdire_C3_R4     = False

    if numero == 1:
        nom_scenario = "Scénario 1 — Demandes +20%"
        for r in regions:
            demandes[r] = round(demandes[r] * 1.20)

    elif numero == 2:
        nom_scenario = "Scénario 2 — Capacité C2 −25%"
        capacites['C2'] = round(capacites['C2'] * 0.75)

    elif numero == 3:
        nom_scenario = "Scénario 3 — Coûts C3 +30%"
        for r in regions:
            couts['C3'][r] = round(couts['C3'][r] * 1.30, 2)

    elif numero == 4:
        nom_scenario = "Scénario 4 — C2 indisponible"
        centre_indisponible = 'C2'

    elif numero == 5:
        nom_scenario = "Scénario 5 — C3 interdit pour R4"
        interdire_C3_R4 = True

    else:
        return redirect('interface:scenarios')

    est_valide, erreurs = valider_donnees(demandes, capacites, couts, regions, centres)
    if not est_valide:
        return render(request, 'interface/scenarios.html', {
            'scenarios':       _liste_scenarios_predef(),
            'erreur_scenario': erreurs,
        })

    solution = resoudre(
        demandes, capacites, couts, regions, centres,
        centre_indisponible=centre_indisponible,
        interdire_C3_R4=interdire_C3_R4,
    )
    violations = verifier_contraintes(solution, demandes, capacites, regions, centres)
    solution['violations'] = violations

    _sauvegarder_dans_historique(
        request,
        nom=nom_scenario,
        resultat=solution,
        donnees={'demandes': demandes, 'capacites': capacites},
    )

    return render(request, 'interface/resultats.html', {
        'resultats':    solution,
        'violations':   violations,
        'nom_scenario': nom_scenario,
    })


def _liste_scenarios_predef():
    """Helper : retourne la liste des scénarios pour le template."""
    return [
        {'numero': 1, 'titre': 'Augmentation des requêtes (+20%)',
         'description': 'Toutes les demandes augmentent de 20%.',
         'impact': "Les centres risquent d'être saturés."},
        {'numero': 2, 'titre': 'Réduction capacité C2 (−25%)',
         'description': 'La capacité de C2 est réduite de 25%.',
         'impact': 'Le flux doit être redistribué.'},
        {'numero': 3, 'titre': 'Augmentation coûts C3 (+30%)',
         'description': 'Les coûts de C3 augmentent de 30%.',
         'impact': 'C3 devient moins attractif.'},
        {'numero': 4, 'titre': 'Indisponibilité de C2',
         'description': 'C2 est hors service.',
         'impact': 'C1 et C3 absorbent tout.'},
        {'numero': 5, 'titre': 'Contrainte métier : C3 interdit pour R4',
         'description': 'C3 ne peut pas traiter R4.',
         'impact': 'R4 va vers C1 ou C2 uniquement.'},
    ]


# =============================================================
#  Vue 5 : Historique — tous les calculs effectués
# =============================================================

@login_required
def historique(request):
    """
    Page de l'historique.
    Affiche tous les calculs effectués depuis le lancement de l'application.
    Les données sont stockées dans la session Django.
    """
    if request.method == 'POST' and request.POST.get('action') == 'vider':
        request.session['historique'] = []
        request.session.modified = True
        return redirect('interface:historique')

    liste = _lire_historique(request)

    return render(request, 'interface/historique.html', {
        'historique': liste,
    })


# =============================================================
#  Vue 6 : Comparaison — deux scénarios côte à côte
# =============================================================

@login_required
def comparaison(request):
    """
    Page de comparaison.
    Compare deux calculs de l'historique côte à côte.
    Par défaut : premier calcul vs dernier calcul.
    """
    liste = _lire_historique(request)

    if len(liste) < 2:
        return render(request, 'interface/comparaison.html', {
            'pas_assez_de_donnees': True,
            'nb_calculs': len(liste),
        })

    # Par défaut : comparer le premier et le dernier
    idx_a = 0
    idx_b = len(liste) - 1

    # L'utilisateur peut choisir via l'URL : ?a=1&b=3
    try:
        idx_a = max(0, int(request.GET.get('a', 1)) - 1)
        idx_b = max(0, int(request.GET.get('b', len(liste))) - 1)
        idx_a = min(idx_a, len(liste) - 1)
        idx_b = min(idx_b, len(liste) - 1)
    except (ValueError, TypeError):
        pass

    scenario_a = liste[idx_a]
    scenario_b = liste[idx_b]

    difference_cout = None
    if scenario_a['cout_total'] and scenario_b['cout_total']:
        difference_cout = scenario_b['cout_total'] - scenario_a['cout_total']

    return render(request, 'interface/comparaison.html', {
        'scenario_a':       scenario_a,
        'scenario_b':       scenario_b,
        'difference_cout':  difference_cout,
        'liste_historique': liste,
        'idx_a':            idx_a + 1,
        'idx_b':            idx_b + 1,
    })
