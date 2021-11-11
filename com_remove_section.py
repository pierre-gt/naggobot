# -*- coding: utf-8 -*-
import pywikibot
import mwparserfromhell
import difflib
from remove_obsolete_sections import remove_obsolete_sections
commons = pywikibot.Site('commons', 'commons')
frwiki = pywikibot.Site('fr')


def traiteCateg(categ):
    i = 0
    for article in categ.articles():
        texte = article.get()
        wikicode = mwparserfromhell.parser.Parser().parse(texte, skip_style_tags=True)
        aSauver = remove_obsolete_sections(wikicode, commons)
        print(article.title(), aSauver)

        if aSauver:
            print(article.title())
            print("".join(difflib.context_diff([x + "\n" for x in texte.split("\n")], [
                  x + "\n" for x in str(wikicode).split("\n")], "before", "after")))

            article.put(
                str(wikicode), "Retrait des annonces de demande de suppression Commons obsolètes", asynchronous=True)
            i += 1
        if i > 500:
            print("500 pages modifiées : arrêt")
            break



nomCateg = "Catégorie:Page contenant un fichier proposé à la suppression sur Commons"
categ = pywikibot.Category(frwiki, nomCateg)
traiteCateg(categ)
