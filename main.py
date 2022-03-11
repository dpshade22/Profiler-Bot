from discord.ext import commands, tasks
import pymongo
import requests
import discord
import os

from leagueClasses import LeagueProfile
from helpers import helperFuncs, leagueHelpers, valorantHelpers
from helpers.helperFuncs import insertSortLists, insertSortChamps, parseInput, headsOrTails
from helpers.leagueHelpers import recentGames, leagueLeaderboard, leaguePoints
from helpers.valorantHelpers import compKDA, compHS, dmgPerRound, getValPoints

mongoPass = os.environ['mongoPass']

client = pymongo.MongoClient(f"mongodb+srv://dpshade22:{mongoPass}@cluster0.z1jes.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
mongoDb = client.profileDB

bot = commands.Bot(command_prefix='!', help_command=None)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def help(ctx):
  outstring = f""" 
  _**Coin Flip**_ `!coin`

  _**Create Player Profile**_   `!newProfile [discord#tag] [valorantName#tag] [leagueName] [cod]`
  _**Update Player Profile**_   `!updateProfile [discord#tag] [valorantName#tag] [leagueName] [cod]` 
  *If you need to change only one of these, still fill in each field (use old names)*
  *Update also recalculates all of your stats*
  
  _**Valorant**_   `!val [stat] [discord#tag]`
  _stats with the \"all\" before them show all competitive seasons together, while without it is current season's competitive games_
  **valid stats**: _kda, allKDA, hs%, allhs%, dmg/r, allDmg/r, points, leaderboard [specific stat to sort by: **points**, **currKda**, **currHS**, **currDmg**] **curr** can be swapped with **all**_

_**League of Legends**_   `!league [stat] [discord#tag]`
  **valid stats**: _topChamps, points, leaderboard_
  """  
  await ctx.send(outstring)

@bot.command()
async def newProfile(ctx, discordName, valName = "", LoLName = "", CoDName = ""):
  collection = mongoDb.profiles
  valorantStats = mongoDb.valorantStats

  if collection.find_one({"DiscordName": discordName}) != None:
    await ctx.send(f"{discordName} already exists. Use `!updateProfile` with your new IGNs")
    return
  
  print(collection.profiles)
  collection.insert_one({
    "DiscordName": discordName,
    "ValorantName": valName,
    "LoLName": LoLName,
    "CoDName": CoDName
  })
  
  if valorantStats.find_one({"ValorantName": valName}) == None and valName != "":
    points = getValPoints(valName, False)
    currKda = compKDA(valName, False)
    allKda = compKDA(valName, True)
    currHS = compHS(valName, False)
    allHS = compHS(valName, True)
    currDmg = dmgPerRound(valName, False)
    allDmg = dmgPerRound(valName, True)
    valorantStats.insert_one({"ValorantName": valName, "points": points, "currKda": currKda, "allKda": allKda, "currHS": currHS, "allHS": allHS,"currDmg": currDmg, "allDmg": allDmg})
  
  print(collection.find_one({"DiscordName": "dpshade22#0196"}))

  await ctx.send(f"Successfully added **{discordName}** to the database")

@bot.command()
async def updateAll(ctx):
  valorantStats = mongoDb.valorantStats
  valQuery = valorantStats.find({})
  
  for player in valQuery:
    valName = player['ValorantName']
    
    points = getValPoints(valName, False)
    currKda = compKDA(valName, False)
    allKda = compKDA(valName, True)
    currHS = compHS(valName, False)
    allHS = compHS(valName, True)
    currDmg = dmgPerRound(valName, False)
    allDmg = dmgPerRound(valName, True)
    valorantStats.update_one(player, {"$set": {"ValorantName": valName, "points": points, "currKda": currKda, "allKda": allKda, "currHS": currHS, "allHS": allHS,"currDmg": currDmg, "allDmg": allDmg}})

  await ctx.send(f"Successfully updated **all** player statistics in the database")


@bot.command()
async def updateProfile(ctx, discordName = "", newVal = "", newLol = "", newCod = ""):
  profiles = mongoDb.profiles
  valorantStats = mongoDb.valorantStats
  profile = profiles.find_one({"DiscordName": discordName})
  valName = profile['ValorantName']
  valQuery = valorantStats.find_one({"ValorantName": valName})
  
  if newVal != "" and newLol != "" and newCod != "":
    profiles.update_one(profile, {"$set": {"ValorantName": newVal, "LoLName": newLol, "CoDName": newCod}})
  elif newVal != "" and newLol != "":
    profiles.update_one(profile, {"$set": {"ValorantName": newVal, "LoLName": newLol}})
  elif newVal != "" and newCod != "":
    profiles.update_one(profile, {"$set": {"ValorantName": newVal, "CoDName": newCod}})
  elif newCod != "" and newLol != "":
    profiles.update_one(profile, {"$set": {"LoLName": newLol, "CoDName": newCod}})
  elif newVal != "":
    profiles.update_one(profile, {"$set": {"ValorantName": newVal}})
  elif newLol != "":
    profiles.update_one(profile, {"$set": {"LoLName": newLol}})
  elif newCod != "":
    profiles.update_one(profile, {"$set": {"CoDName": newCod}})
    
  if  valName != None:
    points = getValPoints(valName, False)
    currKda = compKDA(valName, False)
    allKda = compKDA(valName, True)
    currHS = compHS(valName, False)
    allHS = compHS(valName, True)
    currDmg = dmgPerRound(valName, False)
    allDmg = dmgPerRound(valName, True)
    valorantStats.update_one(valQuery, {"$set": {"ValorantName": valName, "points": points, "currKda": currKda, "allKda": allKda, "currHS": currHS, "allHS": allHS,"currDmg": currDmg, "allDmg": allDmg}})
  
  await ctx.send(f"Successfully updated **{discordName}** in the database")


@bot.command()
async def coin(ctx):
  result = await headsOrTails()
  await ctx.send(f"**{result}**")

@bot.command()
async def league(ctx, statisticToCheck, discordName = "", count = 3):
  profiles = mongoDb.profiles
  profile = profiles.find_one({"DiscordName": discordName})
  riotName = profile['LoLName']
  
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
      await ctx.send(f"Encountered an error. For those who care, here it is: _\"{err}\"_")
   



@bot.command()
async def val(ctx, statisticToCheck, discordName = ""):

  profiles = mongoDb.profiles
  valorantStats = mongoDb.valorantStats

  if "#" in discordName:
    currProfile = profiles.find_one({"DiscordName": discordName})
    valName = currProfile['ValorantName']
    name = valName.split('#')[0]
    
    valQuery = valorantStats.find_one({"ValorantName": valName})
    
  try: 
    if statisticToCheck.lower() == "currkda" or statisticToCheck.lower() == "kda":
      await ctx.send(f"**{valName}'s** current competitive KDA is: _{valQuery['currKda']}_")
      return
    elif statisticToCheck.lower() == "allkda":
      await ctx.send(f"**{valName}'s** overall competitive KDA is: _{valQuery['allKda']}_")
      return
    elif  statisticToCheck.lower() == "currhs%" or statisticToCheck.lower() == "hs%":
      await ctx.send(f"**{valName}'s** current HS% is: _{valQuery['currHS']}_")
      return
    elif statisticToCheck.lower() == "allhs%":
      await ctx.send(f"**{valName}'s** overall HS% is: _{valQuery['allHS']}_")
      return
    elif statisticToCheck.lower() == "currdmg/r" or statisticToCheck.lower() == "dmg/r":
      await ctx.send(f"**{valName}'s** current DMG/Round is: _{valQuery['currDmg']}_")
      return
    elif statisticToCheck.lower() == "alldmg/r":
      await ctx.send(f"**{valName}'s** overall DMG/Round is: _{valQuery['allDmg']}_")
      return
    elif statisticToCheck.lower() == "currpoints" or statisticToCheck.lower() == "points":
      
      await ctx.send(f"**{valName}'s** current points is _{valQuery['points']}_")
      return
      
    elif statisticToCheck.lower() == "leaderboard":
      outstring = "_**Valorant Points Leaderboard**_\n----------------------------------------\n"
      stat = "points"
      if discordName != "": 
        stat = discordName
        pointsLeaderboard = valorantStats.find().sort(stat, -1)
      else:
        pointsLeaderboard = valorantStats.find().sort(stat, -1)
        
      for i, valPlayer in enumerate(pointsLeaderboard):
        valName = valPlayer['ValorantName']
        
        outstring += f"{i + 1}. **{valName}** with _{valPlayer[stat]}_ \n"
        
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
      await ctx.send(f"There was an error. For those who care, the error was: _\"{err}\"_")


bot.run(os.environ["profilerBotToken"])