from django.shortcuts import render
from .forms import DonneesForm


def index(request):
    form = DonneesForm(initial={
        'demande_R1': 1200,
        'demande_R2': 900,
        'demande_R3': 700,
        'demande_R4': 600,
        'capacite_C1': 1500,
        'capacite_C2': 1200,
        'capacite_C3': 1000,
        'cout_C1_R1': 5, 'cout_C1_R2': 6, 'cout_C1_R3': 7, 'cout_C1_R4': 8,
        'cout_C2_R1': 4, 'cout_C2_R2': 5, 'cout_C2_R3': 6, 'cout_C2_R4': 7,
        'cout_C3_R1': 6, 'cout_C3_R2': 4, 'cout_C3_R3': 5, 'cout_C3_R4': 6,
    })
    return render(request, 'interface/index.html', {'form': form})


def resultats(request):
    if request.method == 'POST':
        form = DonneesForm(request.POST)
        if form.is_valid():
            resultats_fictifs = {
                'cout_total': 19400,
                'statut': 'Optimal',
                'flux': [
                    {'region': 'R1', 'centre': 'C1', 'quantite': 600},
                    {'region': 'R1', 'centre': 'C2', 'quantite': 600},
                    {'region': 'R2', 'centre': 'C2', 'quantite': 600},
                    {'region': 'R2', 'centre': 'C3', 'quantite': 300},
                    {'region': 'R3', 'centre': 'C3', 'quantite': 700},
                    {'region': 'R4', 'centre': 'C1', 'quantite': 600},
                ],
                'utilisation': [
                    {'centre': 'C1', 'charge': 1200, 'capacite': 1500, 'pourcentage': 80},
                    {'centre': 'C2', 'charge': 1200, 'capacite': 1200, 'pourcentage': 100},
                    {'centre': 'C3', 'charge': 1000, 'capacite': 1000, 'pourcentage': 100},
                ],
            }
            return render(request, 'interface/resultats.html', {'resultats': resultats_fictifs})
        else:
            return render(request, 'interface/index.html', {'form': form})

    form = DonneesForm()
    return render(request, 'interface/index.html', {'form': form})


def scenarios(request):
    liste_scenarios = [
        {
            'numero': 1,
            'titre': 'Augmentation des requêtes',
            'description': 'Toutes les demandes par région augmentent de 20%.',
            'impact': 'Les centres risquent d\'être saturés.',
            'statut': 'Non calculé',
        },
        {
            'numero': 2,
            'titre': 'Réduction capacité C2',
            'description': 'La capacité du centre C2 est réduite de 25%.',
            'impact': 'Le flux doit être redistribué vers C1 et C3.',
            'statut': 'Non calculé',
        },
        {
            'numero': 3,
            'titre': 'Augmentation coûts C3',
            'description': 'Les coûts unitaires du centre C3 augmentent de 30%.',
            'impact': 'C3 devient moins attractif, le solveur privilégiera C1 et C2.',
            'statut': 'Non calculé',
        },
        {
            'numero': 4,
            'titre': 'Indisponibilité d\'un centre',
            'description': 'Le centre C2 est temporairement hors service.',
            'impact': 'Toute la charge de C2 est absorbée par C1 et C3.',
            'statut': 'Non calculé',
        },
        {
            'numero': 5,
            'titre': 'Contrainte métier personnalisée',
            'description': 'C3 ne peut pas traiter les requêtes de R4.',
            'impact': 'Les requêtes de R4 sont forcément traitées par C1 ou C2.',
            'statut': 'Non calculé',
        },
    ]
    return render(request, 'interface/scenarios.html', {'scenarios': liste_scenarios})


def historique(request):
    return render(request, 'interface/historique.html')