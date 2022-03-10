from leagueClasses import LeagueProfile
from helpers import insertSortChamps, insertSortLists
from replit import db

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

async def leaguePoints(ctx, riotName):    
    name = riotName
            
    await ctx.send(f"Collecting points for {name}...")
  
    player = LeagueProfile(name)
    playerPoints = round(player.getPoints(), 2)
    
    db[f"{name} leaguePoints"] = playerPoints
    
    outstring = f"{player.riotName} has {playerPoints} in League of Legends"    
    await ctx.send(outstring)