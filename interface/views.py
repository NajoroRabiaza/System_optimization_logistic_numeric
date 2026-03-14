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
    # Fausses données pour construire l'affichage
    # Ces valeurs seront remplacées par la vraie solution du solveur plus tard
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


def scenarios(request):
    return render(request, 'interface/scenarios.html')


def historique(request):
    return render(request, 'interface/historique.html')