from bs4 import BeautifulSoup
from helpers.valSeasons import getSeasonAndAct
import requests
import random
import math
import json

def getValStats(valName, allSeasons):
    url = f"https://dak.gg/valorant/api/v1/profile/{valName.replace('#', '-')}/matches"

    season, act = getSeasonAndAct()

    
  
    querystring = {"season": f"s{season}", "act": f"act{act}"}
  
    payload = ""
    headers = {
        "authority": "dak.gg",
        "accept": "application/json, text/plain, */*",
        "x-xsrf-token": "eyJpdiI6InZ0QzljN3NlelIydFdIMC82c1JVS1E9PSIsInZhbHVlIjoiOHJDaEZsVTR2eTErY2xidVE4VDg5ZzdvN1lJbjVodFFidTg4a0VsZG1heUZSTktTZ2ZjTFNVS3VPdGY5c3hyRzA2QWVlbFRiV0ZLQTFHanphZ0lqWThBMTRHT3paeVU2UllLK0VqOWdhb0FXcEs0K1d2d003aXNUMXJDS2RmaVMiLCJtYWMiOiI1NDY4OWExZGIzZGU5NzJlYzdlZjFjMTAyMDcwYWMwMWNlYjMwOWFlNmQxZmM3YmQ3MDllYmVmNTFmY2I0MmJjIn0=",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "sec-gpc": "1",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": f"https://dak.gg/valorant/profile/{valName.replace('#', '-')}",
        "accept-language": "en-US,en;q=0.9"
    }

    valName = valName.split("#")
    name = valName[0].replace(" ", "%20")
    tag = valName[1]

    s = requests.Session()
    s.get(f"https://dak.gg/valorant/profile/{name}-{tag}/renew")
    
    r = s.request("GET", url, data=payload, headers=headers, params=querystring)
    r = r.json()

    kTotal, dTotal, aTotal, wTotal, hsrTotal, dmgrTotal, pointsTotal, fbsTotal = 0, 0, 0, 0, 0, 0, 0, 0
    matches = [] 
  
    if not allSeasons:
      for match in r["data"]:
          if match["game_mode"] == "competitive":
              matches.append(match)
    else:
      s.get(f"https://dak.gg/valorant/profile/{name}-{tag}/renew")
      
      
      iterSeason, iterAct = int(season), int(act)

      while iterSeason > 0:
     
        querystring = {"season": f"s{iterSeason}", "act": f"act{iterAct}"}

        r = s.request("GET", url, data=payload, headers=headers, params=querystring)
        r = r.json()
        # print(json.dumps(r, indent = 2))
        
        for match in r["data"]:
          if match["game_mode"] == "competitive":
              matches.append(match)
  
        if iterAct == 1:
            iterAct = 3
            iterSeason -= 1

        else:
            iterAct -= 1

            
    for match in matches:
        kTotal += match["kills"]
        dTotal += match["deaths"]
        aTotal += match["assists"]
        hsrTotal += match["headshots_rate"]
        dmgrTotal += match["damage"]
        pointsTotal += match["score"]
        fbsTotal += match["first_bloods"] / (match["points"]["Red"] + match["points"]["Blue"])
      
        if match["result_code"] == "victory":
            wTotal += 1

        # print(json.dumps(match, indent=2))
    
    games = len(matches)
    kda = round(float((kTotal + aTotal) / dTotal), 2)
    hsr = round(float(hsrTotal / games), 2)
    dmgr = round(float(dmgrTotal / games), 2)
    wr = round(float(wTotal / games), 2)
    points = round(float(pointsTotal / games), 2)
    fbr = round(float(fbsTotal / games), 2)
  
    return {
    "HS": hsr,
    "DMGR": dmgr,
    "KDA": kda,
    "WR": wr,
    "FBR": fbr,
    "POINTS": points,
    "MATCHES": matches,
    }

def playerValorantProfile(valName, valQuery):
  return f"""
      _{valName}'s Current Season's Valorant Stats:_
    -----------------------------------------------
      _Points_: ***{valQuery['points']}***
      
      **CURRENT**
      _Current KDA_: ***{valQuery['currKDA']}***
      _Current HS%_: ***{valQuery['currHS']}***
      _Current Damage/Round_: ***{valQuery['currDmg/Round']}***
      _Current First Blood Rate_: ***{valQuery['currFBR']}***
      
      **OVERALL**
      _Overall KDA_: ***{valQuery['allKDA']}***
      _Overall HS%_: ***{valQuery['allHS']}***
      _Overall Damage/Round_: ***{valQuery['allDmg/Round']}***
      _Overall First Blood Rate_: ***{valQuery['allFBR']}***
      """

