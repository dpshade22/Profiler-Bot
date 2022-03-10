from leagueOfLeg import LeagueProfile
from helpers import insertSortLists, insertSortChamps, parseInput
from discord.ext import commands, tasks
from valorantWebScraping import compKDA, compHS, dmgPerRound, getValPoints
from replit import db
import os

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
  
@bot.command()
async def leagueTop(ctx, summName, topX = 3):
    player = LeagueProfile(summName)
    
    await ctx.send(f"Finding top {topX} champions for {summName}... fitered through recent 60 games")

    champStats = []
  
    try:  
      champStats = insertSortChamps(player.getPlayerXGamesKDA(count=60))
    except (RuntimeError, TypeError, NameError) as err:
      await ctx.send(f"Encountered an error. For those who care, here it is: \"{err}\"")
      
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


@bot.command()
async def val(ctx, statisticToCheck, *, riotName = ""):

  name = riotName.split('#')[0]
  valPointsNames = []
  valPoints = []
  
  for key in db.keys():
      if key[-9:] == "valPoints":
        valPointsNames.append(key)
        valPoints.append(db[key])

  sortedKeys, sortedValues = insertSortLists(valPointsNames, valPoints)
  
  if statisticToCheck.lower() == "currkda" or statisticToCheck.lower() == "kda":
    await ctx.send(f"{name}'s current competitive Valorant KDA is: {compKDA(riotName, False)}")
    return
  elif statisticToCheck.lower() == "allkda":
    await ctx.send(f"{name}'s overall Valorant KDA is: {compKDA(riotName, True)}")
    return
  elif  statisticToCheck.lower() == "currhs%" or statisticToCheck.lower() == "hs%":
    await ctx.send(f"{name}'s current HS% is: {compHS(riotName, False)}")
    return
  elif statisticToCheck.lower() == "allhs%":
    await ctx.send(f"{name}'s overall HS% is: {compHS(riotName, True)}")
    return
  elif statisticToCheck.lower() == "currdmg/r" or statisticToCheck.lower() == "dmg/r":
    await ctx.send(f"{name}'s current DMG/Round is: {dmgPerRound(riotName, False)}")
    return
  elif statisticToCheck.lower() == "alldmg/r":
    await ctx.send(f"{name}'s overall DMG/Round is: {dmgPerRound(riotName, True)}")
    return
  elif statisticToCheck.lower() == "currpoints" or statisticToCheck.lower() == "points":
    points = getValPoints(riotName, False)
    db[f"{name} valPoints"] = points
    await ctx.send(f"{name}'s current points is {points}")
    return
  elif statisticToCheck.lower() == "allpoints":
    await ctx.send(f"{name}'s overall points is {getValPoints(riotName, True)}")
    return
  elif statisticToCheck.lower() == "leaderboard":
    outstring = ""
    
    for i, key in enumerate(sortedKeys):
      firstMark = key.find("valPoints")
      name = key[:firstMark]
      
      outstring += f"{i + 1}. {name} with {sortedValues[i]} points\n"
      
      if i== 9:
        break
        
    await ctx.send(outstring)


bot.run(os.environ["leagueAPIToken"])