from leagueClasses import LeagueProfile
from helpers import insertSortLists, insertSortChamps, parseInput
from leagueHelpers import recentGames, leagueLeaderboard, leaguePoints
from discord.ext import commands, tasks
from valorantHelpers import compKDA, compHS, dmgPerRound, getValPoints
import discord
from replit import db
import os

bot = commands.Bot(command_prefix='!', help_command=None)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def help(ctx):
  outstring = f""" 
  _**Valorant**_   _!val [stat] [IGN#tag]_
  _stats with the \"all\" before them show all competitive seasons together, while without it is current season's competitive games_
  `kda, allKDA, hs%, allhs%, dmg/r, allDmg/r, points, leaderboard`

_**League of Legends**_   _!league [stat] [IGN]_
  `topChamps, points, leaderboard`
  """  
  await ctx.send(outstring)


@bot.command()
async def league(ctx, statisticToCheck, riotName = "", count = 3):
  try:
    if statisticToCheck.lower() == "topchamps":
      await recentGames(ctx, riotName, count, False)
    elif statisticToCheck.lower() == "recent":
      await recentGames(ctx, riotName, count, True)
    elif statisticToCheck.lower() == "leaderboard":
      await leagueLeaderboard(ctx)
    elif statisticToCheck.lower() == "points":
      await leaguePoints(ctx, riotName)
      
  except (RuntimeError, TypeError, NameError) as err:
      await ctx.send(f"Encountered an error. For those who care, here it is: \"{err}\"")
   

    
@bot.command()
async def dropDB(ctx):
  if str(ctx.author) != "dpshade22#0196":
    await ctx.send(f"Nice try pal. Database is still in tact.")
    return

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
  
  try: 
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
  except (RuntimeError, TypeError, NameError, IndexError) as err:
    if type(err) == IndexError:
      await ctx.send(f"Tag wasn't included in Valorant name")
    else:
      await ctx.send(f"There was an error. For those who care, the error was: {err}")

bot.run(os.environ["profilerBotToken"])