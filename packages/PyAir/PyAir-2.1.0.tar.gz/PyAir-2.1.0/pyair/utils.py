#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
**Various functions

"""

import copy
import pandas as pd


def pivotCSV(fin, fout, nb_ref=1, sep=","):
    """Renvoie une table de pivot où les valeurs stockées en colonnes dans un
    fichier CSV seront retournées en ligne.
    Prérequis :
        - la première ligne contient les en-têtes de colonne
        - les nb_ref premières colonnes contiennent une référence d'enregistrement

    Exemple :
        en entrée :
            Source_name,CO,NO2,NOX
            ROUTE_1,0.0020091357,0.0003510306,0.0012975298
        retournera en sortie :
            ROUTE_1,CO,0.0020091357
            ROUTE_1,NO2,0.0003510306
            ROUTE_1,NOX,0.0012975298

    Paramètres:
        fin : nom du fichier d'entrée où sont stockées les données
        fout: nom du fichier où enregistrer le résultat
        nb_ref: nombre de colonne à utiliser comme référence (par défaut 1)
        sep : séparateur de colonne

    """

    f = open(fin, "rb")
    lines = f.readlines()
    f.close()
    head = lines[0]
    head = head.strip().split(sep)
    head = head[nb_ref:]

    f = open(fout, "wb")

    for line in lines[1:]:
        vals = line.strip().split(sep)
        refs = vals[0:nb_ref]
        datas = vals[nb_ref:]
        for i, v in enumerate(datas):
            l = copy.deepcopy(refs)
            l.append(head[i])
            l.append(v)
            f.write("%s\n" %sep.join(l))
    f.close()


def dissolveMask(a, b):
    """Dissout les masques des 2 series de données passées en paramètres.

    Paramètres:
    a & b: (pandas.Series)

    Retourne:
    a et b modifiés tel que toute valeur nulle (nan) dans la série a soit aussi
    mise à nulle (nan) dans la série b, et inversement
    """
    mask = a.isnull() | b.isnull()
    a = a.mask(mask)
    b = b.mask(mask)
    return a, b


def df_from_MF(fname, sep=';', decimal=',', date_format='%Y%m%d%H'):
    """Créait un DataFrame temporel depuis un fichier CSV Météo-France

    Paramètres:
    fname: nom du fichier CSV Météo-France à lire
    sep: Séparateur de colonne
    decimal: Séparateur décimal
    date_format: Descripteur de format de la colonne date

    Retourne:
    Un DataFrame temporel
    """

    df = pd.read_csv('meteo.csv', sep=sep, decimal=decimal, parse_dates=['DATE'],
                     date_parser=lambda x: pd.to_datetime(x, format=date_format)
                     )
    df = df.set_index('DATE')
    return df