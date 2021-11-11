# -*- coding: utf-8 -*-
import pywikibot
import datetime
import time
from pywikibot import date
utc_offset = 7200
from pywikibot import date
delai=7
site = pywikibot.Site('fr')
cible='Projet:Sport/Articles récents'
pagecible=pywikibot.Page(site,cible)
d=datetime.datetime.now()
d8=d-datetime.timedelta(days=delai+1)

minuit=datetime.datetime(d.year, d.month, d.day)-datetime.timedelta(seconds=utc_offset)
print(minuit)
site.loadrevisions(pagecible, total=5, starttime=minuit)
jourTrouve=False
textearchive=""
jour=d8.day
mois=d8.month
ciblearchive="Projet:Sport/Archives%d-trimestre%d" % (d8.year, int((d8.month-1)/3)+1)
lmois=date.formats['MonthName']['fr'](mois)
commentaire='''(Bot) Sport : archivage des articles du %d %s''' % (jour, lmois)
print(ciblearchive, commentaire)
pagearchive=pywikibot.Page(site,ciblearchive)
for rev in pagecible._revisions:
  texte=pagecible.getOldVersion(rev)
  for line in texte.split('\n'):
    if line.startswith("== %d %s ==" % (jour, lmois)):
      jourTrouve=True
    if line.startswith("----"):
      break
    if jourTrouve:
      textearchive+=line+"\n"
  if jourTrouve:
    break
if pagearchive.exists():
  textearchive=textearchive+"\n"+pagearchive.get()
pagearchive.put(textearchive, commentaire)
