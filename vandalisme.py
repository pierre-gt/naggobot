# -*- coding: utf-8 -*-
import pywikibot
import datetime
import time
from pywikibot import date
import pytz

def dateAffichage(dateBlTxt):
    dateBl=datetime.datetime.strptime(dateBlTxt, u"%Y-%m-%dT%H:%M:%SZ")
    dateBl=pytz.timezone("UTC").localize(dateBl).astimezone(pytz.timezone("Europe/Paris"))
    dateTexte="%d %s %d à %02d:%02d:%02d" % (dateBl.day, date.formats['MonthName']['fr'](dateBl.month), dateBl.year, dateBl.hour, dateBl.minute, dateBl.second)
    return dateTexte

def dateFinBlocage(finBlocage):
    if finBlocage=='infinity':
        return 'indéfiniment'
    else:
        return "jusqu'au %s" % dateAffichage(finBlocage)

def recupereUsers(line):
  users=[]
  while line.find('[[User:')>0 or line.upper().find('{{IP')>0:
    print(line)
    pos=line.upper().find('{{IP')
    if pos>0:
      posfin=line.find('}}',pos)
      users.append(line[pos+5:posfin].strip())
      line=line[posfin:]
    pos=line.find('[[User:')
    if pos>0:
      posfin1=line.find('|',pos)
      posfin2=line.find(']]',pos)
      if posfin1<posfin2:
        posfin=posfin1
      else:
        posfin=posfin2
      users.append(line[pos+7:posfin].strip())
      line=line[posfin:]
  print(users)
  return users

def recupereUsersU(line):
  users=[]
  while line.find('{{u|') > 0:
    pos=line.find('{{u|')
    if pos>0:
      posfin=line.find('}}',pos)
      users.append(line[pos+4:posfin].strip())
      line=line[posfin:]
  print(users)
  return users

def recupereUsersPlus(line):
  users=[]
  while line.find('{{u+') > 0:
    pos=line.find('{{u+')
    if pos>0:
      posfin=line.find('}}',pos)
      users.append(line[pos+5:posfin].strip())
      line=line[posfin:]
  print(users)
  return users

def recupereUsersContrib(line):
  users=[]
  while line.find('[[Spécial:Contributions/') > 0:
    pos=line.find('[[Spécial:Contributions/')
    if pos>0:
      posfin=line.find(']]',pos)
      users.append(line[pos+24:posfin].strip())
      line=line[posfin:]
  print(users)
  return users

def is_ip_or_range(user):
  if pywikibot.tools.is_ip_address(user):
    return True
  if user.count('/') == 1:
    if pywikibot.tools.is_ip_address(user.split('/')[0]) and user.split('/')[1].isnumeric():
      return True
  return False

def getUsersBlocks(users, site):
  comm=""
  global delai, attente, utc_offset
  debut=datetime.datetime.now()-datetime.timedelta(days=delai)
  debut_utc=debut-datetime.timedelta(seconds=utc_offset)
  fin=datetime.datetime.now()-datetime.timedelta(minutes=attente)
  fin_utc=fin-datetime.timedelta(seconds=utc_offset)
  blocks=[]
  for user in set(users):
    user=user.replace(u"\u200E","")
    user=user.replace(u"\u200F","")
    user=user.replace(u"1=","")
    # Si adresse IPV6 : ne marche qu'en majuscules
    if is_ip_or_range(user):
      print("IP address : %s" % user)
      try:
        blocks+= site.blocks(iprange=user.upper(), total=1, starttime=fin_utc.isoformat(), endtime=debut_utc.isoformat())
      except Exception as e:
        print("Erreur : Impossible de récupérer la liste des blocages pour l'IP %s" % user, e)
    blocks+= site.blocks(users=user, total=1, starttime=fin_utc.isoformat(), endtime=debut_utc.isoformat())
    props = ("id", "by", "timestamp", "expiry", "reason")
  # deduplication
  for bl in [dict(s) for s in set(frozenset(d.items()) for d in blocks)]:
    comm+=":{{Icône information}} {{u|%s}} '''bloqué''' %s par %s le %s.\n:Raison : « %s ». ~~~~\n"% (bl['user'], dateFinBlocage(bl['expiry']), bl['by'], dateAffichage(bl['timestamp']), bl['reason'].replace('{{','{{m|'))
  if comm != "": 
    print(comm)
  return comm
# délai = prendre les blocages faits depuis n jours
delai=1
# attente = ne pas prendre les blocages faits dans les n dernières minutes pour laisser le temps au sysop de renseigner manuellement
attente=0
is_dst = time.daylight and time.localtime().tm_isdst > 0
utc_offset = - (time.altzone if is_dst else time.timezone)

site = pywikibot.Site('fr')
cible='Wikipédia:Vandalisme en cours'
pagecible=pywikibot.Page(site,cible)
texte=pagecible.get()
comment=False
users=[]
texteout=""
commdiff=""
titresection=""
for line in texte.split('\n'):
  if line.startswith("=="):
    if not users is None and not comment:
      try:
        comm=getUsersBlocks(users, site)
        if comm != "":
          texteout+=comm
          commdiff+="/* %s */ " % titresection.replace("==","").strip()
      except Exception as e:
        print("Erreur : Impossible de récupérer la liste des blocages", e)
    comment=False
    titresection=line
    users=[]
  users+=recupereUsers(line)
  if line.find('{{u|') > 0:
    users+=recupereUsersU(line)
  if line.find('{{u+') > 0:
    users+=recupereUsersPlus(line)
  if line.find('[[Spécial:Contributions/') > 0:
    users+=recupereUsersContrib(line)
  if line.startswith(":"):
    comment=True
  texteout+=line+"\n"
if not users is None and not comment:
  try:
    comm=getUsersBlocks(users, site)
    if comm != "":
      texteout+=comm
      commdiff+="/* %s */" % titresection.replace("==","").strip()
  except Exception as e:
    print("Erreur : Impossible de récupérer la liste des blocages", e)
if texteout.strip() != texte.strip():
  #pagecible.put(texteout, "MAJ par bot : Liste de blocages déjà effectués")
  pagecible.put(texteout, commdiff)
