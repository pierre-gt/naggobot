import pywikibot
import mysql.connector
from bs4 import BeautifulSoup

def text_if_div(x):
    if x.find('div') is None:
        return("")
    else:
        return(x.find('div').text)

site = pywikibot.Site('fr')

frwiki_p = mysql.connector.connect(host='frwiki.analytics.db.svc.wikimedia.cloud', db='frwiki_p', option_files="/data/project/naggobot/replica.my.cnf")
cursor=frwiki_p.cursor(dictionary=True)
cursor.execute("select rev_id, rev_parent_id, page_id, page_namespace, page_title from revision join page on rev_page=page_id where rev_actor=223 and rev_comment_id=76735128 and rev_id > 187399937 order by rev_id;")
for result in cursor.fetchall():
    rev_parent = int(result['rev_parent_id'])
    rev_id = int(result['rev_id'])
    page = result['page_title']
    print(page.decode(), rev_id)

    try:
        html=site.compare(rev_id,rev_parent)
        soup=BeautifulSoup(html)
        texte="\n".join(list(map(lambda x: text_if_div(x), soup.findAll('td', attrs={'class':'diff-addedline'}))))
        main=pywikibot.Page(site, page.decode())
        if main.exists():
            talkPage=main.toggleTalkPage()
            archivePage=pywikibot.Page(site,talkPage.title()+"/Archive Commons")
            if archivePage.exists():
                texte=texte+"\n"+archivePage.get()
            archivePage.put(texte, "Archivage des demandes de suppression Commons")
    except Exception as e:
        print("Erreur : ", e)


