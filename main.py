from discord.ext import commands, tasks
import pymongo
import requests
import discord
import time
import os

from leagueClasses import LeagueProfile
from helpers import helperFuncs, leagueHelpers, valorantHelpers
from helpers.helperFuncs import insertSortLists, insertSortChamps, parseInput, headsOrTails
from helpers.leagueHelpers import recentGames, leagueLeaderboard, getLeaguePoints
from helpers.valorantHelpers import compKDA, compHS, dmgPerRound, getValPoints, playerValorantProfile

mongoPass = os.environ['mongoPass']

client = pymongo.MongoClient(f"mongodb+srv://dpshade22:{mongoPass}@cluster0.z1jes.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
mongoDb = client.profileDB
intents = discord.Intents(messages=True, guilds=True, members=True)

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)


@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}')

@bot.command()
async def help(ctx):
  outstring = f""" 
  _**LIST OF COMMANDS**_
  
  _**Create Player Profile**_   `!newProfile [discord#tag] [valorantName#tag] [leagueName] [cod]`
  _**Update Player Profile**_   `!updateProfile [discord#tag] [valorantName#tag] [leagueName] [cod]` 
  > *If you need to change only one of these, still fill in each field (use old names)*
  > *Update also recalculates all of your stats*

 _**Update Statistics**_   `!update` _get most up to date statistics for all players_
  
  > _**Valorant**_   `!val [stat] [discord#tag]` standard format
  > _stats with the \"all\" before them show all competitive seasons together, while without it is current season's competitive games_
  > **valid stats**: _kda, allKDA, hs%, allhs%, dmg/r, allDmg/r, points
  >
  > _Other `!val` commands_
  >  `!val leaderboard` 
  >      _shows Valorant leaderboard for members in this server [specific stat to sort by: **points**, **kda**, **hs**, **dmg/round**]_
  >  `!val globalLeaderboard` 
  >      _shows Valorant leaderboard for all players in the database [can also specify stat]_
  >  `!val [discord#tag]` 
  >      _shows Valorant profile of the user given_
  
_**League of Legends**_   `!league [stat] [discord#tag]`
  **valid stats**: _topChamps, points, leaderboard_

  _**Coin Flip**_ `!coin`

  """
  await ctx.send(outstring)

@bot.command()
async def profile(ctx, discordName):
  profiles = mongoDb.profiles
  foundProfile = profiles.find_one({"DiscordName": discordName})
  
  if foundProfile == None:
    await ctx.send("Profile not found, try using the `!newProfile` command")
    return
  
  outstring = f"""
  _{discordName}'s Profile:_
-----------------------------------------------
  _Valorant Name_: ***{foundProfile['ValorantName']}***
  _League of Legends Name_: ***{foundProfile['LoLName']}***
  _Call of Duty Name_: ***{foundProfile['CoDName']}***
  """
  await ctx.send(outstring)
  
@bot.command()
async def newProfile(ctx, discordName, valName = "", LoLName = "", CoDName = ""):
  collection = mongoDb.profiles
  valorantStats = mongoDb.valorantStats
  leagueStats = mongoDb.leagueStats
  
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
    valorantStats.insert_one({"ValorantName": valName, "points": points, "currKda": currKda, "allKda": allKda, "currHS": currHS, "allHS": allHS,"currDmg/Round": currDmg, "allDmg/Round": allDmg})
  
  if leagueStats.find_one({"LoLName": LoLName}) == None and LoLName != "":
    points = getLeaguePoints(LoLName)
  
  print(collection.find_one({"DiscordName": "dpshade22#0196"}))

  await ctx.send(f"Successfully added **{discordName}** to the database")

@bot.command()
async def update(ctx):
  profiles = mongoDb.profiles
  valorantStats = mongoDb.valorantStats
  allProfiles = profiles.find({})
  
  await ctx.send(f"Updating **all** player statistics... this can take a while...")
  
  for i, profile in enumerate(allProfiles):
    print(profile)

    player = valorantStats.find_one({"ValorantName": profile['ValorantName']})
    valName = player['ValorantName']
    
    points = getValPoints(valName, False)
    currKda = compKDA(valName, False)
    allKda = compKDA(valName, True)
    currHS = compHS(valName, False)
    allHS = compHS(valName, True)
    currDmg = dmgPerRound(valName, False)
    allDmg = dmgPerRound(valName, True)
    valorantStats.update_one(player, {"$set": {"ValorantName": valName, "points": points, "currKda": currKda, "allKda": allKda, "currHS": currHS, "allHS": allHS,"currDmg/Round": currDmg, "allDmg/Round": allDmg}})
  
    rate = (i + 1)
  
    if rate % 3 == 0:
      print("Sleeping")
      time.sleep(31)
      print("Resuming")
    
  await ctx.send(f"Successfully updated **all** player statistics in the database")


@bot.command()
async def updateProfile(ctx, discordName = "", newVal = "", newLol = "", newCod = ""):
  profiles = mongoDb.profiles
  valorantStats = mongoDb.valorantStats
  leagueStats = mongoDb.leagueStats
  
  profile = profiles.find_one({"DiscordName": discordName})
  valName = profile['ValorantName']
  lolName = profile['LoLName']
  
  valQuery = valorantStats.find_one({"ValorantName": valName})
  leagueQuery = leagueStats.find_one({"LoLName": lolName})
  
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
  
  valName = valQuery['ValorantName']
  
  valPoints = getValPoints(valName, False)
  currValKda = compKDA(valName, False)
  allValKda = compKDA(valName, True)
  currValHS = compHS(valName, False)
  allValHS = compHS(valName, True)
  currValDmg = dmgPerRound(valName, False)
  allValDmg = dmgPerRound(valName, True)
  valorantStats.update_one(valQuery, {"$set": {"ValorantName": newVal, "points": valPoints, "currKda": currValKda, "allKda": allValKda, "currHS": currValHS, "allHS": allValHS,"currDmg": currValDmg, "allDmg": allValDmg}})
 
  leaguePoints = getLeaguePoints(newLol)
  leagueStats.updates_one(leagueQuery, {"$set": {"LoLName": newLol, "points": leaguePoints}})
  
  await ctx.send(f"Successfully updated _**all**_ of **{discordName}'s** statistics in the database")


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
      await ctx.send(f"Collecting points for {riotName}...")
      
      await f"**{riotName}** current LoL points is _{playerPoints}_" 
      
  except (RuntimeError, TypeError, NameError) as err:
      await ctx.send(f"Encountered an error. For those who care, here it is: _\"{err}\"_")
   



@bot.command()
async def val(ctx, statisticToCheck, discordName = ""):

  profiles = mongoDb.profiles
  valorantStats = mongoDb.valorantStats
  
  if "#" in discordName:
    currProfile = profiles.find_one({"DiscordName": discordName})
    valName = currProfile['ValorantName']
    
    valQuery = valorantStats.find_one({"ValorantName": valName})
    
  elif "#" in statisticToCheck and "#" not in discordName:
    discordName, statisticToCheck = statisticToCheck, discordName
    currProfile = profiles.find_one({"DiscordName": discordName})
    
    valName = currProfile['ValorantName']
    
    valQuery = valorantStats.find_one({"ValorantName": valName})

  statisticToCheck = statisticToCheck.lower()
  
  try: 
    if statisticToCheck == "currkda" or statisticToCheck.lower() == "kda":
      await ctx.send(f"**{valName}'s** current competitive KDA is: _{valQuery['currKda']}_")
      return
    elif statisticToCheck == "allkda":
      await ctx.send(f"**{valName}'s** overall competitive KDA is: _{valQuery['allKda']}_")
      return
    elif  statisticToCheck == "currhs%" or statisticToCheck.lower() == "hs%":
      await ctx.send(f"**{valName}'s** current HS% is: _{valQuery['currHS']}_")
      return
    elif statisticToCheck == "allhs%":
      await ctx.send(f"**{valName}'s** overall HS% is: _{valQuery['allHS']}_")
      return
    elif statisticToCheck == "currdmg/r" or statisticToCheck.lower() == "dmg/r":
      await ctx.send(f"**{valName}'s** current DMG/Round is: _{valQuery['currDmg']}_")
      return
    elif statisticToCheck == "alldmg/r":
      await ctx.send(f"**{valName}'s** overall DMG/Round is: _{valQuery['allDmg']}_")
      return
    elif statisticToCheck == "currpoints" or statisticToCheck.lower() == "points":
      await ctx.send(f"**{valName}'s** current Valorant points is _{valQuery['points']}_")
      return
    elif statisticToCheck == "":
      outstring = playerValorantProfile(valName, valQuery)
      await ctx.send(outstring)
    
    elif statisticToCheck == "leaderboard" or statisticToCheck == "globalleaderboard":
      members = await serverMembers(ctx)
      
      stat = "points"
      
      if discordName.lower() == "hs":
        stat = "currHS"
      elif discordName.lower() == "kda":
        stat = "currKda"
      elif discordName.lower() == "dmg/round":
        stat = "currDmg/Round"
      else:
        discordName = stat
        
      outstring = f"_**Valorant {discordName.upper()} Leaderboard**_\n----------------------------------------\n"

      leaderboard = valorantStats.find({}).sort(stat, -1)
      
      currentServerLeaderboard = []

      if statisticToCheck == "leaderboard":
        for player in leaderboard:
          playerProfile = profiles.find_one({"ValorantName": player["ValorantName"]})
          if playerProfile["DiscordName"] not in members:
            continue
          currentServerLeaderboard.append(player)
      else:
        currentServerLeaderboard = leaderboard
      
      for i, valPlayer in enumerate(currentServerLeaderboard):
        
        valName = valPlayer['ValorantName']
        outstring += f"{i + 1}. **{valName}** with _{valPlayer[stat]}_ \n"
        
        if i == 9:
          break
          
      await ctx.send(outstring)
    else:
      await ctx.send("Valorant statistic not found")
      
  except (RuntimeError, TypeError, NameError, IndexError, discord.ClientException, requests.exceptions.HTTPError) as err:
    if type(err) == IndexError:
      await ctx.send(f"Tag wasn't included in Valorant name \"_{name}_\"")
    elif type(err) == requests.exceptions.HTTPError:
      await ctx.send(f"Can't find the player. Double check your player name and tag. If those are correct, try loging into tracker.gg with that name and try again.")
    else:
      await ctx.send(f"There was an error. For those who care, the error was: _\"{err}\"_")

async def serverMembers(ctx):
  members = []
  for member in ctx.guild.members:
    members.append(str(member.name) + "#" + str(member.discriminator))

  return members
bot.run(os.environ["profilerBotToken"])