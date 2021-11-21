# -*- coding: utf-8 -*-
import pywikibot, mwparserfromhell
import hashlib, os
import pathlib

from remove_obsolete_sections import remove_obsolete_sections
cachePath='/data/project/naggobot/naggobot/.drcache/'
pathlib.Path(cachePath).mkdir(parents=True, exist_ok=True)
listeCaches=set()
commons=pywikibot.Site('commons','commons')
frwiki=pywikibot.Site('fr')
listDRtext='''{{bots|deny=CommonsDelinker}}\n {| class="wikitable alternance centre sortable"
 |+ Fichiers proposés à la suppression
 |----
 ! Fichier !! scope="col" | Lien vers le fichier !! scope="col" | Pages liées !! scope="col" | Motif !! scope="col" | Sous-page !! scope="col" | Date\n'''
def findusage(page, type):
	first=True
	usages=[]
	for usage in frwiki.imageusage(page):
		if first:
			first=False
		# pas les pages listées sur la sous-page du bot
		if ":NaggoBot/" not in str(usage):
			usages.append(usage)
	if not first:
		textFile,dejaTraite=readDesc(page)
		wikicode = mwparserfromhell.parser.Parser().parse(textFile)
		templates = wikicode.filter_templates()
		deleteTemplate=None
		if type=="DR":
			templateList=['delete','del','deletebecause','puf','ffd']
		if type=="nsd":
			templateList=['nsd','no source since','no_source_since']
		if type=="nld":
			templateList=['nld','no license since','no_license_since']
		if type=="npd":
			templateList=['npd','no permission since','no_permission_since']
		for template in templates:
			if template.name.lower().strip() in templateList:
				deleteTemplate=template
				break

		return usages, deleteTemplate, dejaTraite
	return None, None, None

def readDesc(page):
	global cachePath, listeCaches
	cacheFile=hashlib.sha1(page.title().encode('utf-8')).hexdigest()
	listeCaches.add(cacheFile)
	if os.path.isfile(cachePath+cacheFile):
		print(page.title() + " en cache : " + cacheFile)
		f=open(cachePath+cacheFile,'r')
		return f.read(), True
	else:
		f=open(cachePath+cacheFile,'w')
		text=page.get()
		f.write(text)
		return text, False
		
	
	
def articles(catDR, type):
	global listDRtext
	i=0
	for page in catDR.articles():
		# ne devrait pas arriver mais j'ai eu le cas ...
		if page.namespace()!=6:
			continue
		usages, deleteTemplate, dejaTraite = findusage(page, type)
		if usages is not None and len(usages) > 0:
			i+=1
			print(page, usages, end=' ')
			cheminImage=str(page).replace('commons','')
			image=cheminImage.replace('[[:','[[').replace(']]','|100px]]')
			# TODO peut-être overkill ?
			cheminImage=cheminImage.replace('[[File:','[[:c:File:')
			cheminImage=cheminImage.replace('[[:File:','[[:c:File:')
			pagesliees=''
			i=0
			for pageliee in usages:
				pagesliees+=str(pageliee)+' '
				# limite pour ne pas surcharger la page si une image très utilisée est listée
				i+=1
				if i >= 15:
					pagesliees+= "%d utilisations au total" % len(usages)
					break
			motif, souspage, date=parseTemplate(deleteTemplate, type)

			tableDR = '''|----
 ! scope="row" | %s
 | %s || %s || %s || %s || %s\n'''

			deletionRequest = tableDR % (image, cheminImage, pagesliees, motif, souspage, date)
			listDRtext += deletionRequest
			# espace principal
			compteur=0
			for pageliee in usages:
				compteur+=1
				# pas plus de 10 pages pour éviter un flood si l'image est très utilisée
				if compteur==10:
					break
				if pageliee.namespace()==0 and not dejaTraite:
					talkPage=pageliee.toggleTalkPage()
					if talkPage.exists():
						textTalkPage=talkPage.get()
						wikicode = mwparserfromhell.parser.Parser().parse(textTalkPage, skip_style_tags=True)
						aSauver = remove_obsolete_sections(wikicode, commons)
						if aSauver:
							textTalkPage=str(wikicode)
					else:
						textTalkPage=""
					# ajout d'un message sur la page de discussion associée
					textTalkPage+="\n\n== Fichier proposé à la suppression sur Commons ==\n{{Fichier proposé à la suppression sur Commons|fichier=%s|motif=%s|sous-page=%s}}\nMessage déposé automatiquement par un robot le ~~~~~." % (cheminImage, motif, souspage)
					talkPage.put(textTalkPage, "Annonce de fichier proposé à la suppression")

			

def parseTemplate(deleteTemplate, type):
	motif=''
	souspage=''
	date=''
	if deleteTemplate is not None:
		if type == "DR":
			if deleteTemplate.has('reason'):
				print("motif : " + str(deleteTemplate.get('reason').value))
				motif = str(deleteTemplate.get('reason').value)
				motif = motif.replace('{{','{{m|').replace('[[COM:','[[:c:COM:')
				motif = motif.replace('[[Category:','[[:Category:')
				motif = motif.replace('[[Commons:','[[:c:Commons:')
				motif = motif.replace('[[Com:','[[:c:Com:')
				motif = motif.replace("\n"," ")
			if deleteTemplate.has('subpage'):
				souspage='[[:commons:Commons:Deletion_requests/' + str(deleteTemplate.get('subpage').value).strip() + '|lien]]'
			# contre-mesure pour éviter de répercuter des messages diffamatoires venus de commons
			motif=''
		else:
			# pour nsd/nld/npd il n'y a pas de sous-page, le motif est directement sur l'image
			if type=="nsd":
				motif="Pas de source indiquée"
			if type=="nld":
				motif="Pas de licence indiquée"
			if type=="npd":
				motif="Pas de permission indiquée"
			
			
		if deleteTemplate.has('month'):
			date=str(deleteTemplate.get('month').value).strip()
		if deleteTemplate.has('day'):
			date+=" "+str(deleteTemplate.get('day').value).strip()
		if deleteTemplate.has('year'):
			date+=" "+str(deleteTemplate.get('year').value).strip()
	return motif, souspage, date


def parseCategory(catName, catPrefix, type):
	catSelected = pywikibot.Category(commons, 'Category:%s' % catName)
	catGenerator = catSelected.subcategories()

	for catDR in catGenerator:
		print(catDR.title())
		# quickfix moche parce que la catégorie est trop grosse pour être traitée via cette api
		if catDR.title().startswith('Category:%s' % catPrefix) and not "Deletion requests December 2019" in catDR.title():
			articles(catDR, type)


catName="Deletion requests"

parseCategory("Media without a source","Media without a source as of","nsd")
parseCategory("Media missing permission","Media missing permission as of","npd")
parseCategory("Media without a license","Media without a license as of","nld")
parseCategory("Deletion requests","Deletion request","DR")

listDRtext+='|}'
# NS Discussion utilisateur pour éviter que CommonsDelinker vienne y toucher
listDRpage='Discussion utilisateur:NaggoBot/CommonsDR'

pagecible=pywikibot.Page(frwiki,listDRpage)
pagecible.put(listDRtext,"Mise à jour des fichiers Commons proposés à la suppression")

files = []
for (dirpath, dirnames, filenames) in os.walk(cachePath):
    files.extend(filenames)
    break

print("Suppression des fichiers cache devenus inutiles")
for file in files:
	if file not in listeCaches:
		print(cachePath+file)
		os.remove(cachePath+file)
