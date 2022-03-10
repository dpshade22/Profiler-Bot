import os
import math
import time
import requests

header = {
  "X-Riot-Token": os.environ['riotAPIheader']
}

class Champion:
  def __init__(self, name):
    self.name = name

    self.games = 0
    self.numWins = 0
    self.winRate = 0

    self.kdar = []
    self.kda = []
    self.teamDmgPercent = []
    
    self.avgKDA = 0
    self.avgTDP = 0

    self.totalKills = 0
    self.totalDeaths = 0
    self.totalAssists = 0

    self.points = 0



  def PrintAll(self):
    self.calcTotals()
    print(f"{self.name}\n")
    
    print(f"""
          POINTS: {self.points}

          Number of Games: {self.games}
          Win Rate: {self.winRate}
          KDARs: {self.kdar}
          KDAs: {self.kda}
          TDPs: {self.teamDmgPercent}
          """)

    print(f"""
          Total Kills: {self.totalKills}
          Total Deaths: {self.totalDeaths}
          Total Assists: {self.totalAssists}
          KDAR Avg: {self.avgKDA}
          TDP Avg: {self.avgTDP}
          """)
    print("\n")

  def calcTotals(self):
    self.totalKills = sum([kill[0] for kill in self.kda])
    self.totalDeaths = sum([death[1] for death in self.kda])
    self.totalAssists = sum([assist[2] for assist in self.kda])
    self.avgKDA = round((self.totalKills + self.totalAssists)/ self.totalDeaths, 4)
    self.avgTDP = round(sum(self.teamDmgPercent) / len(self.teamDmgPercent), 4)
    self.winRate = round((self.numWins / self.games), 2)
    self.points = round(self.calcPoints(), 2)


  def calcPoints(self):          
    c = 0.4 * (math.log(self.games) + 1)
    points = 0.5 * (c * 4 * self.avgKDA) + 0.5 * (c * self.winRate + c * self.avgTDP)
    return points


class LeagueProfile:
    def __init__(self, riotName):
      self.riotName = riotName
      self.championsObjList = []

    def getSummoner(self):
      request = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{self.riotName}', headers=header)
      # request.raise_for_status()
      
      return request.json()
    
        
    def getSummonerByPUUID(self, puuid):
        request = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}', headers=header)
        # request.raise_for_status()

      
        return request.json()

    def getSummonersRecentMatchesID(self, count):
        summ = self.getSummoner()
        puuid = summ['puuid']
        request = requests.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}', headers=header)
        # request.raise_for_status()
      
        return request.json()

    def getMatchByID(self, id):
        request = requests.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/{id}', headers=header)
        # request.raise_for_status()
        return request.json()

    def getPlayerXGamesKDA(self, count = 75):
        puuid = self.getSummoner()['puuid']
        matchIDs = self.getSummonersRecentMatchesID(count)
      
        kills, deaths, assists = 0, 0, 0

        for match in matchIDs:
            tempMatch = self.getMatchByID(match)
            participants = tempMatch.get('info')['participants']

            if tempMatch.get("info")["queueId"] not in [400, 420, 430, 440]:
              continue
              
            i = 0
            while participants[i]['puuid'] != puuid:
                i += 1
              
            teamId = participants[i]['teamId']
          
            totalTeamDmg = 0.1
            
            for j in range(len(participants)):
              if participants[j]['teamId'] == teamId:
                totalTeamDmg += participants[j]['totalDamageDealtToChampions']


            inGameTeamDmg = participants[i]['totalDamageDealtToChampions']
            inGameKills = participants[i]['kills']
            inGameDeaths = participants[i]['deaths']
            inGameAssists = participants[i]['assists']

              
          
            if inGameDeaths == 0:
              inGameDeaths = 1
          
            championName = participants[i]['championName']
            tempChamp = Champion(championName)
          
            kills += inGameKills
            deaths += inGameDeaths
            assists += inGameAssists
          
            if tempChamp.name not in [champ.name for champ in self.championsObjList]:
                self.championsObjList.append(tempChamp)
                tempChamp.games += 1
                tempChamp.kdar.append(round((inGameKills + inGameAssists) / inGameDeaths, 4))
                tempChamp.kda.append([inGameKills, inGameDeaths, inGameAssists])
                tempChamp.teamDmgPercent.append(round(inGameTeamDmg / totalTeamDmg, 4))

                if participants[i]['win'] == True:
                  tempChamp.numWins += 1

                tempChamp.calcTotals()
                
            else:
                ndx = [champ.name for champ in self.championsObjList].index(championName)
                returningChamp = self.championsObjList[ndx]
                returningChamp.games += 1
                returningChamp.kdar.append(round((inGameKills + inGameAssists) / inGameDeaths, 4))
                returningChamp.kda.append([inGameKills, inGameDeaths, inGameAssists])
                returningChamp.teamDmgPercent.append(round(inGameTeamDmg / totalTeamDmg, 4))

                if participants[i]['win'] == True:
                  returningChamp.numWins += 1

                returningChamp.calcTotals()
      
        return self.championsObjList

    def getPoints(self):
      self.getPlayerXGamesKDA(count = 10)
      points = 0
        
      for champ in self.championsObjList:
        points += champ.points

      return points