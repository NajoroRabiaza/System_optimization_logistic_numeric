from django.shortcuts import render, redirect


def index(request):
    return render(request, 'interface/index.html')


def resultats(request):
    if request.method != 'POST':
        return redirect('interface:index')
    return render(request, 'interface/resultats.html')


def scenarios(request):
    return render(request, 'interface/scenarios.html')


def historique(request):
    return render(request, 'interface/historique.html')