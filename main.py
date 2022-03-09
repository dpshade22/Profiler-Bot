from riotGames import LeagueProfile
from helpers import insertSortLists, insertSortChamps
from discord.ext import commands, tasks
from replit import db
import discord
import time
import os

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
  
@bot.command()
async def leagueTop(ctx, *, summName, topX = 3):
    player = LeagueProfile(summName)
    
    await ctx.send(f"Finding top {topX} champions for {summName}... fitered through recent 60 games")
    
    
    champStats = insertSortChamps(player.getPlayerXGamesKDA(gameTypes=[400, 420, 430, 440,], count=60))

    if len(champStats) == 0:
      await ctx.send("Too many requests. Trying again in 60 seconds")
      time.sleep(60)
      champStats = insertSortLists(player.getPlayerXGamesKDA(gameTypes=[400, 420, 430, 440], count=75))
      
    outstring = ""
    
    for i in range(topX):
      if i > len(champStats):
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

@bot.command()
async def leaguePoints(ctx, *, message):    
    name = message
            
    await ctx.send(f"Collecting points for {name}...")
  
    player = LeagueProfile(name)
    playerPoints = round(player.getPoints(), 2)
    
    db[f"{name} leaguePoints"] = playerPoints
    
    outstring = f"{player.riotName} has {playerPoints} in League of Legends"    
    await ctx.send(outstring)

@bot.command()
async def leagueLeaderboard(ctx):
    allLeaguePointsKeys = []
    allLeaguePointsValues = []
    
    for key in db.keys():
      if key[-12:] == "leaguePoints":
        allLeaguePointsKeys.append(key)
        allLeaguePointsValues.append(db[key])
        
    outstring = ""

    sortedKeys, sortedValues = insertSortLists(allLeaguePointsKeys, allLeaguePointsValues)
    
    for i, key in enumerate(sortedKeys):
      firstMark = key.find("leaguePoints")
      name = key[:firstMark]
      
      outstring += f"{i + 1}. {name} with {sortedValues[i]} points\n"
    
    await ctx.send(outstring)

@bot.command()
async def leagueDel(ctx, *, message):
    del db[message.split(' ')[1]]
    
@bot.command()
async def dropDB(ctx):
    for key in db.keys():
      del db[key]
    await ctx.send("Dropping the current database")
    
def parseInput(message):
  wordsList = message.split(' ')
  return wordsList
  




bot.run(os.environ["leagueAPIToken"])