from bs4 import BeautifulSoup
from helpers.proxies import responseThruProxy
import requests
import random
import math


def getValStats(valName, AllFromQueue):
  valName = valName.split("#")
  name = valName[0].replace(" ", "%20")
  tag = valName[1]
  cookies = {
      'cf_chl_2': '67b065257ccf1ec',
      'cf_chl_prog': 'x11',
      'cf_clearance': 'agbsrtVNs2FnsTNJqbFAFUupK943xAjiY3AgwDiaH1M-1647815259-0-150',
  }

  headers = {
      'authority': 'tracker.gg',
      'cache-control': 'max-age=0',
      'upgrade-insecure-requests': '1',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'sec-gpc': '1',
      'sec-fetch-site': 'same-origin',
      'sec-fetch-mode': 'navigate',
      'sec-fetch-user': '?1',
      'sec-fetch-dest': 'document',
      'referer': 'https://tracker.gg/valorant/profile/riot/41619%23NA1/overview?__cf_chl_tk=e9QE0WXKhy0MVH0vu.Cv9xHUPkCTyjX5EJQ4AXPHolo-1647815258-0-gaNycGzNByU',
      'accept-language': 'en-US,en;q=0.9',
      # Requests sorts cookies= alphabetically
      # 'cookie': 'cf_chl_2=67b065257ccf1ec; cf_chl_prog=x11; cf_clearance=agbsrtVNs2FnsTNJqbFAFUupK943xAjiY3AgwDiaH1M-1647815259-0-150',
      'if-modified-since': 'Sun, 20 Mar 2022 21:22:30 GMT',
  }
  URL = f"https://tracker.gg/valorant/profile/riot/{name}%23{tag}/overview"

  if AllFromQueue:
    URL += "?season=all"
  
  s = requests.Session()

  page = s.get(URL, headers = headers, cookies = cookies)
    
  soup = BeautifulSoup(page.content, "html.parser")
  
  hs = soup.find("span", text="Headshot%").find_next("span").text[:-1]
  dmg = soup.find("span", text="Damage/Round").find_next("span").text
  kad = soup.find("span", text="KAD Ratio").find_next("span").text

  matches = int(soup.find("span", class_="matches").text.split(" ")[10])
  kda = float(soup.find("span", text="KAD Ratio").find_next("span").text)
  dmgr = float(soup.find("span", text="Damage/Round").find_next("span").text[:-2])
  winRate = float(soup.find("span", text="Win %").find_next("span").text[:-2])
  
  return {
    "HS": float(hs),
    "DMG": float(dmg),
    "KDA": float(kad),
    "POINTS": getPoints(matches, kda, dmgr, winRate)
  }

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

