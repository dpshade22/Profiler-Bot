import requests, regex, json
import demjson3 as dj
from bs4 import BeautifulSoup


def parseBattleStats(r):
    r = str(r)

    if r.find("let battleStats = ") == None or r.find("function drawStats") == None:
        return "Stats not found"

    r = r[r.find("let battleStats = ") + 18 : r.find("function drawStats")].replace(
        "'", '"'
    )

    findObj = regex.search(
        r"{(?:[^{}]|(?R))*.}",
        r,
    )

    stats = dj.decode(str(findObj[0]))

    for key, value in stats["allBattles"].items():
        stats["allBattles"][key] = float(str(value).replace(",", ""))
    for key, value in stats["normalBattles"].items():
        stats["normalBattles"][key] = float(str(value).replace(",", ""))
    for key, value in stats["rankedBattles"].items():
        stats["rankedBattles"][key] = float(str(value).replace(",", ""))

    print(stats)

    return stats


def getWildStats(wildName):
    url = "https://na.wildstats.gg/en/profile/gameid"

    querystring = {
        "_token": "J8vtJMjQabbwm0Z9EeD6rRmOp3gONweVQPhyOUDg",
        "gameid": f"{wildName}",
    }

    payload = ""
    headers = {
        "cookie": "wild_stats_session=eyJpdiI6IkZsdjdyOXI0MFVzNmZQNW1OLzBkdWc9PSIsInZhbHVlIjoiTmgvVEhZOHJJTCsyTzVwZ3VtdU5XN0F0V1MzTUNsVWJKdWlIWDFFS0RwV1E3QzVkVWx5TmlhTk5Hb0JLMjA1Nzkyc2lZcCsrWTkvN2FxSjJOR0ovTUFhaTZ6Y0MyZ0Y0RFNzWUtBdWR6SDhENFBLck5CekFhVmQzeExTTVdDWisiLCJtYWMiOiIwMTNkMjhmYjM2YmUzYTk4ODZmMmE3NWE5ZjJmMDAzNjUzNGNmMDE1ODhkOTJlMzdjOGViMDNhNWQ2OTU0Yjc4In0%3D",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://na.wildstats.gg/en",
    }

    r = requests.get(url, data=payload, headers=headers, params=querystring)

    soup = BeautifulSoup(r.text, "html.parser")

    data = soup.find("script", type="text/javascript")

    stats = parseBattleStats(data)

    return stats


