# -*- coding: utf-8 -*-
import pywikibot, time, datetime
site = pywikibot.Site('fr')
# on recherche toutes les pages qui comment par Wikipédia:Appel à commentaires/Utilisateur ou Article
# dans l'espace Wikipédia: uniquement
for commentaire in ['Utilisateur','Article']:
  for ref in site.allpages(prefix="Appel à commentaires/%s/" % commentaire, namespace=4):
    if ref.isRedirectPage():
      continue
    titre=ref.title()
    texte=ref.get()
    # déjà archivé et pas rouvert : on passe

    if len(texte)<50 and "{{Blanchiment" in texte:
      continue
    else:
      lastrev = next(ref.revisions(reverse=False, total=1))
      date_edit = lastrev['timestamp']
      datepage = date_edit+datetime.timedelta(seconds=21*3600*24)
      if datepage > datetime.datetime.now():
        continue
      print(titre)
      texte_blanchi = "{{Blanchiment Appel à Commentaire}}"
      comm_blanchiment = "[[Utilisateur:NaggoBot/Blanchiment#Blanchiment_AAC|Blanchiment de courtoisie par bot]]"
      try:
        ref.put(texte_blanchi, comm_blanchiment)
      except Exception as e:
        print(e.message, e.args)
