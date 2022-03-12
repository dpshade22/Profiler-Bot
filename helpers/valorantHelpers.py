import requests
import random
import math
from bs4 import BeautifulSoup

header = {}

def compKDA(valName, AllFromQueue):
  valName = valName.split("#")
  name = valName[0].replace(" ", "%20")
  tag = valName[1]
  rand1, rand2 = random.randint(0, 200), random.randint(0, 200)

  randTrue = random.choice([True, False])  
  
  URL = f"https://tracker.gg/valorant/profile/riot/{name}%23{tag}/overview"

  if AllFromQueue:
    URL += "?season=all"
  elif randTrue:
    URL += "/"
  
  page = requests.get(URL, headers = {"X-Forwarded-For": f"192.{rand1}.1.{rand2}"})
  page.raise_for_status()
  
  soup = BeautifulSoup(page.content, "html.parser")
  
  kad = soup.find("span", text="KAD Ratio").find_next("span").text
  return kad


def compHS(valName, AllFromQueue):
  valName = valName.split("#")
  name = valName[0].replace(" ", "%20")
  tag = valName[1]
  rand1, rand2 = random.randint(0, 200), random.randint(0, 200)

  randTrue = random.choice([True, False])

  
  URL = f"https://tracker.gg/valorant/profile/riot/{name}%23{tag}/overview"
  
  if AllFromQueue:
    URL += "?season=all"
  elif randTrue:
    URL += "/"
    
  page = requests.get(URL, headers = {"X-Forwarded-For": f"192.{rand1}.1.{rand2}"})
  page.raise_for_status()
    
  soup = BeautifulSoup(page.content, "html.parser")
  
  hs = soup.find("span", text="Headshot%").find_next("span").text
  hs +=  " in the " + soup.find("span", text="Headshot%").find_next("span").find_next("span").text.lower()

  return hs

def dmgPerRound(valName, AllFromQueue):
  valName = valName.split("#")
  name = valName[0].replace(" ", "%20")
  tag = valName[1]
  rand1, rand2 = random.randint(0, 200), random.randint(0, 200)

  randTrue = random.choice([True, False])

  URL = f"https://tracker.gg/valorant/profile/riot/{name}%23{tag}/overview"
  
  if AllFromQueue:
    URL += "?season=all"
  elif randTrue:
    URL += "/"
    
  page = requests.get(URL, headers = {"X-Forwarded-For": f"192.{rand1}.1.{rand2}"})
  page.raise_for_status()

  soup = BeautifulSoup(page.content, "html.parser")
  
  dmg = soup.find("span", text="Damage/Round").find_next("span").text
  
  return float(dmg)

def getValPoints(valName, AllFromQueue):
  valName = valName.split("#")
  name = valName[0].replace(" ", "%20")
  tag = valName[1]
  rand1, rand2 = random.randint(0, 200), random.randint(0, 200)

  randTrue = random.choice([True, False])

  URL = f"https://tracker.gg/valorant/profile/riot/{name}%23{tag}/overview"
  
  if AllFromQueue:
    URL += "?season=all"
  elif randTrue:
    URL += "/"
    
  page = requests.get(URL, headers = {"X-Forwarded-For": f"192.{rand1}.1.{rand2}"})
  page.raise_for_status()

  soup = BeautifulSoup(page.content, "html.parser")

  matches = int(soup.find("span", class_="matches").text.split(" ")[10])
  kda = float(soup.find("span", text="KAD Ratio").find_next("span").text)
  dmgr = float(soup.find("span", text="Damage/Round").find_next("span").text[:-2])
  winRate = float(soup.find("span", text="Win %").find_next("span").text[:-2])

  return getPoints(matches, kda, dmgr, winRate)

def getPoints(matches, kda, dmgr, winRate):
  c = 0.4 * (math.log(matches) + 1)
  points =  0.5 * (c * 4 * kda) + 0.5 * (c * winRate + c * dmgr)
  return round(points, 2)

def playerValorantProfile(valName, valQuery):
  return f"""
      _{valName}'s Valorant Stats:_
    -----------------------------------------------
      _Points_: ***{valQuery['points']}***
      _Current KDA_: ***{valQuery['currKda']}***
      _Current HS%_: ***{valQuery['currHS']}***
      _Current Damage/Round_: ***{valQuery['currDmg/Round']}***
      
      _Overall KDA_: ***{valQuery['allKda']}***
      _Overall HS%_: ***{valQuery['allHS']}***
      _Overall Damage/Round_: ***{valQuery['allDmg/Round']}***
      """