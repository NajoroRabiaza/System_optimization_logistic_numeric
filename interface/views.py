from django.shortcuts import render


def index(request):
    return render(request, 'interface/index.html')


def resultats(request):
    return render(request, 'interface/resultats.html')


def scenarios(request):
    return render(request, 'interface/scenarios.html')


def historique(request):
    return render(request, 'interface/historique.html')