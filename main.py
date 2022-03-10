from leagueClasses import LeagueProfile
from helpers import helperFuncs, leagueHelpers, valorantHelpers
from helpers.helperFuncs import insertSortLists, insertSortChamps, parseInput
from helpers.leagueHelpers import recentGames, leagueLeaderboard, leaguePoints
from helpers.valorantHelpers import compKDA, compHS, dmgPerRound, getValPoints
from discord.ext import commands, tasks
import requests
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
  _**Valorant**_   `!val [stat] [IGN#tag]`
  _stats with the \"all\" before them show all competitive seasons together, while without it is current season's competitive games_
  **valid stats**: _kda, allKDA, hs%, allhs%, dmg/r, allDmg/r, points, leaderboard_

_**League of Legends**_   `!league [stat] [IGN]`
  **valid stats**: _topChamps, points, leaderboard_
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
      await ctx.send(f"**{name}'s** current competitive KDA is: _{compKDA(riotName, False)}_")
      return
    elif statisticToCheck.lower() == "allkda":
      await ctx.send(f"**{name}'s** overall competitive KDA is: _{compKDA(riotName, True)}_")
      return
    elif  statisticToCheck.lower() == "currhs%" or statisticToCheck.lower() == "hs%":
      await ctx.send(f"**{name}'s** current HS% is: _{compHS(riotName, False)}_")
      return
    elif statisticToCheck.lower() == "allhs%":
      await ctx.send(f"**{name}'s** overall HS% is: _{compHS(riotName, True)}_")
      return
    elif statisticToCheck.lower() == "currdmg/r" or statisticToCheck.lower() == "dmg/r":
      await ctx.send(f"**{name}'s** current DMG/Round is: _{dmgPerRound(riotName, False)}_")
      return
    elif statisticToCheck.lower() == "alldmg/r":
      await ctx.send(f"**{name}'s** overall DMG/Round is: _{dmgPerRound(riotName, True)}_")
      return
    elif statisticToCheck.lower() == "currpoints" or statisticToCheck.lower() == "points":
      points = getValPoints(riotName, False)
      db[f"{name} valPoints"] = points
      await ctx.send(f"**{name}'s** current points is _{points}_")
      return
    elif statisticToCheck.lower() == "allpoints":
      await ctx.send(f"**{name}'s** overall points is _{getValPoints(riotName, True)}_")
      return
    elif statisticToCheck.lower() == "leaderboard":
      outstring = "_**Valorant Points Leaderboard**_\n----------------------------------------\n"
      
      for i, key in enumerate(sortedKeys):
        firstMark = key.find("valPoints")
        name = key[:firstMark]
        
        outstring += f"{i + 1}. **{name}**with _{sortedValues[i]}Vp_ \n"
        
        if i == 9:
          break
          
      await ctx.send(outstring)
    else:
      await ctx.send("Valorant stat not found.")
      
  except (RuntimeError, TypeError, NameError, IndexError, discord.ClientException, requests.exceptions.HTTPError) as err:
    if type(err) == IndexError:
      await ctx.send(f"Tag wasn't included in Valorant name \"_{name}_\"")
    elif type(err) == requests.exceptions.HTTPError:
      await ctx.send(f"Can't find the player. Double check your player name and tag. If those are correct, try loging into tracker.gg with that name and try again.")
    else:
      await ctx.send(f"There was an error. For those who care, the error was: {err}")

bot.run(os.environ["profilerBotToken"])