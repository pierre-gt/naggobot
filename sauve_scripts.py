# -*- coding: utf-8 -*-
import pywikibot
site = pywikibot.Site('fr')
f=open("liste_a_sauver","r")
line=f.readline()
while line:
  line=line.strip()
  texte='''<syntaxhighlight lang="python">\n%s\n</syntaxhighlight>''' % open(line,"r").read()
  page=pywikibot.Page(site,"Utilisateur:NaggoBot/%s" % line)
  try:
    texteCourant=page.get()
  except:
    texteCourant=""
  if texte.strip() != texteCourant.strip():
    page.put(texte, "Sauvegarde du script %s" % line)
  line=f.readline()
