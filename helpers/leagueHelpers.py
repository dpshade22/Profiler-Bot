from leagueClasses import LeagueProfile
from helpers.helperFuncs import insertSortChamps, insertSortLists
from replit import db
import pymongo
import os
mongoPass = os.environ['mongoPass']

client = pymongo.MongoClient(f"mongodb+srv://dpshade22:{mongoPass}@cluster0.z1jes.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
mongoDb = client.profileDB

async def recentGames(ctx, riotName, count, recent):
  player = LeagueProfile(riotName)
  champStats = []
  if recent:
    await ctx.send(f"Finding past {count} games for {riotName}...")
    champStats = insertSortChamps(player.getPlayerXGamesKDA(count=count))

  else:
    await ctx.send(f"Finding top {count} champions for {riotName}... fitered through recent 60 games")
    champStats = insertSortChamps(player.getPlayerXGamesKDA(count=60))
  
  outstring = ""
  
  for i in range(0, count):
    if i >= len(champStats):
        break
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

async def leagueLeaderboard(ctx, discordName):
    leagueStats = mongoDb.leagueStats

    outstring = "_**Valorant Points Leaderboard**_\n----------------------------------------\n"
    stat = "points"
    if discordName != "": 
      stat = discordName
      pointsLeaderboard = leagueStats.find().sort(stat, -1)
    else:
      pointsLeaderboard = leagueStats.find().sort(stat, -1)
      
    for i, valPlayer in enumerate(pointsLeaderboard):
      valName = valPlayer['ValorantName']
      
      outstring += f"{i + 1}. **{valName}** with _{valPlayer[stat]}_ \n"
      
      if i == 9:
        break
        
    await ctx.send(outstring)

async def leaguePoints(ctx, riotName):    
    name = riotName
            
    await ctx.send(f"Collecting points for {name}...")
  
    player = LeagueProfile(name)
    playerPoints = round(player.getPoints(), 2)
    
    db[f"{name} leaguePoints"] = playerPoints
    
    outstring = f"**{player.riotName}** current LoL points is _{playerPoints}_"    
    await ctx.send(outstring)