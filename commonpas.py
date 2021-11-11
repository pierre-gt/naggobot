# -*- coding: utf-8 -*-
import datetime

def decoupedate(l):
    tdatepas=l.split('|')
    jour=tdatepas[1].strip().replace("er","")
    if len(jour)==1:
        jour="0"+jour
    mois="00"
    smois=tdatepas[2]
    if smois=="janvier":
        mois="01"
    if smois=="février":
        mois="02"
    if smois=="mars":
        mois="03"
    if smois=="avril":
        mois="04"
    if smois=="mai":
        mois="05"
    if smois=="juin":
        mois="06"
    if smois=="juillet":
        mois="07"
    if smois=="août":
        mois="08"
    if smois=="septembre":
        mois="09"
    if smois=="octobre":
        mois="10"
    if smois=="novembre":
        mois="11"
    if smois=="décembre":
        mois="12"
    annee=tdatepas[3].split("}")[0]
    return annee,mois,jour
def datedujour():
    nom_mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    dt=datetime.datetime.now()
    return "%d %s %d" % (dt.day , nom_mois[dt.month -1].lower(), dt.year)
