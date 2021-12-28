# -*- coding: utf-8 -*-
import pywikibot
import sys
from commonpas import decoupedate, datedujour
import datetime

def danieldize(n):
    if n==1:
        return "un"
    if n==2:
        return "deux"
    if n==3:
        return "trois"
    if n==4:
        return "quatre"
    if n==5:
        return "cinq"
    if n==6:
        return "six"
    if n==7:
        return "sept"
    if n==8:
        return "huit"
    if n==9:
        return "neuf"
    if n==10:
        return "dix"
    if n==11:
        return "onze"
    if n==12:
        return "douze"
    if n==13:
        return "treize"
    if n==14:
        return "quatorze"
    if n==15:
        return "quinze"
    if n==16:
        return "seize"
    return str(n)

nomDePage="Wikipédia:Pages à supprimer"
limite_avis_pour_bistro=2
limite_jours_pour_bistro=5
nb_liste_bistro=0
nb_limite_bistro=30
site = pywikibot.Site('fr')
page = pywikibot.Page(site, nomDePage)
text = page.get().encode('utf-8')
lines=text.decode().split("\n")
traitee=False
datepas="Date non renseignée"
textenaggo=""
troisoumoins=""
deuxoumoins=""
deuxoumoins5j=""
tableau=""" {| class="wikitable alternance centre sortable"
 |+ Pages à supprimer
 |----
 ! !! scope="col" | Date !! scope="col" | Conserver !! scope="col" | Supprimer !! scope="col" | Fusionner !! scope="col" | Total des avis"""

nomDePage="Wikipédia:Pages à supprimer"
limite_avis_pour_bistro=2
limite_jours_pour_bistro=5
nb_liste_bistro=0
nb_limite_bistro=30
site = pywikibot.Site('fr')
page = pywikibot.Page(site, nomDePage)
text = page.get().encode('utf-8')
lines=text.decode().split("\n")
traitee=False
datepas="Date non renseignée"
textenaggo=""
troisoumoins=""
deuxoumoins=""
deuxoumoins5j=""
tableau=""" {| class="wikitable alternance centre sortable"
 |+ Pages à supprimer
 |----
 ! !! scope="col" | Date !! scope="col" | Conserver !! scope="col" | Supprimer !! scope="col" | Fusionner !! scope="col" | Total des avis"""
for line in lines:
    if "/début" in line:
        traitee=True
    if "/fin" in line:
        traitee=False
    if line.startswith("=="):
        print(line)
        datepas=line.split("==")[1]
        textenaggo+=line+"\n"
    if "{{En-tête section" in line:
        annee,mois,jour=decoupedate(line)
        print(annee,mois,jour)
        dt=datetime.datetime(int(annee),int(mois),int(jour))


    if "{{L|" in line and not traitee:
        print(line)
        lien=line.split('|')[1].split('}')[0]
        if ':::' not in lien:
            print("lien : " + lien)
            try:
                pddi=pywikibot.Page(site,lien)
            except:
                print("?")
                continue
            if pddi.isRedirectPage():
                print("WARNING : redir")
                nompdd=pddi.getRedirectTarget().toggleTalkPage().title()+"/Suppression"
            else:
                nompdd=pddi.toggleTalkPage().title()+"/Suppression"
            print("nompdd : " + nompdd)
            textenaggo+=line+"\n"
            try:
                pdd=pywikibot.Page(site,nompdd)
                if pdd.isRedirectPage():
                    tpdd=pdd.getRedirectTarget().get()
                else:
                    tpdd=pdd.get()
            except Exception:
                print("impossible de traiter " + lien)
                try:
                    nompdd="Discussion " + lien[0].lower()+lien[1:].split(":")[0]+":"+":".join(lien.split(":")[1:])+"/Suppression"
                    print("essai avec " + nompdd)
                    pdd=pywikibot.Page(site,nompdd)
                    if pdd.isRedirectPage():
                        tpdd=pdd.getRedirectTarget().get()
                    else:
                        tpdd=pdd.get()
                except Exception as e:
                    print("bon bah tant pis", e)
                    textenaggo+="erreur de traitement, bot en cours de mise au point"+"\n"
                    continue
            linespdd=tpdd.split("\n")
            vote=None
            cptvote=0
            totalavis=0
            conserver=0
            supprimer=0
            fusionner=0
            nondec=0
            sectionavis=0
            votespage=""
            for linepdd in linespdd:
                if "{{Article cons" in linepdd:
                    if sectionavis==0:
                        line+=" *** article déjà conservé ***"
                        textenaggo+=" *** article déjà conservé ***"
                        print("article cons.")
                if "{{Article sup" in linepdd:
                    if sectionavis==0:
                        print("article supp.")
                        line+=" *** article déjà supprimé ***"
                        textenaggo+=" *** article déjà supprimé ***"
                if "=== Avis ===" in linepdd:
                    if sectionavis==1:
                        break
                    sectionavis=1
                if "==Ancienne discussion" in linepdd:
                    break
                if "= Ancienne discussion" in linepdd:
                    break
                if linepdd.startswith("===="):
                    if not vote is None and cptvote > 0:
                        print(vote + ":" + str(cptvote), end=' ')
                        textenaggo+= vote + " : " + str(cptvote) + " "
                        votespage+= vote + " : " + str(cptvote) + " "
                        totalavis+=cptvote
                        if "Suppr" in vote:
                            supprimer+=cptvote
                        if "Conserv" in vote:
                            conserver+=cptvote
                        if "fusionn" in vote.lower():
                            fusionner+=cptvote
                        if "avis non d" in vote.lower():
                            nondec+=cptvote
                        cptvote=0
                    vote=linepdd.split("====")[1].strip()
                if not vote is None and linepdd.startswith("#") and linepdd.strip() != '#' and not linepdd.startswith("#:") and not linepdd.startswith("##") and not linepdd.startswith("#*"):
                    cptvote=cptvote+1
            if not vote is None and cptvote > 0:
                print(vote + ":" + str(cptvote))
                textenaggo+= vote + " : " + str(cptvote) + "\n"
                votespage+= vote + " : " + str(cptvote) + " "
                totalavis+=cptvote
                if "Suppr" in vote:
                    supprimer+=cptvote
                if "Conserv" in vote:
                    conserver+=cptvote
                if "fusionn" in vote.lower():
                    fusionner+=cptvote
                if "avis non d" in vote.lower():
                    nondec+=cptvote

            else:
                print()
                if totalavis == 0:
                    textenaggo+= "Aucun avis"
                    votespage= "Aucun avis"
                textenaggo+= "\n"

            if totalavis <=3:
                troisoumoins+=line + " (" + datepas.strip() + ")\n" + votespage + "\n"
            if conserver+supprimer <= 2:
                deuxoumoins+=line + " (" + datepas.strip() + ")\n" + votespage + "\n"
            if totalavis-nondec <= limite_avis_pour_bistro:
                nb_liste_bistro+=1
                if nb_liste_bistro <= nb_limite_bistro and (datetime.datetime.now()-dt).days >=limite_jours_pour_bistro:
                    deuxoumoins5j+=line + " (%d avis depuis le %s)\n" % ( totalavis-nondec, datepas.strip() ) 
                    print(deuxoumoins5j)
                if nb_liste_bistro == nb_limite_bistro + 1:
                    deuxoumoins5j+= "\n<br/> Liste tronquée à %d éléments.\n" % ( nb_limite_bistro ) 
            tableau+="""\n|----
 ! scope="row" | %s
 | %s || %d || %d || %d ||%d""" % (line.lstrip(" *").split("}}")[0]+"}}" + line.split("}}")[1][:50], datepas.strip(), conserver, supprimer, fusionner, totalavis)
tableau+="\n|}"
textenaggo+="\n==Trois avis ou moins==\n"+troisoumoins
textenaggo+="\n==Tableau==\n"+tableau

#print textenaggo
pagesuivipas="Utilisateur:NaggoBot/SuiviPAS"
if len(sys.argv)>=2 and sys.argv[1]=="bistro":
    pagesuivipas="Wikipédia:Le Bistro/"+datedujour()
    pageNaggo = pywikibot.Page(site, pagesuivipas)
    textenaggo=pageNaggo.get().replace("=== Anniversaires ===","\n=== Pages proposées à la suppression depuis au moins %s jours avec %s avis ou moins ===\n{{Boîte déroulante début|titre=Liste des pages proposées à la suppression avec peu d'avis}}\n" % (danieldize(limite_jours_pour_bistro), danieldize(limite_avis_pour_bistro))+deuxoumoins5j + "\n[[Utilisateur:NaggoBot/SuiviPAS|Suivi complet des avis sur les PAS]]\n\n{{Boîte déroulante fin}}\n=== Anniversaires ===")
    #textenaggo+="\n[[Utilisateur:NaggoBot/SuiviPAS|Suivi complet des avis sur les PAS]]\n"
    print(textenaggo)
    pageNaggo.put(textenaggo, "Suivi des PAS avec peu d'avis")
    sys.exit(0)
if len(sys.argv)>=2 and sys.argv[1]=="test":
    pagesuivipas="Utilisateur:NaggoBot/SuiviPASTEST"
    textenaggo+="\n==Deux avis (cons+sup) ou moins==\n"+deuxoumoins
    textenaggo+="\n== Pages proposées à la suppression depuis au moins %s jours avec %s avis ou moins ==\n{{Boîte déroulante début|titre=Liste des pages proposées à la suppression avec peu d'avis}}\n" % (danieldize(limite_jours_pour_bistro), danieldize(limite_avis_pour_bistro))+deuxoumoins5j + "\n{{Boîte déroulante fin}}"
pageNaggo = pywikibot.Page(site, pagesuivipas)
pageNaggo.put(textenaggo, "Suivi des PAS")

pagesuivitableau="Utilisateur:NaggoBot/SuiviPASTableau"
pageTableau = pywikibot.Page(site, pagesuivitableau)
pageTableau.put(tableau, "Tableau de suivi des PAS")
