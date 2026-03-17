# =============================================================
#  views.py — Couche IHM (vues Django)
#
#  EXTENSIONS AJOUTÉES (Jour 5-6) :
#    - Extension A : scénario avec contrainte énergétique
#    - Extension B : scénario avec contrainte de latence
#    - Extension C : sauvegarde et chargement de scénarios en JSON
# =============================================================

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, JsonResponse

from .forms import DonneesForm
from data      import get_donnees_initiales, REGIONS, CENTRES
from validator import valider_donnees
from optimizer import resoudre, verifier_contraintes


# =============================================================
#  Fonctions utilitaires
# =============================================================

def _lire_historique(request):
    return request.session.get('historique', [])


def _sauvegarder_dans_historique(request, nom, resultat, donnees):
    historique = _lire_historique(request)
    numero = len(historique) + 1
    date   = timezone.now().strftime('%d/%m/%Y %H:%M')

    entree = {
        'numero':    numero,
        'nom':       nom,
        'date':      date,
        'statut':    resultat['statut'],
        'cout_total': resultat['cout_total'],
        'flux':        resultat.get('flux', []),
        'utilisation': resultat.get('utilisation', []),
        'energie_totale': resultat.get('energie_totale'),
        'donnees_utilisees': {
            'demandes':  donnees['demandes'],
            'capacites': donnees['capacites'],
        },
    }

    historique.append(entree)
    request.session['historique'] = historique
    request.session.modified = True
    return entree


def _extraire_donnees_du_formulaire(form_data):
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
            'R1': form_data['cout_C1_R1'], 'R2': form_data['cout_C1_R2'],
            'R3': form_data['cout_C1_R3'], 'R4': form_data['cout_C1_R4'],
        },
        'C2': {
            'R1': form_data['cout_C2_R1'], 'R2': form_data['cout_C2_R2'],
            'R3': form_data['cout_C2_R3'], 'R4': form_data['cout_C2_R4'],
        },
        'C3': {
            'R1': form_data['cout_C3_R1'], 'R2': form_data['cout_C3_R2'],
            'R3': form_data['cout_C3_R3'], 'R4': form_data['cout_C3_R4'],
        },
    }
    return demandes, capacites, couts


def _liste_scenarios_predef():
    return [
        {'numero': 1, 'titre': 'Augmentation des requêtes (+20%)',
         'description': 'Toutes les demandes augmentent de 20%.',
         'impact': "Les centres risquent d'être saturés.",
         'extension': False},
        {'numero': 2, 'titre': 'Réduction capacité C2 (−25%)',
         'description': 'La capacité de C2 est réduite de 25%.',
         'impact': 'Le flux doit être redistribué.',
         'extension': False},
        {'numero': 3, 'titre': 'Augmentation coûts C3 (+30%)',
         'description': 'Les coûts de C3 augmentent de 30%.',
         'impact': 'C3 devient moins attractif.',
         'extension': False},
        {'numero': 4, 'titre': 'Indisponibilité de C2',
         'description': 'C2 est hors service.',
         'impact': 'C1 et C3 absorbent tout.',
         'extension': False},
        {'numero': 5, 'titre': 'Contrainte métier : C3 interdit pour R4',
         'description': 'C3 ne peut pas traiter R4.',
         'impact': 'R4 va vers C1 ou C2 uniquement.',
         'extension': False},
        # ── Extensions jour 5-6 ──────────────────────────────
        {'numero': 6, 'titre': '⚡ Extension A — Contrainte énergétique',
         'description': 'La consommation totale d\'énergie est limitée à 7000 unités. '
                        'C1=2u/req, C2=1.5u/req, C3=2.5u/req.',
         'impact': 'Le solveur favorise C2 (moins énergivore). Le coût peut augmenter.',
         'extension': True},
        {'numero': 7, 'titre': '📡 Extension B — Contrainte de latence (35ms max)',
         'description': 'Les flux dont la latence dépasse 35ms sont interdits. '
                        'Ex: R4→C1 (50ms) et R1→C3 (40ms) sont bloqués.',
         'impact': 'Certaines paires région-centre sont interdites. '
                   'La solution change et peut coûter plus cher.',
         'extension': True},
        {'numero': 8, 'titre': '⚡📡 Extension A+B — Énergie ET Latence combinées',
         'description': 'Les deux contraintes sont actives en même temps.',
         'impact': 'Le problème est plus contraint. Le solveur doit satisfaire '
                   'les deux limitations simultanément.',
         'extension': True},
    ]


# =============================================================
#  Vue 1 : Accueil
# =============================================================

@login_required
def index(request):
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
#  Vue 2 : Résultats
# =============================================================

@login_required
def resultats(request):
    if request.method != 'POST':
        return redirect('interface:index')

    form = DonneesForm(request.POST)
    if not form.is_valid():
        return render(request, 'interface/index.html', {'form': form})

    demandes, capacites, couts = _extraire_donnees_du_formulaire(form.cleaned_data)
    regions = REGIONS
    centres = CENTRES

    est_valide, erreurs = valider_donnees(demandes, capacites, couts, regions, centres)
    if not est_valide:
        return render(request, 'interface/index.html', {
            'form': form,
            'erreurs_validation': erreurs,
        })

    donnees_init = get_donnees_initiales()
    solution = resoudre(
        demandes, capacites, couts, regions, centres,
        energie=donnees_init['energie'],
    )

    violations = verifier_contraintes(solution, demandes, capacites, regions, centres)
    solution['violations'] = violations

    if demandes == donnees_init['demandes'] and capacites == donnees_init['capacites']:
        nom_calcul = "Situation initiale"
    else:
        nom_calcul = "Situation personnalisée"

    _sauvegarder_dans_historique(
        request, nom=nom_calcul, resultat=solution,
        donnees={'demandes': demandes, 'capacites': capacites},
    )

    return render(request, 'interface/resultats.html', {
        'resultats':    solution,
        'violations':   violations,
        'nom_scenario': nom_calcul,
    })


# =============================================================
#  Vue 3 : Scénarios
# =============================================================

@login_required
def scenarios(request):
    return render(request, 'interface/scenarios.html', {
        'scenarios': _liste_scenarios_predef()
    })


# =============================================================
#  Vue 4 : Lancer un scénario
# =============================================================

@login_required
def lancer_scenario(request, numero):
    donnees = get_donnees_initiales()
    regions  = donnees['regions']
    centres  = donnees['centres']
    demandes  = donnees['demandes']
    capacites = donnees['capacites']
    couts     = donnees['couts']
    energie   = donnees['energie']
    latences  = donnees['latences']
    emax      = donnees['emax']
    latence_max = donnees['latence_max']

    centre_indisponible          = None
    interdire_C3_R4              = False
    activer_contrainte_energie   = False
    activer_contrainte_latence   = False

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

    # ── Extensions jour 5-6 ──────────────────────────────────

    elif numero == 6:
        # Extension A : contrainte énergétique
        nom_scenario = "Extension A — Contrainte énergétique (Emax=7000)"
        activer_contrainte_energie = True

    elif numero == 7:
        # Extension B : contrainte de latence
        nom_scenario = "Extension B — Contrainte de latence (max 35ms)"
        activer_contrainte_latence = True

    elif numero == 8:
        # Extensions A + B combinées
        nom_scenario = "Extension A+B — Énergie ET Latence"
        activer_contrainte_energie = True
        activer_contrainte_latence = True

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
        activer_contrainte_energie=activer_contrainte_energie,
        energie=energie,
        emax=emax,
        activer_contrainte_latence=activer_contrainte_latence,
        latences=latences,
        latence_max=latence_max,
    )

    violations = verifier_contraintes(solution, demandes, capacites, regions, centres)
    solution['violations'] = violations

    _sauvegarder_dans_historique(
        request, nom=nom_scenario, resultat=solution,
        donnees={'demandes': demandes, 'capacites': capacites},
    )

    return render(request, 'interface/resultats.html', {
        'resultats':    solution,
        'violations':   violations,
        'nom_scenario': nom_scenario,
    })


# =============================================================
#  Vue 5 : Historique
# =============================================================

@login_required
def historique(request):
    if request.method == 'POST' and request.POST.get('action') == 'vider':
        request.session['historique'] = []
        request.session.modified = True
        return redirect('interface:historique')

    return render(request, 'interface/historique.html', {
        'historique': _lire_historique(request),
    })


# =============================================================
#  Vue 6 : Comparaison
# =============================================================

@login_required
def comparaison(request):
    liste = _lire_historique(request)

    if len(liste) < 2:
        return render(request, 'interface/comparaison.html', {
            'pas_assez_de_donnees': True,
            'nb_calculs': len(liste),
        })

    idx_a = 0
    idx_b = len(liste) - 1

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


# =============================================================
#  EXTENSION C : Sauvegarde et chargement JSON
# =============================================================

@login_required
def sauvegarder_scenario_json(request):
    """
    Sauvegarde le dernier calcul de l'historique en fichier JSON.
    Le fichier est téléchargé directement par le navigateur.
    """
    historique = _lire_historique(request)

    if not historique:
        return redirect('interface:index')

    # On prend le dernier calcul effectué
    dernier = historique[-1]

    # Construire le contenu JSON à sauvegarder
    # On inclut tout ce qui permet de reconstruire et comprendre le calcul
    contenu = {
        'nom':        dernier['nom'],
        'date':       dernier['date'],
        'statut':     dernier['statut'],
        'cout_total': dernier['cout_total'],
        'energie_totale': dernier.get('energie_totale'),
        'flux':       dernier.get('flux', []),
        'utilisation': dernier.get('utilisation', []),
        'donnees_utilisees': dernier.get('donnees_utilisees', {}),
        'info': 'Fichier généré par Logistics Optimizer — Projet L3 Informatique'
    }

    # Convertir en texte JSON bien formaté (indent=2 pour la lisibilité)
    contenu_json = json.dumps(contenu, ensure_ascii=False, indent=2)

    # Créer un nom de fichier propre basé sur le nom du scénario
    nom_fichier = dernier['nom'].replace(' ', '_').replace('—', '-')
    nom_fichier = ''.join(c for c in nom_fichier if c.isalnum() or c in '_-')
    nom_fichier = f"scenario_{nom_fichier[:40]}.json"

    # Retourner le fichier comme téléchargement
    response = HttpResponse(contenu_json, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{nom_fichier}"'
    return response


@login_required
def charger_scenario_json(request):
    """
    Charge un fichier JSON précédemment sauvegardé et l'ajoute à l'historique.
    Le fichier est uploadé via un formulaire POST.
    """
    if request.method != 'POST':
        return redirect('interface:scenarios')

    fichier = request.FILES.get('fichier_json')

    if not fichier:
        return render(request, 'interface/scenarios.html', {
            'scenarios':       _liste_scenarios_predef(),
            'erreur_chargement': "Aucun fichier sélectionné.",
        })

    # Vérifier que c'est bien un fichier .json
    if not fichier.name.endswith('.json'):
        return render(request, 'interface/scenarios.html', {
            'scenarios':         _liste_scenarios_predef(),
            'erreur_chargement': "Le fichier doit être au format .json",
        })

    try:
        # Lire et décoder le fichier JSON
        contenu = json.loads(fichier.read().decode('utf-8'))

        # Construire une entrée d'historique à partir du JSON chargé
        historique = _lire_historique(request)
        numero = len(historique) + 1

        entree = {
            'numero':    numero,
            'nom':       contenu.get('nom', 'Scénario chargé') + ' (importé)',
            'date':      timezone.now().strftime('%d/%m/%Y %H:%M') + ' [chargé]',
            'statut':    contenu.get('statut', 'Inconnu'),
            'cout_total': contenu.get('cout_total'),
            'flux':        contenu.get('flux', []),
            'utilisation': contenu.get('utilisation', []),
            'energie_totale': contenu.get('energie_totale'),
            'donnees_utilisees': contenu.get('donnees_utilisees', {}),
        }

        historique.append(entree)
        request.session['historique'] = historique
        request.session.modified = True

        # Rediriger vers la page résultats pour afficher le scénario chargé
        return render(request, 'interface/resultats.html', {
            'resultats':    entree,
            'violations':   [],
            'nom_scenario': entree['nom'],
            'depuis_json':  True,   # flag pour afficher un badge spécial
        })

    except (json.JSONDecodeError, KeyError) as e:
        return render(request, 'interface/scenarios.html', {
            'scenarios':         _liste_scenarios_predef(),
            'erreur_chargement': f"Fichier JSON invalide : {str(e)}",
        })


@login_required
def exporter_csv(request):
    """
    Exporte le dernier calcul de l'historique en fichier CSV.
    """
    import csv
    historique = _lire_historique(request)

    if not historique:
        return redirect('interface:index')

    dernier = historique[-1]

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="resultats.csv"'
    response.write('\ufeff')  # BOM UTF-8 pour Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Logistics Optimizer — Export CSV'])
    writer.writerow(['Scénario :', dernier['nom']])
    writer.writerow(['Date :', dernier['date']])
    writer.writerow(['Statut :', dernier['statut']])
    writer.writerow(['Coût total :', dernier['cout_total']])
    if dernier.get('energie_totale') is not None:
        writer.writerow(['Énergie totale consommée :', dernier['energie_totale']])
    writer.writerow([])
    writer.writerow(['Région', 'Centre', 'Requêtes traitées'])
    for ligne in dernier.get('flux', []):
        writer.writerow([ligne['region'], ligne['centre'], ligne['quantite']])
    writer.writerow([])
    writer.writerow(['Centre', 'Charge', 'Capacité', 'Utilisation (%)'])
    for u in dernier.get('utilisation', []):
        writer.writerow([u['centre'], u['charge'], u['capacite'], u['pourcentage']])

    return response
