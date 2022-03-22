import os
from bs4 import BeautifulSoup
from helpers.valSeasons import getSeasonAndAct
import requests
import random
import math
import json

def getValStats(wildName, allSeasons):
    url = "https://na.wildstats.gg/en/profile/gameid"
    
    querystring = {"_token": os.environ["_wildriftToken"],"gameid": f"{wildName}"}
    
    payload = ""
    headers = {
        "cookie": "locale=en; region=na; 8NGpu9jqKvaxfwaxYgsbRZPPZxSoPEpBn2EbMpGs=eyJpdiI6InZGOGQ3MDJzVEFiNWp1WlBsc0x3N3c9PSIsInZhbHVlIjoiNUtQOFZ0a1RBZnJVZURGODNybFBDUXF6MndTUlo0eDFBSXpRakdZalVZbU1lNzBqaVpJeDJNRDIyOE8xemRhMXNXNEtXdzh1dCtVcjRNZ1A2ZjRGQk9zcFdCMm95TTgzTFFWZnN2VUJvYnVUT1Bzd2hmb2ZKaEJyR0tPTC9idWlsY3hNTmJOUTc5RWpmaW1wSXM4RmhqaVNtNEh3ZW8raTFjbktVUE9Bd2hWVnFzRVpwaDh2UVQybUNDaktXVzBaR1FRZms4ZllObzloVitCRTFGbTJLRHoreENUSW9YZ2tUTndCN3lCWVlVeTM1TEVHS2dhcVl4STBsSVFMUERMUmZpanhFVm5SSkdqNDlINXFkUHkxcWY4dFJBQUE0UWc3d2x3Z1lGVEFiVG9BNHVVZVBqNFZjU1licjR4d3lrR2krenJ2V3hOSldObXBIVUpuYXpGc0c5RDhKRGZLK1g1UC92UlF0Ujdac0Fmc3libjMxUmorck94SWI2Wnkxd09xTytORHdDSFNLNjJlb056bTFnSXIyL0o2eWpOdjA1dXQ5LzZXRjRRSmwzOD0iLCJtYWMiOiJjMmFhNTIzZWVjYTNmY2RiYWRmYjVlZGQ4NjllNTQ1OTk1ZDU3MWJiNjJiOWNhMWY2YWI3MTIwMTlmOTNmNWZmIn0%253D",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-gpc": "1",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://na.wildstats.gg/en?",
        "accept-language": "en-US,en;q=0.9"
    }
    s = requests.Session()
    r = s.request("POST", url, data=payload, headers=headers, params=querystring)

    matches = [] 
  
    if not allSeasons and r.get("data") != None:
      for match in r["data"]:
          if match["game_mode"] == "competitive":
              matches.append(match)
            
    elif r.get("data") != None:
      s.get(f"https://dak.gg/valorant/profile/{valName.replace('#', '-')}/renew")
      
      
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

    if games == 0:
      dTotal = 1
      games = 1
  
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

