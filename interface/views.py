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
    return render(request, 'interface/resultats.html')


def scenarios(request):
    return render(request, 'interface/scenarios.html')


def historique(request):
    return render(request, 'interface/historique.html')