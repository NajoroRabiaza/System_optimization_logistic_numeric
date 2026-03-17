# Logistics Optimizer

Projet d'examen — L2 Informatique  
Optimisation d'un système logistique numérique avec Django.

## Installation

```bash
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Ouvrir : http://127.0.0.1:8000

---

## Architecture des modules d'optimisation

```
projet/
├── data.py          # Couche données — demandes, capacités, coûts initiaux
├── model.py         # Couche modélisation — matrices LP (A_ub, A_eq, c, bornes)
├── validator.py     # Couche validation — vérification des saisies utilisateur
├── optimizer.py     # Couche optimisation — scipy.optimize.linprog (HiGHS)
├── interface/
│   ├── views.py     # Couche IHM — vues Django câblées au vrai solveur
│   ├── urls.py      # Routes (+ lancer_scenario/<int:numero>/)
│   ├── forms.py     # Formulaire de saisie
│   └── templatetags/
│       └── dict_extras.py  # Filtre {{ dict|get_item:'cle' }}
└── visualization/
    └── charts.py    # Couche visualisation — graphiques matplotlib
```

## Solveur utilisé

`scipy.optimize.linprog` avec la méthode **HiGHS** (simplex révisé + point intérieur).
Justification : scipy est disponible sans installation supplémentaire, et HiGHS est
le solveur LP libre le plus performant actuellement.

## Résultats — Situation initiale

| Scénario              | Statut    | Coût total |
|-----------------------|-----------|------------|
| Situation initiale    | Optimal   | 17 900     |
| Scénario 2 (C2 -25%) | Optimal   | 18 200     |
| Scénario 3 (C3 +30%) | Optimal   | 19 130     |
| Scénario 5 (C3≠R4)   | Optimal   | 17 900     |
| Scénario 1 (+20%)     | Infaisable| —          |
| Scénario 4 (C2 off)   | Infaisable| —          |
