# -*- coding: utf-8 -*-
import pywikibot, mwparserfromhell
import difflib
import sys
import re

# key without spaces

def stripKey(arg):
  if '=' in str(arg):
    return str(arg).split('=')[0].strip()
  else:
    return None

# value without leading or trailing spaces

def stripValue(arg):
  if '=' in str(arg):
    return "=".join(str(arg).split('=')[1:]).strip()
  else:
    return None

# list of args used in the template

def getAllArgs(template):
  allArgs=[]
  for arg in template.params:
    argKey=stripKey(arg)
    if '=' in str(arg) and argKey != "":
      allArgs.append(argKey)
  return allArgs

# list of args used more than once

def getDuplicateArgs(template):
  allArgs=getAllArgs(template)
  duplicateArgs=[]
  prev=None
  for arg in sorted(allArgs):
    if arg==prev:
      if arg not in duplicateArgs:
        duplicateArgs.append(arg)
    prev=arg
  return duplicateArgs

# list of unnamed args
def getUnnamedArgs(template):
  unnamedArgs=[]
  for arg in template.params:
    if not '=' in str(arg):
      unnamedArgs.append(arg)
  return unnamedArgs
  
# first 500 chars of the template

def sampleTemplate(template):
  return str(template)[0:500].replace("\n","").replace("\r","")

# rename the key of the nth (n=argToRename) occurrence of the duplicate argument call
  
def renameArgInTemplate(template, argToRename, dupArg):
  indexInArg=0
  newName=input("New name for argument, change %s to :" % dupArg)
  
  for index, param in enumerate(template.params):
    if stripKey(param)==dupArg:
      indexInArg+=1
      if indexInArg == argToRename:
        template.params[index]=template.params[index].replace(dupArg, newName, 1)

# keep only the nth (n=valueToKeep) occurrence of the duplicate argument call

def keepOneValueInTemplate(template, valueToKeep, dupArg):
  indexInArg=0
  for index, param in enumerate(template.params):
    if stripKey(param)==dupArg:
      indexInArg+=1
      if indexInArg != valueToKeep:
        template.params[index]="argumentToBeDeleted=delete"
  while "argumentToBeDeleted=delete" in template.params:
    template.params.pop(template.params.index("argumentToBeDeleted=delete"))

def templateOK(template):
  if template.name.matches("Climat"):
    return False
  if template.name.matches("Foot classement"):
    return False
  if template.name.matches("Phase finale à 4"):
    return False
  if template.name.matches("Phase finale à 6"):
    return False
  if template.name.matches("Phase finale à 8"):
    return False
  if template.name.matches("Phase finale à 16"):
    return False
  if template.name.matches("Tournoi sur 3 tours"):
    return False
  if template.name.matches("Fstats total"):
    return False
  if template.name.matches("Fstats"):
    return False
  if "Tableau Coupe" in template.name:
    return False
  for x in [str(n) for n in range(1,10)]:
    if x in template.name:
      return False
  return True

# main function : deduplicate a single page
  
def deduplicatePage(page):
  pageHasDuplicate=False
  title=page.title()
  if dupCateg not in page.categories():
    print("%s not in category, skipping" % title)
    return
  text=page.get()
  print("= Page : ",title,' ',page.full_url())
  wikicode = mwparserfromhell.parser.Parser().parse(text, skip_style_tags=True)
  templates = wikicode.filter_templates()
  nDup=0
  for template in templates:
    duplicateArgs=getDuplicateArgs(template)
    unnamedArgs=getUnnamedArgs(template)
    if len(duplicateArgs) > 0:
      print("In template %s :" % sampleTemplate(template))
    for arg in template.params:
      if re.match("^[1-9][0-9]*$",str(stripKey(arg))):
        num=int(stripKey(arg))
        if len(unnamedArgs)>=num:
          print("Argument %s in template %s conflicts with unnamed argument %s - edit manually" % (arg, template.name, unnamedArgs[num-1]))
    for dupArg in duplicateArgs:
      print("* Argument %s has multiple occurrences :" % dupArg)
      pageHasDuplicate=True
      firstValue=None
      hasDistinctValues=False
      hasNonEmptyValues=False
      numberOfValues=0
      values=[]
      lastValue=0
      for arg in template.params:
        if stripKey(arg) == dupArg:
          numberOfValues+=1
          value=stripValue(arg)
          values.append(value)
          if firstValue is None and value not in ["", None]:
            firstValue=value
            hasNonEmptyValues=True
              
          if value not in ["",None]: 
            lastValue=numberOfValues
            if firstValue != value:
              hasDistinctValues=True
      i=0
      nDup+=1
      for value in values:
        i+=1
        print(" * Value %d : %s"	 % (i , value))
      # automatically select an option in simple cases
      if '-auto' in sys.argv:
        if templateOK(template) and not hasDistinctValues and not (dupArg[-1:] in [str(n) for n in range(1,10)]) and (lastValue==i or not hasNonEmptyValues):
          action=str(i)
        else:
          action="s"
      else:
        action=input("s=skip this argument, n=skip this article, 1-%d = keep this value only, r1-r%d = rename this argument :" % (i, i))
      if action=="s":
        continue
      if action=="n":
        return
      valueToKeep=None
      argToRename=None
      if action >= "1" and action <= str(i):
        valueToKeep=int(action)
        keepOneValueInTemplate(template, valueToKeep, dupArg)
      if action >= "r1" and action <= "r"+str(i):
        argToRename=int(action[1:2])
        renameArgInTemplate(template, argToRename, dupArg)
  print("".join(difflib.context_diff([x + "\n" for x in text.split("\n")],[x + "\n" for x in str(wikicode).split("\n")], "before","after")))
  if str(wikicode).strip() != text.strip():
    page.put(str(wikicode),message, asynchronous=True)       
  else:
    if nDup==0 and "-null" in sys.argv:
      action=input("No duplicate found. Null edit ? y/n")
      if action=="y":
        page.put(text,message, asynchronous=True)       

# deduplicate all pages in a category

def parseCateg(categoryName, fromPage=None, namespace=None):
  page=pywikibot.Page(site,categoryName)
  for article in site.categorymembers(page, namespaces=namespace):
    if fromPage is None or article.title() >= fromPage:
      deduplicatePage(article)
#site=pywikibot.Site('ja', 'wiktionary')
#site=pywikibot.Site('fr')
namespace=None
if '-namespace' in sys.argv:
  namespace=sys.argv[sys.argv.index("-namespace")+1]
if '-lang' in sys.argv:
  lang=sys.argv[sys.argv.index("-lang")+1]
else:
  lang='fr'
if '-project' in sys.argv:
  project=sys.argv[sys.argv.index("-project")+1]
else:
  project='wikipedia'
site=pywikibot.Site(lang, project)
# Find out the category
nsCateg=site.namespace(14)
nameCateg=site.mediawiki_message("Duplicate-args-category")
dupCategName=nsCateg+":"+nameCateg
print(dupCategName)
dupCateg=pywikibot.Page(site, dupCategName)
if '-message' in sys.argv:
  message=sys.argv[sys.argv.index("-message")+1]
else:
  if lang=='fr':
    message="[[%s|Correction de modèles utilisant des arguments dupliqués]]" % dupCategName
  else:
    message="[[%s|%s]]" % (dupCategName, nameCateg)
if '-main' in sys.argv:
  namespace='0'
if '-cat' in sys.argv or '-catdup' in sys.argv:
  if '-catdup' in sys.argv:
    categoryName=dupCategName
  else:
    categoryName=sys.argv[sys.argv.index("-cat")+1]
  if '-frompageincat' in sys.argv:
    fromPage=sys.argv[sys.argv.index("-frompageincat")+1]
    print("Parsing category %s from article %s" % (categoryName,fromPage))
  else:
    fromPage=None
  parseCateg(categoryName, fromPage, namespace=namespace)

if '-page' in sys.argv:
  pageName=sys.argv[sys.argv.index("-page")+1]
  page=pywikibot.Page(site, pageName)
  deduplicatePage(page)

if '-linksto' in sys.argv:
  pageName=sys.argv[sys.argv.index("-linksto")+1]
  page=pywikibot.Page(site, pageName)
  for ref in page.getReferences(namespaces=namespace):
    deduplicatePage(ref)
