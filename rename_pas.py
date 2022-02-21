# -*- coding: utf-8 -*-
import pywikibot
from pywikibot.pagegenerators import GeneratorFactory
pywikibot.config.put_throttle=0
site=pywikibot.Site('fr')
gen_factory = GeneratorFactory()
args=["-ns:1", '''-search:intitle:"/Suppression" -intitle:"Admissibilité"''']
for arg in args:
    print(arg)
    gen_factory.handle_arg(arg)
gen = gen_factory.getCombinedGenerator()
if gen:
    for article in gen:
        titre=article.title()
        if titre.endswith("/Suppression"):
            titre_adm=titre.replace("/Suppression", "/Admissibilité")
            if not article.isRedirectPage() and not pywikibot.Page(site, titre_adm).exists():
                try:
                    article.move(newtitle=titre_adm, reason="bot : application de [[Wikipédia:Prise de décision/Réforme et renommage de « Wikipédia:Page à supprimer »]]")
                    print(titre, titre_adm)
                except Exception as e:
                    print("impossible de renommer %s en %s :" % (titre, titre_adm), e)

