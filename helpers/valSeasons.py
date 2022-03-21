import requests
import json
from datetime import datetime, date

def getLastSeasonUUID():
    r = requests.get('https://valorant-api.com/v1/seasons/competitive').json()
    for i, season in enumerate(r["data"]):
        endTime = season["endTime"]
        startTime = season["startTime"]
        if (datetime.strptime(endTime, "%Y-%m-%dT%H:%M:%SZ") < datetime.now()) and (datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%SZ") < datetime.now()):
            return r["data"][i - 3]["seasonUuid"]

def getSeasonAndAct():
    r = requests.get(f'https://valorant-api.com/v1/seasons/{getLastSeasonUUID()}').json()
    assetPath = r["data"]["assetPath"]
    season = assetPath[assetPath.find("Episode") + 7]
    act = assetPath[assetPath.find("Act") + 3]
    return season, act
  