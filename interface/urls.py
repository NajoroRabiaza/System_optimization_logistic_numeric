from django.urls import path
from . import views

app_name = 'interface'

urlpatterns = [
    path('',                                    views.index,                   name='index'),
    path('resultats/',                          views.resultats,               name='resultats'),
    path('scenarios/',                          views.scenarios,               name='scenarios'),
    path('scenarios/lancer/<int:numero>/',      views.lancer_scenario,         name='lancer_scenario'),
    path('historique/',                         views.historique,              name='historique'),
    path('comparaison/',                        views.comparaison,             name='comparaison'),
    # Extension C : JSON
    path('sauvegarder-json/',                   views.sauvegarder_scenario_json, name='sauvegarder_json'),
    path('charger-json/',                       views.charger_scenario_json,   name='charger_json'),
    # Export CSV
    path('exporter-csv/',                       views.exporter_csv,            name='exporter_csv'),
]
