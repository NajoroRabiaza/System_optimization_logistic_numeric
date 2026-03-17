from django.urls import path
from . import views

app_name = 'interface'

urlpatterns = [
    path('',                        views.index,           name='index'),
    path('resultats/',              views.resultats,       name='resultats'),
    path('scenarios/',              views.scenarios,       name='scenarios'),
    path('scenarios/lancer/<int:numero>/', views.lancer_scenario, name='lancer_scenario'),
    path('historique/',             views.historique,      name='historique'),
    path('comparaison/',            views.comparaison,     name='comparaison'),
]
