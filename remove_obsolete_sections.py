# -*- coding: utf-8 -*-
import pywikibot


def remove_obsolete_sections(wikicode, commons):
    aSauver = False
    archive = ""
    for section in wikicode.get_sections(levels=[2], matches="suppression sur Commons"):
        templates = section.filter_templates()
        for template in templates:
            nocat = True
            if template.has('nocat'):
                if template.name == "Fichier proposé à la suppression sur Commons":
                    aSauver = True
                    archive += str(section)
                    section.replace(section, "")
                    print("section 1" + str(section))
                break
            if template.name == "Fichier proposé à la suppression sur Commons":
                chemin = str(template.get('fichier').value).replace('[[:', '').replace(
                        '[[c:Fichier:', 'File:').replace(']]', '').strip()
                fichierCommons = pywikibot.Page(commons, chemin)
                if not fichierCommons.exists():
                    aSauver = True
                    archive += str(section)
                    section.replace(section, "")
                    print("section 2" + str(section))
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
                    aSauver = True
                    archive += str(section)
                    section.replace(section, "")
                    print("section 3" + str(section))
    return aSauver, archive

def archive_commons(site, talkPage, texte):
    page_archive = pywikibot.Page(site, talkPage.title()+"/Archive Commons")
    if page_archive.exists():
        texteArchive=page_archive.get()+"\n"+texte
    else:
        texteArchive=texte
    page_archive.put(texteArchive, "Archivage des demandes de suppression Commons")
