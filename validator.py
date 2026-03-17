# =============================================================
#  validator.py — Couche validation
#
#  Vérifie que les données saisies par l'utilisateur sont
#  correctes avant de lancer l'optimisation.
#  Toutes les vérifications sont dans une seule fonction.
# =============================================================


def valider_donnees(demandes, capacites, couts, regions, centres):
    """
    Vérifie la cohérence des données du problème.

    Retourne un tuple (est_valide, liste_erreurs) :
      - est_valide    : True si tout est OK, False sinon
      - liste_erreurs : liste de messages d'erreur (vide si OK)
    """
    erreurs = []

    # ── 1. Vérifier que les demandes sont strictement positives ──
    for r in regions:
        valeur = demandes.get(r, 0)
        if valeur is None or valeur <= 0:
            erreurs.append(f"La demande de la région {r} doit être > 0 (valeur : {valeur}).")

    # ── 2. Vérifier que les capacités sont strictement positives ──
    for c in centres:
        valeur = capacites.get(c, 0)
        if valeur is None or valeur <= 0:
            erreurs.append(f"La capacité du centre {c} doit être > 0 (valeur : {valeur}).")

    # ── 3. Vérifier que tous les coûts sont positifs ──────────────
    for c in centres:
        for r in regions:
            valeur = couts.get(c, {}).get(r, 0)
            if valeur is None or valeur < 0:
                erreurs.append(f"Le coût {c}→{r} doit être ≥ 0 (valeur : {valeur}).")

    # ── 4. Vérifier que la capacité totale couvre la demande totale ──
    # Si ce n'est pas le cas, le problème est mathématiquement infaisable.
    if not erreurs:  # inutile de vérifier si on a déjà des erreurs de valeur
        demande_totale  = sum(demandes.get(r, 0) for r in regions)
        capacite_totale = sum(capacites.get(c, 0) for c in centres)
        if capacite_totale < demande_totale:
            erreurs.append(
                f"La capacité totale des centres ({capacite_totale} requêtes) est "
                f"inférieure à la demande totale ({demande_totale} requêtes). "
                f"Il manque {demande_totale - capacite_totale} places."
            )

    est_valide = len(erreurs) == 0
    return est_valide, erreurs
