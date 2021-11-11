# -*- coding: utf-8 -*-
import pywikibot


def remove_obsolete_sections(wikicode, commons):
    aSauver = False
    for section in wikicode.get_sections():
        templates = section.filter_templates()
        for template in templates:
            nocat = True
            if template.has('nocat'):
                if template.name == "Fichier proposé à la suppression sur Commons":
                    aSauver = True
                    section.replace(section, "")
                break
            if template.name == "Fichier proposé à la suppression sur Commons":
                chemin = str(template.get('fichier').value).replace('[[:', '').replace(
                        '[[c:Fichier:', 'File:').replace(']]', '').strip()
                fichierCommons = pywikibot.Page(commons, chemin)
                if not fichierCommons.exists():
                    aSauver = True
                    section.replace(section, "")
                    print(chemin, " n'existe plus : on retire la section")
                else:
                    for categCommons in fichierCommons.categories():
                        title = categCommons.title()
                        if title.startswith("Category:Media without a source") or title.startswith("Category:Media missing permission") or title.startswith("Category:Media without a license") or title.startswith("Category:Deletion requests"):
                            nocat = False

                    if nocat:
                        print(
                                "L'image {%s} n'est plus dans les catégories de suppression : retrait" % chemin)
                if nocat:
                    section.replace(section, "")
                    aSauver = True
    return aSauver
