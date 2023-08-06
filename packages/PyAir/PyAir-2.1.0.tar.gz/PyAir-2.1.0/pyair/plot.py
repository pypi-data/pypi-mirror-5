#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
**Plotting

Tracage de diagrammes de vents et utilitaires d'ajustement de diagrammes

Exemple d'utilisation:

vv = numpy.arange(start=1, end=6, step=0.1)
dv = numpy.arange(start=0, end=360, step=5)
vents(vv, dv, speed_classes=[1,2,3,4,5])
"""

RC = {
    "lines.linewidth": 2.0,
    "examples.download": True,
    "axes.edgecolor": "#bcbcbc",
    "patch.linewidth": 0.5,
    "legend.fancybox": True,
    "legend.fontsize": 8,
    "axes.color_cycle": [
        "#348ABD",
        "#A60628",
        "#7A68A6",
        "#467821",
        "#CF4457",
        "#188487",
        "#E24A33"
    ],
    "axes.facecolor": "#eeeeee",
    "axes.labelsize": "large",
    "axes.grid": True,
    "patch.edgecolor": "#eeeeee",
    "axes.titlesize": "x-large",
    "svg.embed_char_paths": "path",
    "examples.directory": ""
}

import matplotlib
matplotlib.rcParams.update(RC)

import matplotlib.pyplot as plt
import scipy as sc
import numpy as np
from pylab import DateFormatter
from windrose.windrose import WindroseAxes

import date
import stats
import utils

UNITES = {
    'micro' : r'$\rm{\mu g/m^3}$',
    'microg/m3' : r'$\rm{\mu g/m^3}$',
    'milli' : r'$\rm{mg/m^3}$',
    'deg' : r'$\rm{degr\acute{e}}$',
}


#Paramétres par défaut
FIGSIZE = {'1c' : (3.854, 3.154), #1colonne, 1ligne
'2c' : (7.20, 3.154), #2colonnes, 1ligne
'2c_vert' : (3.854, 6.308), #1colonne, 2lignes
'3c' : (7.20, 6.308), #2colonnes, 2lignes
'defaut': plt.rcParams['figure.figsize'],
'A4_portrait': (8.267, 11.693),
'A4_landscape': (11.693, 8.267),
}


def new_wraxe():
    """Génère une nouvelle figure (matplotlib) contenant un graphique (axes)
    adapté pour tracer une rose des vents

    Retourne:
    une instance de WindroseAxes

    """

    fig = plt.figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='w')
    rect = [0.1, 0.1, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    return ax


def _new_default_axe(size):
    """Retournes une nouvelle figure suivant la taille demandée
    size: taille de la figure telle que définie par FIGSIZE (str)
    ou en passant directement une liste de valeur(largeur, hauteur)
    """
    if type(size)==str:
        size = FIGSIZE[size]
    fig = plt.figure(num = None, figsize=size, facecolor='w',
                   edgecolor='w')
    axe = fig.add_axes([0.15, 0.15, 0.75, 0.75])
    return axe


def _new_time_axe(size='defaut'):
    """Retournes une nouvelle figure suivant le type demandé
    size: taille de la figure telle que définie par FIGSIZE (str)
    ou en passant directement une liste de valeur(largeur, hauteur)
    """
    if type(size)==str:
        size = FIGSIZE[size]
    fig = tpl.tsfigure(figsize=size, facecolor='w',
                   edgecolor='w')
    axe = fig.add_tsplot(111)
    return axe


def set_valeurs(serie, axes=None, xdelta=0., ydelta=0., format_="%.1f"):
    """
    Ecrit les valeurs (y) sur le diagramme (utile pour les bargraphes)

    Paramètres:
    serie: pandas.Series de données d'entrée utilisé pour générer le diagramme
    axes: soit un matplotlib.Axes existant à utiliser, soit récupère automatiquement
    le graphique courant
    xdelta: valeur x de décalage pour le texte
    ydelta: valeur y de décalage pour le texte
    format_: chaine de formatage du texte

    Retourne:
    le graphique modifié

    """

    if axes is None:
        axes = plt.gca()

    ticks = axes.get_xticks()
    for i, (index, value) in enumerate(serie.iteritems()):
        plt.text(ticks[i], value, format_%value, ha='center', va='top',
                 color='red', weight='bold')


def _set_unit(axe, unit=''):
    """Pose l'unité sur l'axe des y

    """
    if unit in UNITES.keys():
        u = UNITES[unit]
    else:
        u = unit
#    u = unicode("%s" %u, CODING)
    axe.set_ylabel(u)
    axe.figure.canvas.draw()


def plot(y, x=None, noms=None, linestyle=None, colors=None, style='ts',
    datefmt='%d/%m/%Y', ordre=1, unit='', size='defaut', legend=False, axe=None):
    """plot(params): tracage de diagrammes pour publication.

    x: données pour les abscisses. Si x=None, alors les entrées dans y doivent
    être des timeseries (au moins y[0]) desquelles les dates serviront de
    valeurs pour x

    y: données pour les ordonnées. DOIT ETRE UNE LISTE, MEME POUR UNE SEULE
    ENTREE!

    colors:liste de couleur des courbes. Si None, une par defaut est utilisé

    noms: noms des courbes s'il y a lieu (à utiliser avec legend)

    linestyle: Liste de style de ligne, conformément à la description de
    maptlotlib.plot (continu par défaut)

    style: 'date', 'ts', 'xy'(voir fonction regression pour plus d'options)

    datefmt: format des libellés des X si style='date'. Pas utilisé si
    style = 'ts'

    unit: unité des Y (voir UNITES.keys()). Peut etre remplis (ex: unit='°C')

    size: taille de la figure (voir FIGSIZE.keys())

    legend: emplacement de la légende (voir pylab.legend). Default=False

    axe: une instance d'axes où tracer les courbes. Si None, une est créée

    """

    if axe is None:
        if style == 'ts':
            axe = _new_time_axe(size)
        else:
            axe = _new_default_axe(size)
    if not noms:
        noms = ['_nolegend_']*len(y)
    if not isinstance(noms, list):
        noms=list(noms)
    if not linestyle:
        linestyle = ['.-',]*len(y)
    noms = [unicode("%s" %nom, CODING) for nom in noms]

    #Gestion des dates avec le module timeseries.
    if x is None:
        if hasattr(y[0], 'dates'):
            x = DAtonum(y[0].dates)
        else:
            raise ValueError("x=None mais y n'est pas une liste contenant des timeseries")

    #Tracage des courbes
    for n, datas in enumerate(y):
        if colors:
            c = colors[n]
        else:
            c = COULEURS[n]
        if style == 'xy':
            axe.plot(x, datas, linestyle[n], label=noms[n], color=c, linewidth=0.5,
                     markeredgewidth=0)

        if style == 'date':
            #fmt: format des dates ('%d/%m/%Y %H:%M')
            axe.plot_date(x, datas, linestyle[n], label=noms[n], color=c,
                          markeredgewidth=0)
            axe.xaxis.set_major_formatter( DateFormatter(datefmt) )
            formatXAxis(axe)

        if style == 'ts':
            axe.tsplot(datas, linestyle[n], label=noms[n], color=c,
                       markeredgewidth=0)

    #Légende
    if legend:
        leg = plt.legend(loc=legend, numpoints=2,
                         markerscale=plt.rcParams['legend.markerscale']/plt.rcParams['lines.markersize'])
        leg.draw_frame(True)
        leg.get_frame().set_facecolor('1')

    #Unité
    _set_unit(axe, unit)

    axe.figure.canvas.draw()
    axe.figure.show()
    return axe


def regression(x, y, ordre=1):
    """
    Trace x contre y et calcul la fonction de régression d'ordre défini
    """
    try:
        xlab = x.mesure
    except:
        x = np.ma.array(x)
        xlab = "X"
    try:
        ylab = y.mesure
    except:
        y = np.ma.array(y)
        ylab = "Y"
    x, y = utils.dissolveMask(x, y)
    x = x.compressed()
    y = y.compressed()
    coefs = sc.polyfit(x, y, ordre)
    xr = np.sort(x)
    yr = sc.polyval(coefs, xr)
    ax = plot(x=x, y=[y,], linestyle='o', style='xy')
    ax.plot(xr, yr, 'k-', label='regression')
    plt.legend()
#    ax = plot(x=x, y=[yr,], linestyle='-', style='xy', noms=['regression'],
#              axe=ax, legend=True, colors=['k',])
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    print("coefficients : %s (a et b de y=ax+b si ordre=1)"%coefs)
    print("correlation  : %s (0: aucune corrélation, -1 ou 1: corrélation parfaite)"%stats.correlation(y, x))


def trace_indices(X, annees=[], axe=None, _type='3c'):
    """
    Tracage des histogrammes d'indices ATMO en accord avec la charte de Publidec
    y: tableau 2D de valeurs à tracer. Chaque ligne est un tableau de len()=3, où
    sont données les quantités d'indices (classes) tel que :
    [1 <= x < 5, 5 <= x < 7, 7 <= x < 11] ( ce que retourne scipy.stats.histogram2(x, [1,5,7,11]) )
    pour chaque année
    annees = liste de noms des années. len(annees) = y.shape[0]
    ax: axes instance sur lequel tracer
    """
    COULEURS_ATMO = ['#00ff00', #Vert foncé : C1000 M0 J100 N0
                     '#f7c901', #Jaune : C3 M20 J100 N0
                     '#ff0000', #Rouge : C0 M100 J100 N0
                     ]

    if axe is None:
        axe = _new_default_axe(_type)
        #ax = fig.add_subplot(111)

    #Tracage des courbes
    X = np.array(X)
    if len(annees) != X.shape[0]:
        raise ValueError, "le nombre d'années est le nombre de lignes dans X doivent correspondre."
    epaisseur = 0.1666 # Epaisseur des barres horizontales (=hauteur)
    steps = [0.25, 0.50, 0.75] # Positions de pose des barres (en y relatifs)
    classes = X.transpose()
    Y = np.arange(len(annees)) # Nombre d'années = nombre d'ordonnées
    patches = list()
    for i in range(0, 3):
        values = classes[i]
        y = Y+steps[i]
        col = plt.barh(y, width=values, height=epaisseur, left=0, color=COULEURS_ATMO[i], linewidth=0, align='center')
        for v in range(len(values)):
            plt.text(values[v]+5, y[v], "%i"%int(values[v]),ha='left',va='center')
        patches.append(col[0])

    # axe des ordonnées
    #plt.axvline(color='k', linewidth=BOXLINESIZE, label='_nolegend_')
    ylabelspos = np.arange(len(annees))
    # On place des labels vides aux ordonnées, puis on place du texte (solution à l'arrache :-P)
    plt.yticks(ylabelspos, ['']*len(annees), va='bottom')
    for i, t in enumerate(map(str, annees)):
        plt.text(-10, ylabelspos[i]+0.5, t, va='center', ha='right')

    # axe des abscisses
    #plt.axhline(color='k', linewidth=BOXLINESIZE, label='_nolegend_')
    locs, labels = plt.xticks(np.arange(50, 360, 50), map(str, np.arange(50, 360, 50)), rotation=45, ha='right')
    plt.xlim((0,360))

    #Légende
    leg = plt.legend(patches, (u"1 à 4", u"5 à 6", u"7 à 10"))
#    for l in leg.get_texts():
#        plt.setp(l, fontsize=LEGFONTSIZE )
    leg.draw_frame(False)

    plt.ylim((0, len(annees)+1))
    plt.draw()
    return axe


def formatXAxis(axe, rotation=30, fontsize=10, pop_last_x=True):
    """
    Formattage des axes X et Y et pose de l'unité des y
    pop_last_x=False si le dernier label des x ne doit pas etre enlevé
    """

    # axe des abscisses
    labels = axe.get_xticklabels()
    plt.setp( labels, rotation=rotation, fontsize=fontsize )

    if pop_last_x:
        textlabels = [ t.get_text() for t in labels ]
        axe.set_xticklabels(textlabels[0:-1])


def VV_histo(x, y, _type='1c', axe=None):
    """
    Trace une figure représentant l'histogramme des vitesses de vent
    """
    if axe is None:
        axe = _new_default_axe(_type)
    plt.bar(x, y, width=0.9, align='edge', facecolor="#348ABD")
    #xlabels = map(str, x)
    for i in range(len(x)):
        plt.text(x[i]+0.5, y[i], "%.1f"%y[i], ha='center', va='bottom',
                color='red', weight='bold', fontsize=10)
    plt.xlim(x[0], x[-1]+1)
    #_set_unit(plt.gca(), unit='%')
    axe.set_ylabel('%')
    axe.set_xlabel('m/s')
    return axe


def DV_histo(y, _type='2c', axe=None):
    """
    Trace une figure représentant l'histogramme des directions de vent
    """
    if axe is None:
        axe = _new_default_axe(_type)
    xlabels = ('N','','N-E','','E','','S-E','','S','','S-O','','O','','N-O','')
    xticks = range(1, 17)
    plt.bar(xticks, y, align='center', facecolor="#348ABD")
    plt.gca().set_xticks(xticks)
    plt.gca().set_xticklabels(xlabels)
    for i in range(len(xticks)):
        plt.text(xticks[i], y[i], "%.1f"%y[i], ha='center', va='bottom',
                color='red', weight='bold',fontsize=10)
    #_set_unit(plt.gca(), unit='%')
    axe.set_ylabel('%')
    axe.set_xlabel('directions')
    return axe


def vents(vv, dv, speed_classes=[0,1,2,3,4,5], histo=True, savein=None,
          suffix='', format='jpg', **kwargs):
    """Trace les graphiques suivants (16 secteurs fixés):
        - rose des vents
        - histogramme des vitesses de vent
        - histogramme des directions de vent

    Paramètres:
    vv: vitesses de vent
    dv: directions du vent
    speed_classes: classes de vent
    histo: si oui ou non il faut tracer les histogrammes de direction et vitesse
    savein: 'repertoire' oé enregistrer les graphiques
    suffix: suffixe à ajouter au nom du fichier image sauvegardé
    format: format du fichier image é sauvegarder. Si aucun, 'jpg' est choisi.
    """
    axes_list = list()

    if not format:
        format = 'jpg'
    if suffix:
        suffix = '_%s' %suffix
    else:
        suffix = ''

    vv = vv.astype(float)
    dv = dv.astype(float)
    vv, dv = utils.dissolveMask(vv,dv)
    vv = vv.dropna()
    dv = dv.dropna()
    # Rose des vents
    try:
        ax = new_wraxe()
#        w_c, s_c, freq = ax.bar(dv, vv, bins=speed_classes, nsector=16, normed=True)
        ax.bar(dir=dv, var=vv, bins=speed_classes, opening=0.8, normed=True, **kwargs)
        ax.legend()
        plt.draw()
        freq = ax._info['table']
        if savein:
            plt.savefig("%s/RDV%s.%s" %(savein, suffix, format))
        axes_list.append(ax)
    except Exception, error:
            print error

    if histo:
        # Histograme des vitesses
        try:
            vv_ax = VV_histo(speed_classes, freq.sum(axis=1), axe=None)
            if savein:
                plt.savefig("%s/VV_histo%s.%s" %(savein, suffix, format))
            axes_list.append(vv_ax)
        except Exception, error:
                print error

        # Histograme des directions
        try:
            dv_ax = DV_histo(freq.sum(axis=0), axe=None)
            if savein:
                plt.savefig("%s/DV_histo%s.%s" %(savein, suffix, format))
            axes_list.append(dv_ax)
        except Exception, error:
                print error

    return axes_list


def ventsMF(vv, dv, speed_classes=[1,2,3,4,5,6], lim=1, histo=True,
            savein=None, suffix=None, format=None):
    """histo VV & DV + rose des vents sur base de données Météo-France, i.e.
    annulation des DV=0 (et VV réciproques) + hors vents calmes

    Paramètres:
    vv & dv: (pandas.Series) Vitesse et Direction de vent
    speed_classes : (int|float list) nombres de classes de vents à calculer
    histo: si oui ou non il faut tracer les histogrammes de direction et vitesse
    lim : (int|float) limite vent calme, normallement 1 m/s
    savein: (str) Répertoire où enregistrer les diagrammes. None = pas d'enregistrement
    suffix: (str) Suffix à rajouter aux noms des diagrammes à enregistrer
    format: (str) Format des fichiers à enregistrer (PNG, JPEG, ...)

    Retourne:
    Des statistiques sur les données, et affiche les diagrammes

    """

    dv = dv.astype(float)
    #Suppression des directions nulles
    dv = dv.mask(dv==0.)
    #nombre de directions nulles
    dvnul = dv.size - dv.count()

    vv = vv.astype(float)
    #Suppression des vitesses de vent inférieures à la limite de vent calme
    vv = vv.mask(vv<lim)
    #nombre de vitesses de vents inférieures à la limite de vent calme
    vvnul = vv.size - vv.count()
    #Suppression des vitesses de vent où les directions sont nulles
    vv = vv.mask(dv.isnull())

    print("%s directions nulles sur %s (%.1f %%)" % (dvnul, dv.size, float(dvnul)*100/dv.size))
    print("%s occurences de vents calmes sur %s (%.1f %%)" % (vvnul, vv.size, float(vvnul)*100./vv.size))
    vents(vv, dv, speed_classes, histo, savein, suffix, format)


def polim(axe, polluant='O3'):
    """
    Raccourcis pour tracer les lignes horizontales décrivant les seuils
    réglementaires pour les polluants
    """
    seuils = {'O3' : (150, 180, 240),
              'NO2': (135, 200, 400),
              'SO2': (200, 300, 500)}
    labs = ['MVR', 'IR', 'A']
    if polluant not in seuils.keys():
        return axe
    colors = ('green', 'orange', 'red')
    xlim = axe.get_xlim()
    for i in range( len(seuils[polluant]) ):
        seuil = seuils[polluant][i]
        color = colors[i]
        x0 = xlim[0]
        x1 = xlim[1]
        axe.hlines(seuil, x0, x1, color, label='_nolegend_')
    for i in range( len(seuils[polluant]) ): #Deuxième passe pour inscrire les
        #valeurs, sinon le texte de la première ligne est décalée (bug MPL??)
        seuil = seuils[polluant][i]
        color = colors[i]
        x0 = xlim[0]
        x1 = xlim[1]
        t = "%s (%s)"%(labs[i], seuil)
        plt.text(x0, seuil, t, color=color, ha='left', va='bottom', weight='bold')
    plt.ylim(0, seuils[polluant][-1]+100)
    plt.draw()
    return axe


def plot3D(fname, ex = 1):
    """
    Affiche rapidement un champ 3D dans les valeurs sont stockés dans un fichier
    CSV de format ID,X,Y,Z
    fname : nom du fichier CSV contenant les données
    ex : exagération à appliquer sur Z (Z = Z*ex)
    Requiert le module mayavi, et si lancé dans ipython, utiliser le switch -wthread
    """
    try:
        from enthought.mayavi import mlab
    except ImportError:
        print("Erreur d'import. Installez le module enthought.mayavi")
    id,x,y,z = np.loadtxt('limoges.csv', delimiter=',', skiprows=1, unpack=True)
    z = z * ex
    mlab.figure(1, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))
    pts = mlab.points3d(x, y, z, z, scale_mode='none', scale_factor=0.2)
    mlab.show()
    mesh = mlab.pipeline.delaunay2d(pts)
    surf = mlab.pipeline.surface(mesh)

