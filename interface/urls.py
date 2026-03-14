from django.urls import path
from . import views

app_name = 'interface'

urlpatterns = [
    path('', views.index, name='index'),
    path('resultats/', views.resultats, name='resultats'),
    path('scenarios/', views.scenarios, name='scenarios'),
    path('historique/', views.historique, name='historique'),
]