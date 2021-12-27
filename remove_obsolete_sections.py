# -*- coding: utf-8 -*-
import pywikibot


def remove_obsolete_sections(wikicode, commons):
    aSauver = False
    archive = ""
    for section in wikicode.get_sections(levels=[2], matches="suppression sur Commons", include_lead=False):
        print("Section :", section)
        templates = section.filter_templates()
        for template in templates:
            nocat = True
            if template.has('nocat'):
                if template.name == "Fichier proposé à la suppression sur Commons":
                    aSauver = True
                    archive = replace_section(archive, section)
                    print("section 1" + str(section))
                break
            if template.name == "Fichier proposé à la suppression sur Commons":
                chemin = str(template.get('fichier').value).replace('[[:', '').replace(
                        '[[c:Fichier:', 'File:').replace(']]', '').strip()
                fichierCommons = pywikibot.Page(commons, chemin)
                if not fichierCommons.exists():
                    aSauver = True
                    archive = replace_section(archive, section)
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
                    archive = replace_section(archive, section)
                    print("section 3" + str(section))
    return aSauver, archive

def replace_section(archive, section):
    lines_archive = []
    lines_conserver = []
    conserver = False
    for line in str(section).split("\n"):
        if line.startswith("{{") and not line.startswith("{{Fichier proposé") and not line.startswith("{{RI"):
            conserver = True
        if line.startswith("==") and "suppression sur Commons" in line:
            conserver = False
        if conserver:
            lines_conserver += [line]
        else:
            lines_archive += [line]
    if len(lines_conserver)>0:
        lines_conserver += ['']
        if lines_conserver[-2] != '':
            lines_conserver += ['']
        if lines_conserver[-3] != '':
            lines_conserver += ['']
    if len(lines_archive)>0:
        lines_archive += ['']
        if lines_archive[-2] != '':
            lines_archive += ['']
        if lines_archive[-3] != '':
            lines_archive += ['']
    print(lines_conserver)
    print(lines_archive)
    archive += "\n".join(lines_archive)
    print("nouvelle section", "\n".join(lines_conserver),"fin nouvelle section")
    section.replace(section, "\n".join(lines_conserver))
#    section.replace(section, "x\n")
    return archive

def archive_commons(site, talkPage, texte):
    page_archive = pywikibot.Page(site, talkPage.title()+"/Archive Commons")
    if page_archive.exists():
        texteArchive=page_archive.get()+"\n\n"+texte
    else:
        texteArchive=texte
    page_archive.put(texteArchive, "Archivage des demandes de suppression Commons")
    if texte.count("Discussion utilisateur") != texte.count("Discussion utilisateur:NaggoBot") or texte.count("{{") != (texte.count("{{Fichier proposé")+texte.count("{{m|")) or texte.count("== ") != (texte.count("== Fichier proposé")+texte.count("== Fichiers proposés")):
        print("Page à vérifier : %s" % page_archive.title())
        page_verif=pywikibot.Page(site, "Utilisateur:NaggoBot/Vérification Archive Commons")
        texte_verif = page_verif.get()+"\n# [[%s]]" % page_archive.title()
        page_verif.put(texte_verif, "Page à vérifier : [[%s]]" % page_archive.title(), asynchronous=True)
