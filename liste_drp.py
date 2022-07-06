# -*- coding: utf-8 -*-
import pywikibot
import mwparserfromhell
import re
from datetime import datetime, timedelta
import urllib.parse
from ipaddress import ip_address, IPv4Address
  
def validIPAddress(IP: str) -> str:
    try:
        return "IPv4" if type(ip_address(IP)) is IPv4Address else "IPv6"
    except ValueError:
        return "Invalid"

class ListeDrp:
    def __init__(self):
        self.frwiki = pywikibot.Site('fr')
        self.users_sysop=[]
        self.users_non_sysop=[]


    def calcule_date(self, min_date, max_date, min_user, max_user, user, line, max_date_sysop, max_user_sysop):
        les_mois = {
            "janvier": "01",
            "février": "02",
            "mars": "03",
            "avril": "04",
            "mai": "05",
            "juin": "06",
            "juillet": "07",
            "août": "08",
            "septembre": "09",
            "octobre": "10",
            "novembre": "11",
            "décembre": "12"
            }

        try:
            if user not in self.users_non_sysop and user not in self.users_sysop:
                user_wiki = pywikibot.User(self.frwiki, user)
                if 'sysop' in user_wiki.groups():
                    self.users_sysop+=[user]
                else:
                    self.users_non_sysop+=[user]

            match_date = re.compile("(?P<day>[0-9]+) *(?P<month>[^ ]+) *(?P<year>20[0-9]{2}) *à *(?P<hours>[0-9]{2})[h:](?P<minutes>[0-9]{2})")
            date_msg = match_date.search(line)
            text_date = "%s %s %s %s:%s" % (date_msg.group('day'), les_mois[date_msg.group('month')], date_msg.group('year'), date_msg.group('hours'), date_msg.group('minutes'))
            date_msg = datetime.strptime(text_date, "%d %m %Y %H:%M")
            if date_msg < min_date:
                min_date = date_msg
                min_user = user
            if user in self.users_non_sysop:
                if date_msg > max_date:
                    max_date = date_msg
                    max_user = user
            else:
                if date_msg > max_date_sysop:
                    max_date_sysop = date_msg
                    max_user_sysop = user

            return (min_date, max_date, min_user, max_user, max_date_sysop, max_user_sysop)
                            
        except Exception as e:
            print("erreur dans la date", e)
            return (min_date, max_date, min_user, max_user, max_date_sysop, max_user_sysop)

    def traitement(self):
        nom_page_drp='Wikipédia:Demande de restauration de page'

        page_drp=pywikibot.Page(self.frwiki, nom_page_drp)
        text=page_drp.get()
        wikicode = mwparserfromhell.parser.Parser().parse(text, skip_style_tags=True)
        modele_tableau=""" {| class="wikitable alternance centre sortable"
        |+ %s
        |----
        ! Demande !! scope="col" | Date demande !! scope="col" | Utilisateur demande !! scope="col" | Date dernier message non sysop !! scope="col" | Dernier non sysop !! scope="col" | Date dernier message sysop !! scope="col" | Dernier sysop !! scope="col" | Délai depuis création !! scope="col" | Délai depuis dernier non sysop !! scope="col" | Délai depuis dernier sysop !! scope="col" | taille"""

        tableau_autre = modele_tableau % "Demande de restauration en attente d'autres avis"
        tableau_attente = modele_tableau % "Demande de restauration en attente d'informations"
        tableau_vide = modele_tableau % "Demande de restauration sans statut"

        for section in wikicode.get_sections(levels=[2], include_lead=False):
            min_date=datetime(3000,1,1)
            max_date=datetime(1000,1,1)
            max_date_sysop=datetime(1000,1,1)
            min_user=""
            max_user=""
            max_user_sysop=""
            statut=""
        #    print("section : ", section.filter_headings()[0])
            titre = section.filter_headings()[0]
            templates = section.filter_templates()
            for template in templates:
                if template.has('statut'):
                    statut=template.get('statut').split('=')[1]
                if template.name=="non signé":
                    user=template.get(1)
                    date_msg=str(template.get(2))
                    (min_date, max_date, min_user, max_user, max_date_sysop, max_user_sysop) = self.calcule_date(min_date, max_date, min_user, max_user, user, date_msg, max_date_sysop, max_user_sysop)

            modeles_discussion=["Discussion utilisateur:", "user talk:"]
            for line in str(section).split("\n"):
                for modele in modeles_discussion:
                    pos = line.lower().find(modele.lower())
                    if pos > -1:
                        pos_fin_bar = line.find('|', pos)
                        pos_fin_cro = line.find(']]', pos)
                        if pos_fin_bar > -1 and pos_fin_bar < pos_fin_cro:
                            pos_fin = pos_fin_bar
                        else:
                            pos_fin = pos_fin_cro
                        if pos_fin > -1:
                            user=line[pos+len(modele):pos_fin]
                            (min_date, max_date, min_user, max_user, max_date_sysop, max_user_sysop) = self.calcule_date(min_date, max_date, min_user, max_user, user, line, max_date_sysop, max_user_sysop)
            delai_premier = (datetime.now() + timedelta(hours=2) - min_date).days
            delai_dernier = (datetime.now() + timedelta(hours=2)- max_date).days
            delai_dernier_sysop = (datetime.now() + timedelta(hours=2) - max_date_sysop).days
            print("SECTION", titre,"PREMIER", min_user, min_date, "DERNIER",max_user, max_date, "DERNIER ADMIN",max_user_sysop, max_date_sysop, "STATUT", statut, delai_premier, delai_dernier, delai_dernier_sysop)
            titre_section_MediaWiki = titre[2:-2].strip()
            titre_section_MediaWiki = titre_section_MediaWiki.replace("[[:", "")
            titre_section_MediaWiki = titre_section_MediaWiki.replace("[[", "")
            titre_section_MediaWiki = titre_section_MediaWiki.replace("]]", "")
            texte_lien = titre_section_MediaWiki
            titre_section_MediaWiki = urllib.parse.quote(titre_section_MediaWiki.encode('utf-8'), safe=" /").replace(" ", "_").replace("%", ".")

            lien_drp = "[[%s#%s|%s]]" % (page_drp.title(as_link = False), titre_section_MediaWiki, texte_lien)
            if validIPAddress(min_user) == 'IPv6':
                min_user=min_user[0:14]+'...'
            if validIPAddress(max_user) == 'IPv6':
                max_user=max_user[0:14]+'...'
            ajout="""\n|----
 ! scope="row" | %s
 | %s ||  %s || %s ||%s ||%s || %s || %s || %s ||%s||%d""" % ( lien_drp, min_date.date(), min_user, max_date.date(), max_user, max_date_sysop.date(), max_user_sysop, delai_premier, delai_dernier, delai_dernier_sysop, len(str(section)))
            if statut == "attente":
                tableau_attente+=ajout
            if statut == "autre" or statut == "autreavis":
                tableau_autre+=ajout
            if statut == "":
                tableau_vide+=ajout
        tableau_attente+="\n|}"
        tableau_autre+="\n|}"
        tableau_vide+="\n|}"
        texte_page = '''{{Wikipédia:Demande de restauration de page/Onglets}}

== Demandes en attente d'autres avis ==
{{raccourci|WP:DRP/SV}}
Les demandes de restauration dans ce tableau attendent des avis supplémentaires de la part d'admin.

%s

== Demandes en attente d'informations ==

Les demandes dans ce tableau sont en attente d'éléments supplémentaires de la part de la personne ayant fait la demande (sources supplémentaires, brouillon publiable ...)

%s

== Demandes sans statut ==

Les demandes dans ce tableau n'ont pas encore eu un statut attribué

%s''' % (tableau_autre, tableau_attente, tableau_vide)
        pageNaggo = pywikibot.Page(self.frwiki, "Wikipédia:Demande de restauration de page/Suivi")
        pageNaggo.put(texte_page, "Suivi des DRP")


            
if __name__ == '__main__':
    bot = ListeDrp()
    bot.traitement()
