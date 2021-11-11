# -*- coding: utf-8 -*-
import pywikibot, time, datetime
def blanchirDiscussion(ref, id):
  article=getArticle(ref)
  texte_blanchi = "{{subst:Blanchiment LANN | article = [[:%s]] | oldid = %s }}" % (article.title(), id)
  comm_blanchiment = "[[Utilisateur:NaggoBot/Blanchiment#Blanchiment_LANN|Blanchiment de courtoisie par bot]]"
  try:
    ref.put(texte_blanchi, comm_blanchiment)
  except Exception as e:
    print(e.message, e.args)
# Ajouter un bandeau d'instructions
def ajouterInstructions(ref):
  texte=ref.get()
  if not "Instructions LANN" in texte:
    try:
      ref.put("{{Instructions LANN}}\n" + texte, "BOT : ajout instructions LANN")
    except Exception as e:
      print(e.message, e.args)
# Article en fonction de la page de discussion de neutralité
def getArticle(ref):
  article=ref.toggleTalkPage()
  article=pywikibot.Page(site,article.title().replace("/Neutralité",""))
  return article
# Si l'article est dans la catégorie "soupçonné de partialité" (ajoutée par bandeau)
# ==> on ne traite pas, la controverse n'est pas terminée.
def toujoursEnCours(ref):
  article=getArticle(ref)
  if not article.exists():
    print("article inexistant : %s" % article.title())
    return False
  enCours=False
  for cat in article.categories():
    if "Article soupçonné de partialité" in cat.title() or "Désaccord de neutralité" in cat.title():
      print("Controverse non terminée : " + article.title())
      enCours=True
      continue
  return enCours
# SI le délai depuis la dernière modif > 21 jours
def delaiAtteint(date_edit): 
  datepage = date_edit+datetime.timedelta(seconds=21*3600*24)
  if datepage < datetime.datetime.now():
    return True
  else:
    return False

site = pywikibot.Site('fr')
# Phase 1 : pages de discussion sans le modèle Instructions LANN
# (elles devraient l'avoir : on le rajoute au besoin)

for neu in site.search(namespaces=1, searchstring='''insource: -Instructions_LANN intitle:/Neutralité'''):
  titre= neu.title()
  if titre.endswith('/Neutralité'):
    print("pris en compte : " + titre)
  else:
    print("non pris en compte : " + titre)
    continue
  if toujoursEnCours(neu):
    print("controverse en cours : " + titre)
    ajouterInstructions(neu)
    continue
  else:
    print("pas en cours : " + titre)
  lastrev = next(neu.revisions(reverse=False, total=1))
  date_edit = lastrev['timestamp']
  id = lastrev['revid']
  if delaiAtteint(date_edit):
    print("delai atteint", date_edit)
    blanchirDiscussion(neu, id)
  else:
    print("delai pas atteint", date_edit)
    ajouterInstructions(neu)

# Phase 2 : pages de discussion intégrant le modèle Instructions LANN
article='Modèle:Instructions LANN'
page=pywikibot.Page(site,article)
# on recherche toutes les pages qui incluent le modèle dans l'espace Discussion:
for ref in page.getReferences(namespaces=1, only_template_inclusion=True):
  if ref.isRedirectPage():
    continue
  titre=ref.title()

  lastrev = next(ref.revisions(reverse=False, total=1))
  user = lastrev['user']
  comm = lastrev['comment']
  date_edit = lastrev['timestamp']
  id = lastrev['revid']

  # on ne va pas plus loin si le dernier edit est un blanchissement de courtoisie
  if user == "NaggoBot" and "Blanchiment de courtoisie" in comm:
    print("déjà blanchi par le bot : %s" % titre)
    continue
  # ni si le délai n'est pas atteint
  if not delaiAtteint(date_edit):
    print("délai non atteint : %s" % titre)
    continue
  # ni si l'article est toujours dans la catégorie "non neutre"
  if toujoursEnCours(ref):
    continue
  # déjà archivé et pas rouvert : on passe
  # le 450 est une estimation, la taille dépend du nom de l'article
  texte=ref.get()
  if len(texte)<450 and "Archive LANN" in texte:
    continue
  else:
    blanchirDiscussion(ref, id)
