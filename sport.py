# -*- coding: utf-8 -*-
import pywikibot
import datetime
import time
is_dst = time.daylight and time.localtime().tm_isdst > 0
#utc_offset = - (time.altzone if is_dst else time.timezone)
# pour simplfier on admettra que le bot reste sur UTC en permanence
utc_offset = 7200
from pywikibot import date
delai=7
limit_commentaire=6
site = pywikibot.Site('fr')
commentaire='''Sport : suivi des articles récents'''
cible='Projet:Sport/Articles récents'
pagecible=pywikibot.Page(site,cible)
listes=[]
for article in pagecible.linkedPages():
    listes.append(article.title())
categpalette=pywikibot.Page(site,"Catégorie:Modèle lien vers portail sport")
portaux=[]
for p in site.categorymembers(categpalette):
    for l in p.linkedPages():
        if l.title().startswith("Portail:"):
            portaux.append(l.title())
articles={}
deb=datetime.datetime.now()-datetime.timedelta(days=delai)
debut=datetime.datetime(deb.year, deb.month, deb.day)
categ=pywikibot.Page(site,"Catégorie:Portail:Sport/Articles liés")
cpt=0
debut_utc=debut-datetime.timedelta(seconds=utc_offset)
for page in site.categorymembers(categ, sortby="timestamp", starttime=debut_utc.isoformat()):
    firstrev= next(page.revisions(reverse=True, total=1))
    daterev=firstrev['timestamp']
    datepage=daterev+datetime.timedelta(seconds=utc_offset)
    if datepage<debut:
        continue
    dateJMA="%4d-%02d-%02d" % (datepage.year, datepage.month, datepage.day)
    for r in page.linkedPages():
        if r.isRedirectPage():
            r=r.getRedirectTarget()
        if r.title() in portaux:
            if dateJMA in articles:
                if r.title() in articles[dateJMA]:
                    if not page.title() in articles[dateJMA][r.title()]:
                        articles[dateJMA][r.title()].append(page.title())
                else:
                    articles[dateJMA][r.title()]=[page.title()]
            else: 
                articles[dateJMA]={r.title():[page.title()]}
    if page.title() not in listes and cpt < limit_commentaire:
        commentaire+=" + [[%s]]" % page.title()
        cpt+=1
        if cpt == limit_commentaire:
            commentaire+=" et al."
texte="__NOTOC__\n"
sous_portails={"Tennis":'Portail:Tennis/Articles récents',
		"Baseball":"Utilisateur:NaggoBot/TestBaseball",
		"Basket-ball":"Projet:Basket-ball/Articles récents",
		"Football américain":"Projet:Football américain/Articles récents",
		"Athlétisme":"Projet:Athlétisme/Tableau suivi/Articles récents"}
texte_sousportail={}
cible_sousportail={}
pagecible_sousportail={}

for sousportail,cible in sous_portails.items():
    texte_sousportail[sousportail]="__NOTOC__\n{{bots|deny=HAL}}\n"
    cible_sousportail[sousportail]=cible
    pagecible_sousportail[sousportail]=pywikibot.Page(site,cible_sousportail[sousportail])

for k in sorted(articles, reverse=True):
    texte+= "== %d %s ==\n" % (int(k.split("-")[2]), date.formats['MonthName']['fr'](int(k.split("-")[1])))
    for i in sorted(articles[k]):
        texte+= "* '''%s''' : "% str(i).split(':')[1]
        for j in sorted(articles[k][i]):
            texte+= " [[%s]] ;" % j
        for sousportail, cible in sous_portails.items():
            if str(i).split(':')[1] == sousportail:
                texte_sousportail[sousportail]+= "* %d %s :" % (int(k.split("-")[2]), date.formats['MonthName']['fr'](int(k.split("-")[1])))
                for j in sorted(articles[k][i]):
                    texte_sousportail[sousportail]+= " [[%s]] ;" % j
                texte_sousportail[sousportail]+= "\n"
        texte+="\n"
texte+="----\n*'''Les précédents articles sont placés dans la page''' '''[[Projet:Sport/Archives|archives]].'''"
pagecible.put(texte, commentaire)
for sousportail, cible in sous_portails.items():
    pagecible_sousportail[sousportail].put(texte_sousportail[sousportail], "Bot : Articles récents du portail %s" % sousportail.lower())
