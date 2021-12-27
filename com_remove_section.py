# -*- coding: utf-8 -*-
import pywikibot
import mwparserfromhell
import difflib
from remove_obsolete_sections import remove_obsolete_sections, archive_commons
from pywikibot.pagegenerators import GeneratorFactory
limit=500
commons = pywikibot.Site('commons', 'commons')
frwiki = pywikibot.Site('fr')


def traiteArticles(articles):
    i = 0
    for article in articles:
        main = article.toggleTalkPage()
        if not main.exists():
            print(main.title() + "n'existe pas : on passe")
        else:
            texte = article.get()
            wikicode = mwparserfromhell.parser.Parser().parse(texte, skip_style_tags=True)
            aSauver, archive = remove_obsolete_sections(wikicode, commons)
            print(article.title(), aSauver)

            if aSauver:
                print(article.title())
                print("".join(difflib.context_diff([x + "\n" for x in texte.split("\n")], [
                    x + "\n" for x in str(wikicode).split("\n")], "before", "after")))

                article.put(
                    str(wikicode), "Retrait et archivage des annonces de demande de suppression Commons obsolètes", asynchronous=True)
                i += 1
                archive_commons(frwiki, article, archive)
            if i >= limit:
                print("%d pages modifiées : arrêt" % limit)
                break

nomCateg = "Catégorie:Page contenant un fichier proposé à la suppression sur Commons"
categ = pywikibot.Category(frwiki, nomCateg)
traiteArticles(categ.articles())

gen_factory = GeneratorFactory()
args=["-ns:1", '''-search:insource:"fichier proposé à la suppression" -intitle:"Archive Commons" -incategory:"Page contenant un fichier proposé à la suppression sur Commons"''']
for arg in args:
    print(arg)
    gen_factory.handle_arg(arg)
gen = gen_factory.getCombinedGenerator()
if gen:
    traiteArticles(gen)

