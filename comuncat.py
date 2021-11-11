# -*- coding: utf-8 -*-
import pywikibot, mwparserfromhell
import difflib
commons=pywikibot.Site('commons','commons')
frwiki=pywikibot.Site('fr')

def traiteCateg(categ):
	i=0
	for article in categ.articles():
		texte=article.get()
		wikicode = mwparserfromhell.parser.Parser().parse(texte, skip_style_tags=True)
		templates = wikicode.filter_templates()
		aSauver=False
		for template in templates:
			nocat=True
			if template.has('nocat'):
				break
			if template.name == "Fichier proposé à la suppression sur Commons":
				chemin=str(template.get('fichier').value).replace('[[:','').replace('[[c:Fichier:','File:').replace(']]','').strip()
				fichierCommons=pywikibot.Page(commons, chemin)
				if not fichierCommons.exists():
					print(chemin , " n'existe plus : on retire la catégorie")
				else:
					for categCommons in fichierCommons.categories():
						title=categCommons.title()
						if title.startswith("Category:Media without a source") or title.startswith("Category:Media missing permission") or title.startswith("Category:Media without a license") or title.startswith("Category:Deletion requests") :
							nocat=False
							
					if nocat:
						print("L'image n'est plus dans les catégories de suppression : retrait")
				if nocat:
					template.add("nocat", "oui")
					aSauver=True
				
		if aSauver:
			print(article.title() , nocat)
			print("".join(difflib.context_diff([x + "\n" for x in texte.split("\n")],[x + "\n" for x in str(wikicode).split("\n")], "before","after")))
			article.put(str(wikicode), "Ajout du paramètre nocat sur le [[Modèle:Fichier proposé à la suppression sur Commons]]")
			i+=1
		if i > 500:
			print("500 pages modifiées : arrêt")
			break


				

nomCateg="Catégorie:Page contenant un fichier proposé à la suppression sur Commons"
categ=pywikibot.Category(frwiki, nomCateg)
traiteCateg(categ)

