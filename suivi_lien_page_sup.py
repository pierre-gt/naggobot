# -*- coding: utf-8 -*-

import pywikibot
import datetime
from pywikibot.data import api
import os
#monkeypatch de la fonction pour avoir le filtre sur leaction
if True:
    def f(self, logtype=None, user=None, page=None,
                  start=None, end=None, reverse=False, step=None, total=None, action=None, namespace=None):
        """Iterate all log entries.

        @param logtype: only iterate entries of this type (see wiki
            documentation for available types, which will include "block",
            "protect", "rights", "delete", "upload", "move", "import",
            "patrol", "merge")
        @param user: only iterate entries that match this user name
        @param page: only iterate entries affecting this page
        @param start: only iterate entries from and after this Timestamp
        @param end: only iterate entries up to and through this Timestamp
        @param reverse: if True, iterate oldest entries first (default: newest)

        """
        if start and end:
            self.assert_valid_iter_params('logevents', start, end, reverse)

        legen = self._generator(api.LogEntryListGenerator, type_arg=logtype,
                                total=total)
        if logtype is not None:
            legen.request["letype"] = logtype
        if action is not None:
            legen.request["leaction"] = action
        if user is not None:
            legen.request["leuser"] = user
        if namespace is not None:
            legen.request["lenamespace"] = namespace
        if page is not None:
            legen.request["letitle"] = page.title(withSection=False)
        if start is not None:
            legen.request["lestart"] = str(start)
        if end is not None:
            legen.request["leend"] = str(end)
        if reverse:
            legen.request["ledir"] = "newer"
        return legen

pywikibot.site.logevents=f
site = pywikibot.Site('fr')
delai=2
debut=datetime.datetime.now()-datetime.timedelta(days=delai)
page_rapport=pywikibot.Page(site,"Utilisateur:NaggoBot/Suivi des liens vers une page supprimée")
texte_rapport=""
texte_pas="\n== Suppression PàS ==\n"
texte_redir="\n== Redirections ==\n"
texte_autres="\n== Autres ==\n"
for l in pywikibot.site.logevents(site, action="delete/delete", logtype="delete", total=5000, namespace=0, end=debut.isoformat()):
    # on ne prend que les suppressions qui font référence à une décision PàS
    titre= l.data['title']
    page=pywikibot.Page(site,titre)
    if page.exists():
        continue
	# pas de lien rouge donc OSEF
        #texte_rapport+="\n* La page [[%s]] a été recréée après avoir été supprimée le %s par %s avec le commentaire : %s" % (titre, l.timestamp(), l.user(), l.comment() )
    print(str(l))
    print(l.comment(),':::', l.user(), l.timestamp(), l.data['title'])
    backlinks=page.backlinks(namespaces=0)
    modeledebut=""
    modelefin=""
    couleur=""
    trouve=False
    if "Redirection" in l.comment() or "redirection" in l.comment():
        couleur="Vert"
    if "Discussion" in l.comment() and ("/Suppression" in l.comment() or "/Admissibilité" in l.comment()):
        couleur="Rouge"
    if couleur != "":
        modeledebut="{{%s|" % couleur
        modelefin="}}"
    i=0
    length=-1
    for lien in backlinks:
        trouve=True
        if i==0:
            texte_rapport+="\n* [[Spécial:Pages liées/%s|Pages contenant un lien]] vers [[%s]] , supprimée le %s par %s avec %sle commentaire %s%s :" % (titre, titre, l.timestamp(), l.user(), modeledebut,modelefin,l.comment() )
        if i==10:
            length = sum(1 for x in backlinks)
            break
        texte_rapport+=" [[%s]] " % (lien.title() )
        i+=1
    if length > 0:
        texte_rapport += " (%d pages en plus)" % (length)
    backlinks=page.backlinks(namespaces=10)
    i=0
    for lien in backlinks:
        trouve=True
        if i==0:
            texte_rapport += "\n* Modèles contenant un lien vers [[%s]] :" % titre
        if i==10:
            length = sum(1 for x in backlinks)
            if length > 0:
                texte_rapport += " suite : [[Spécial:Pages liées/%s]] (%d modèles en plus)" % (titre, length)
            break
        texte_rapport+=" [[%s]] " % (lien.title() )
        i+=1
    if couleur=="Vert":
        texte_redir+=texte_rapport
        if trouve:
            moves=site.logevents(page=page.title(), logtype='move', total=10)
            for move in moves:
                texte_redir+="\n** [[%s]] déplacé vers [[%s]] par %s le %s avec le commentaire : %s" % (titre, move.data["params"]["target_title"], move.data["user"], move.data["timestamp"],move.data["comment"])
                dest_title=move.data["params"]["target_title"]
                pagedest=pywikibot.Page(site, dest_title)
                if (not pagedest.exists()):
                    for dest_delete in pywikibot.site.logevents(site, action="delete/delete", logtype="delete", total=5, page=pagedest):
                        texte_redir+="\n*** [[%s]] supprimé par %s le %s avec le commentaire : %s" % (dest_title, dest_delete.user(), dest_delete.timestamp(), dest_delete.comment())
                for move2 in site.logevents(page=dest_title, logtype='move', total=10):
                    texte_redir+="\n*** [[%s]] déplacé vers [[%s]] par %s le %s avec le commentaire : %s" % (dest_title, move2.data["params"]["target_title"], move2.data["user"], move2.data["timestamp"],move2.data["comment"])

    elif couleur=="Rouge":
        texte_pas+=texte_rapport
    else:
        texte_autres+=texte_rapport
    texte_rapport=""
texte_rapport=texte_pas+texte_redir

page_rapport.put(texte_rapport, "Rapport : liens vers des pages supprimées pendant les %d derniers jours" % delai)
