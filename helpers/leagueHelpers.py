from leagueClasses import LeagueProfile
from helpers.helperFuncs import insertSortChamps, insertSortLists, serverMembers
import datetime
import pymongo
import os
mongoPass = os.environ['mongoPass']

client = pymongo.MongoClient(f"mongodb+srv://dpshade22:{mongoPass}@cluster0.z1jes.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
mongoDb = client.profileDB
leagueStats = mongoDb.leagueStats
profiles = mongoDb.profiles

async def recentGames(ctx, riotName, count, recent):
  player = LeagueProfile(riotName)
  leagueStats = mongoDb.leagueStats
  
  champStats = []

  if recent:
    await ctx.send(f"Finding past {count} games for {riotName}...")
    champStats = insertSortChamps(player.getPlayerXGamesKDA(count=count))

  else:
    await ctx.send(f"Finding top {count} champions for {riotName}... fitered through recent 60 games")
    champStats = insertSortChamps(player.getPlayerXGamesKDA(count=60))
  
  outstring = ""
  
  for i in range(0, count):
    leagueQuery = leagueStats.find_one({"LoLName": riotName})

    if i >= len(champStats):
        break

    # if i < 4:
    #   if leagueQuery['TopChamps'] == None:
    #   else:
        
    if len(outstring) < 1599:
      outstring += f"""{champStats[i].name} has {champStats[i].points} points
                      Games: {champStats[i].games}
                      Winrate: {champStats[i].winRate}
                      KDA: {champStats[i].avgKDA} ({champStats[i].totalKills}, {champStats[i].totalDeaths}, {champStats[i].totalAssists})
                      Average Percent (from team) DMG to Champs: {champStats[i].avgTDP}\n\n"""
    else:
      await ctx.send(outstring)
      outstring = f"""{champStats[i].name} has {champStats[i].points} points
                      Games: {champStats[i].games}
                      Winrate: {champStats[i].winRate}
                      KDA: {champStats[i].avgKDA} ({champStats[i].totalKills}, {champStats[i].totalDeaths}, {champStats[i].totalAssists})
                      Average Percent (from team) DMG to Champs: {champStats[i].avgTDP}\n\n"""
  await ctx.send(outstring)

async def leagueLeaderboard(ctx, statisticToCheck):
  leagueStats = mongoDb.leagueStats
  profiles = mongoDb.profiles
  members = await serverMembers(ctx)
    
  stat = "points"
  
    
  outstring = f"_**League of Legends POINTS Leaderboard**_\n----------------------------------------\n"

  leaderboard = leagueStats.find({}).sort(stat, -1)
  
  currentServerLeaderboard = []

  if statisticToCheck == "leaderboard":
    for player in leaderboard:
      playerProfile = profiles.find_one({"LoLName": player["LoLName"]})
      if playerProfile["DiscordName"] not in members:
        continue
      currentServerLeaderboard.append(player)
  else:
    currentServerLeaderboard = leaderboard
  
  for i, lolPlayer in enumerate(currentServerLeaderboard):
    
    lolName = lolPlayer['LoLName']
    outstring += f"{i + 1}. **{lolName}** with _{lolPlayer[stat]}_ \n"
    
    if i == 9:
      break
      
  await ctx.send(outstring)

def getLeaguePoints(riotName):
  name = riotName
  leagueQuery = leagueStats.find_one({"LoLName": riotName})
  profile = profiles.find_one({"LoLName": riotName})

  
  player = LeagueProfile(name)
  playerPoints = round(player.getPoints(), 2)

  if leagueQuery == None:
    leagueStats.insert_one({"LoLName": f"{riotName}", "points": playerPoints})
    profiles.update_one(profile, {"$set": {"LastUpdate": datetime.datetime.now()}})
  else:
    leagueStats.update_one(leagueQuery, {"$set": {"points": playerPoints}})
    profiles.update_one(profile, {"$set": {"LastUpdate": datetime.datetime.now()}})
  return playerPoints

