import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Wedge
import numpy as np
import os

# ── Design tokens ────────────────────────────────────────
PRIMARY      = '#448A99'
PRIMARY_DARK = '#2d6875'
DARK_BAR     = '#2c3e50'
PAGE_BG      = '#FFFFFF'
GRID_COLOR   = '#e8edf2'
TICK_COLOR   = '#8b9caa'
TITLE_COLOR  = '#1A1A1A'
LEGEND_BG    = '#1e2a32'
LEGEND_FG    = '#e8f0f4'
COLOR_OK     = '#448A99'
COLOR_WARN   = '#e67e22'
COLOR_DANGER = '#e74c3c'
COLOR_CAP    = '#dde8ec'
TRACK_COLOR  = '#eef2f6'


def _font_ok(name):
    return name in [f.name for f in fm.fontManager.ttflist]

FONT = 'Poppins' if _font_ok('Poppins') else 'DejaVu Sans'


def _apply_base_style(ax, fig):
    fig.patch.set_facecolor(PAGE_BG)
    ax.set_facecolor(PAGE_BG)
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.spines['bottom'].set_linewidth(1.2)
    ax.yaxis.grid(True, color=GRID_COLOR, linewidth=1, linestyle='-', zorder=0)
    ax.set_axisbelow(True)
    ax.xaxis.grid(False)
    ax.tick_params(axis='x', colors=TICK_COLOR, length=0, labelsize=9.5)
    ax.tick_params(axis='y', colors=TICK_COLOR, length=0, labelsize=9)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily(FONT)


def _title_block(ax, title, subtitle=None):
    ax.text(0, 1.14, title, transform=ax.transAxes,
            fontsize=13, fontweight='bold', color=TITLE_COLOR,
            va='top', fontfamily=FONT)
    if subtitle:
        ax.text(0, 1.06, subtitle, transform=ax.transAxes,
                fontsize=9, color=TICK_COLOR, va='top', fontfamily=FONT)


def _legend_card(ax, labels, colors, x_rel=0.66, y_rel=0.96):
    pad_x  = 0.022
    pad_y  = 0.028
    line_h = 0.075
    dot_r  = 0.020
    card_w = 0.32
    card_h = pad_y * 2 + line_h * len(labels) + 0.005

    card = FancyBboxPatch(
        (x_rel, y_rel - card_h), card_w, card_h,
        boxstyle="round,pad=0.008",
        transform=ax.transAxes,
        facecolor=LEGEND_BG, edgecolor='none',
        zorder=10, clip_on=False,
    )
    ax.add_patch(card)

    for i, (label, color) in enumerate(zip(labels, colors)):
        y_c = y_rel - pad_y - line_h * i - line_h / 2
        dot = plt.Circle(
            (x_rel + pad_x + dot_r, y_c), dot_r,
            transform=ax.transAxes, color=color,
            zorder=11, clip_on=False,
        )
        ax.add_patch(dot)
        ax.text(
            x_rel + pad_x + dot_r * 2 + 0.016, y_c,
            label,
            transform=ax.transAxes,
            color=LEGEND_FG, fontsize=8.5,
            va='center', fontfamily=FONT,
            zorder=11, clip_on=False,
        )


# ── Graphique flux ────────────────────────────────────────
def generer_graphique_flux(donnees_flux, chemin_sortie):
    regions = ['R1', 'R2', 'R3', 'R4']
    centres = ['C1', 'C2', 'C3']
    bar_colors = [PRIMARY, PRIMARY_DARK, DARK_BAR]

    valeurs = {c: [0] * len(regions) for c in centres}
    for ligne in donnees_flux:
        ri = regions.index(ligne['region'])
        valeurs[ligne['centre']][ri] = ligne['quantite']

    x     = np.arange(len(regions))
    n     = len(centres)
    grp_w = 0.62
    bar_w = grp_w / n * 0.88

    fig, ax = plt.subplots(figsize=(8, 4))
    _apply_base_style(ax, fig)

    for i, centre in enumerate(centres):
        offset = (i - (n - 1) / 2) * (grp_w / n)
        ax.bar(x + offset, valeurs[centre], bar_w,
               color=bar_colors[i], zorder=3, linewidth=0,
               # coins arrondis en haut
               capstyle='round' if hasattr(matplotlib, '__version__') else 'butt')

    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontfamily=FONT, fontsize=11, color=TICK_COLOR)
    max_val = max((max(valeurs[c]) for c in centres), default=100)
    ax.set_ylim(0, max_val * 1.32)
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True, nbins=5))

    _title_block(ax, 'Répartition des flux', 'Nombre de requêtes par région et par centre')
    _legend_card(ax, centres, bar_colors, x_rel=0.66, y_rel=0.97)

    fig.subplots_adjust(top=0.80, right=0.97, left=0.07, bottom=0.10)
    plt.savefig(chemin_sortie, dpi=120, bbox_inches='tight',
                facecolor=PAGE_BG, edgecolor='none')
    plt.close()


# ── Graphique capacités ───────────────────────────────────
def generer_graphique_capacites(donnees_utilisation, chemin_sortie):
    centres      = [l['centre']      for l in donnees_utilisation]
    charges      = [l['charge']      for l in donnees_utilisation]
    capacites    = [l['capacite']    for l in donnees_utilisation]
    pourcentages = [l['pourcentage'] for l in donnees_utilisation]

    bar_colors = []
    for pct in pourcentages:
        if pct >= 90:
            bar_colors.append(COLOR_DANGER)
        elif pct >= 70:
            bar_colors.append(COLOR_WARN)
        else:
            bar_colors.append(COLOR_OK)

    x     = np.arange(len(centres))
    bar_w = 0.45

    fig, ax = plt.subplots(figsize=(8, 4))
    _apply_base_style(ax, fig)

    ax.bar(x, capacites, bar_w + 0.18, color=COLOR_CAP, linewidth=0, zorder=2)
    ax.bar(x, charges,   bar_w,        color=bar_colors, linewidth=0, zorder=3)

    max_cap = max(capacites) if capacites else 1
    for i, (charge, pct, color) in enumerate(zip(charges, pourcentages, bar_colors)):
        ax.text(x[i], charge + max_cap * 0.025, f'{pct}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold',
                color=color, fontfamily=FONT, zorder=4)

    ax.set_xticks(x)
    ax.set_xticklabels(centres, fontfamily=FONT, fontsize=11, color=TICK_COLOR)
    ax.set_ylim(0, max(capacites) * 1.32 if capacites else 100)
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True, nbins=5))

    _title_block(ax, 'Utilisation des capacités', 'Charge actuelle vs capacité maximale par centre')
    _legend_card(ax, ['Charge actuelle', 'Capacité max'],
                 [PRIMARY, COLOR_CAP], x_rel=0.63, y_rel=0.97)

    fig.subplots_adjust(top=0.80, right=0.97, left=0.07, bottom=0.10)
    plt.savefig(chemin_sortie, dpi=120, bbox_inches='tight',
                facecolor=PAGE_BG, edgecolor='none')
    plt.close()


# ── Jauges circulaires utilisation ───────────────────────
def _draw_donut(ax, pct, label_centre, label_bas,
                color, track=TRACK_COLOR, bg=PAGE_BG):
    """
    Dessine une jauge circulaire (donut) dans un axe carré.
    - pct         : 0‑100
    - label_centre: texte affiché au centre (ex : "80%")
    - label_bas   : texte sous le cercle (ex : "C1 · 1200/1500")
    - color       : couleur de l'arc de progression
    """
    theta_start = 90                        # départ en haut
    theta_end   = 90 - 360 * (pct / 100)   # sens anti-horaire

    # Épaisseur et rayon
    r_out = 1.0
    r_in  = 0.68
    lw    = r_out - r_in

    # ── Piste de fond (cercle complet gris) ──
    track_wedge = Wedge(
        (0, 0), r_out, 0, 360,
        width=lw, facecolor=track, linewidth=0, zorder=1,
    )
    ax.add_patch(track_wedge)

    # ── Arc de progression ──
    if pct > 0:
        arc = Wedge(
            (0, 0), r_out,
            min(theta_end, theta_start),
            max(theta_end, theta_start),
            width=lw,
            facecolor=color, linewidth=0, zorder=2,
        )
        # Recalcul propre sens horaire ↓
        arc2 = Wedge(
            (0, 0), r_out,
            theta_end, theta_start,
            width=lw,
            facecolor=color, linewidth=0, zorder=2,
        )
        ax.add_patch(arc2)

    # ── Cercle intérieur blanc (trou du donut) ──
    hole = plt.Circle((0, 0), r_in - 0.02, color=bg, zorder=3)
    ax.add_patch(hole)

    # ── Pourcentage centré ──
    ax.text(0, 0.06, f'{pct}%',
            ha='center', va='center',
            fontsize=19, fontweight='bold',
            color=color, fontfamily=FONT, zorder=4)

    # ── Petite ligne de séparation ──
    ax.plot([-0.35, 0.35], [-0.12, -0.12],
            color=GRID_COLOR, linewidth=1, zorder=4)

    # ── Nom du centre ──
    parts = label_bas.split('·')
    nom   = parts[0].strip()
    detail = parts[1].strip() if len(parts) > 1 else ''

    ax.text(0, -0.26, nom,
            ha='center', va='center',
            fontsize=12, fontweight='bold',
            color=TITLE_COLOR, fontfamily=FONT, zorder=4)

    if detail:
        ax.text(0, -0.44, detail,
                ha='center', va='center',
                fontsize=8.5, color=TICK_COLOR,
                fontfamily=FONT, zorder=4)

    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.set_aspect('equal')
    ax.axis('off')


def generer_graphique_cercles(donnees_utilisation, chemin_sortie):
    """
    Génère une rangée de jauges circulaires (une par centre),
    alignées horizontalement. Sauvegarde en PNG.
    """
    n = len(donnees_utilisation)
    fig, axes = plt.subplots(1, n, figsize=(n * 2.5, 3.2))
    fig.patch.set_facecolor(PAGE_BG)

    if n == 1:
        axes = [axes]

    for ax, ligne in zip(axes, donnees_utilisation):
        pct    = ligne['pourcentage']
        centre = ligne['centre']
        charge = ligne['charge']
        cap    = ligne['capacite']

        if pct >= 90:
            color = COLOR_DANGER
        elif pct >= 70:
            color = COLOR_WARN
        else:
            color = COLOR_OK

        _draw_donut(
            ax, pct,
            label_centre=f'{pct}%',
            label_bas=f'{centre} · {charge}/{cap} requêtes',
            color=color,
        )

    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.06, wspace=0.1)
    plt.savefig(chemin_sortie, dpi=130, bbox_inches='tight',
                facecolor=PAGE_BG, edgecolor='none')
    plt.close()