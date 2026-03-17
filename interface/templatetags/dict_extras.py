# =============================================================
#  dict_extras.py — Filtres de template personnalisés
#
#  Ce fichier ajoute des filtres utiles dans les templates Django.
#  On peut les utiliser avec :  {% load dict_extras %}
# =============================================================

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Permet d'accéder à une clé de dictionnaire dans un template.
    Exemple d'usage : {{ historique|last|get_item:'numero' }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
