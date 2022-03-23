from discord.ext import commands, tasks
import datetime
import pymongo
import requests
import discord
import time
import os

from helpers.db import insertObjIntoMongo, updateMongoQueryWObj, deleteQueryInCollection
from games import leagueStats, valorantStats
from helpers.helpfulFunctions import insertSortLists, insertSortChamps, parseInput, headsOrTails, readyForMoreRequests
from games.leagueStats import recentGames, leagueLeaderboard, getLeaguePoints
from games.valorantStats import getValStats, playerValorantProfile
from games.wildStats import getWildStats

mongoPass = os.environ['_mongoPass']

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
  
  _**Create Player Profile**_   `!newProfile [discord#tag] [valorantName#tag] [leagueName]`
  _**Update Player Profile**_   `!update [discord#tag] [valorantName#tag] [leagueName]` 
  > *If you need to change only one of these, still fill in each field (use old names)*
  > *Update also recalculates all of your stats*

 _**Update Statistics**_   `!update` _get the most up to date statistics for all players in your server_
  
  _**Valorant**_   `!val [stat] [discord#tag]` standard format. Must connect to https://dak.gg/valorant/ with your Riot Acc.
  
  **valid stats**: _kda, hs%, dmg/r, fbr, points_ 
  fbr = first blood rate
  
  > **Other `!val` commands**
  >  `!val leaderboard [stat]` 
  >      _shows Valorant leaderboard for members in this server [specific stat to sort by: **points**, **kda**, **hs%**, **dmg/round**]_
  >  `!val globalLeaderboard [stat]` 
  >      _shows Valorant leaderboard for all players in the database [can also specify stat]_
  >  `!val [discord#tag]` 
  >      _shows Valorant profile of the user given_
  
  _**League of Legends**_   `!league [stat] [discord#tag]`
  **valid stats**: points_

  _**Coin Flip**_ `!coin`
-------------------------------------------------------------------------------
  
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
async def newProfile(ctx, discordName, valName = "", LoLName = "", CoDNameName = ""):
  collection = mongoDb.profiles
  valorantStats = mongoDb.valorantStats
  leagueStats = mongoDb.leagueStats
  
  if collection.find_one({"DiscordName": discordName}) != None:
    await ctx.send(f"{discordName} already exists. Use `!updateProfile` with your new IGNs")
    return
  
  print(collection.profiles)

  insertObjIntoMongo(collection, {
    "LastUpdate": datetime.datetime.now(),
    "DiscordName": discordName,
    "ValorantName": valName,
    "LoLName": LoLName,
  })

  
  
  if valorantStats.find_one({"ValorantName": valName}) == None and valName != "":

    currentValStats = getValStats(valName, False)
    overallValStats = getValStats(valName, True)
        
    insertObjIntoMongo(valorantStats, 
                      {"ValorantName": valName, "points": currentValStats["POINTS"], "currKDA": currentValStats["KDA"], 
                       "currHS": currentValStats["HS"], "currDmg/Round": currentValStats["DMGR"], "allKDA": overallValStats["KDA"], 
                       "allHS": overallValStats["HS"], "allDmg/Round": overallValStats["DMGR"], "currFBR": currentValStats["FBR"], 
                       "allFBR": overallValStats["FBR"]})
  
  if leagueStats.find_one({"LoLName": LoLName}) == None and LoLName != "":
    points = getLeaguePoints(LoLName)
  
  await ctx.send(f"_Successfully added **{discordName}** to the database_")

@bot.command()
async def update(ctx, discordName = "", newVal = "", newLol = "", newCoDName = ""):
  if discordName == "":
    members = await serverMembers(ctx)
    profilesUpdated = []
    
    profiles = mongoDb.profiles
    valorantStats = mongoDb.valorantStats
    leagueStats = mongoDb.leagueStats
    
    allProfiles = profiles.find({})
    s = requests.Session()
    
    await ctx.send(f"Updating **all** server member profiles... this can take a... while...")
    
    for i, profile in enumerate(allProfiles):
      if profile['DiscordName'] not in members or not readyForMoreRequests(profile['LastUpdate']):
        continue
      elif profile['ValorantName'] != None or profile['LoLName'] != None:
        profilesUpdated.append(profile['DiscordName'])
        
      valQuery = valorantStats.find_one({"ValorantName": profile['ValorantName']})
      leagueQuery = leagueStats.find_one({"LoLName": profile['LoLName']})
      rate = (i + 1)
  
      if valQuery != None:
        if rate % 3 == 0:
          print("Sleeping")
          time.sleep(rate)
          print("Resuming")
  
        valName = valQuery['ValorantName']
        
        currentValStats = getValStats(valName, False)
        overallValStats = getValStats(valName, True)
      
        updateMongoQueryWObj(valorantStats, valQuery, 
                            {"ValorantName": valName, "points": currentValStats["POINTS"], "currKDA": currentValStats["KDA"], 
                             "currHS": currentValStats["HS"], "currDmg/Round": currentValStats["DMGR"], "allKDA": overallValStats["KDA"], 
                             "allHS": overallValStats["HS"], "allDmg/Round": overallValStats["DMGR"], "currFBR": currentValStats["FBR"], 
                             "allFBR": overallValStats["FBR"]})
        
        updateMongoQueryWObj(profiles, profile, {"LastUpdate": datetime.datetime.now()})
      
      elif profile['ValorantName'] != None:
        valName = profile['ValorantName']
        
        currentValStats = getValStats(valName, False)
        overallValStats = getValStats(valName, True)
        
        insertObjIntoMongo(valorantStats,
                          {"ValorantName": valName, "points": currentValStats["POINTS"], "currKDA": currentValStats["KDA"], 
                           "currHS": currentValStats["HS"], "currDmg/Round": currentValStats["DMGR"], "allKDA": overallValStats["KDA"], 
                           "allHS": overallValStats["HS"], "allDmg/Round": overallValStats["DMGR"], "currFBR": currentValStats["FBR"], 
                           "allFBR": overallValStats["FBR"]}
                          )
        
        updateMongoQueryWObj(profiles, profile, {"LastUpdate": datetime.datetime.now()})
  
      
      if leagueQuery != None:
        leagueName = leagueQuery['LoLName']
        getLeaguePoints(leagueName)
              
    outstring = "\n"
    for profileUpdated in profilesUpdated:
      outstring += f"_{profileUpdated}_\n"
  
    if outstring == "\n":
      await ctx.send("_No profiles updated_")
      return
      
    await ctx.send(f"_Successfully updated the following player's statistics in the database:_ {outstring}")

  else:
    await ctx.send(f"Updating _**all**_ of **{discordName}'s** statistics in the database...")
  
    profiles = mongoDb.profiles
    valorantStats = mongoDb.valorantStats
    leagueStats = mongoDb.leagueStats
    
    profile = profiles.find_one({"DiscordName": discordName})
    valName = profile['ValorantName']
    lolName = profile['LoLName']
  
    if not readyForMoreRequests(profile['LastUpdate']):
      await ctx.send(f"_{discordName}'s profile was updated within the past 20 minutes. Please allow time before your next update_")
      return
      
    valQuery = valorantStats.find_one({"ValorantName": valName})
    leagueQuery = leagueStats.find_one({"LoLName": lolName})
    s = requests.Session()
  
    if valQuery == None:
      insertObjIntoMongo(valorantStats, {"ValorantName": valName})
      valQuery = valorantStats.find_one({"ValorantName": valName})
  
    if leagueQuery == None:
      insertObjIntoMongo(leagueStats, {"LoLName": lolName})
      leagueQuery = leagueStats.find_one({"LoLName": lolName})
  
    if newVal != "" and newLol != "" and newCoDName != "":
      updateMongoQueryWObj(profiles, profile, {"ValorantName": newVal, "LoLName": newLol, "CoDNameName": newCoDName})
    elif newVal != "" and newLol != "":
      updateMongoQueryWObj(profiles, profile, {"ValorantName": newVal, "LoLName": newLol})
    elif newVal != "" and newCoDName != "":
      updateMongoQueryWObj(profiles, profile, {"ValorantName": newVal, "CoDNameName": newCoDName})
    elif newCoDName != "" and newLol != "":
      updateMongoQueryWObj(profiles, profile, {"LoLName": newLol, "CoDNameName": newCoDName})
    elif newVal != "":
      updateMongoQueryWObj(profiles, profile, {"ValorantName": newVal})
    elif newLol != "":
      updateMongoQueryWObj(profiles, profile, {"LoLName": newLol})
    elif newCoDName != "":
      updateMongoQueryWObj(profiles, profile, {"CoDNameName": newCoDName})
  
    valName = valQuery['ValorantName']
    lolName = leagueQuery['LoLName']
  
    
    currentValStats = getValStats(valName, False)
    overallValStats = getValStats(valName, True)
    
    updateMongoQueryWObj(valorantStats, valQuery, 
                        {"ValorantName": valName, "points": currentValStats["POINTS"], "currKDA": currentValStats["KDA"], 
                         "currHS": currentValStats["HS"], "currDmg/Round": currentValStats["DMGR"], "allKDA": overallValStats["KDA"], 
                         "allHS": overallValStats["HS"], "allDmg/Round": overallValStats["DMGR"], "currFBR": currentValStats["FBR"], 
                         "allFBR": overallValStats["FBR"]})
    
    if lolName != "":
      getLeaguePoints(lolName)
  
    updateMongoQueryWObj(profiles, profile, {"LastUpdate": datetime.datetime.now()})
    
    await ctx.send(f"_Successfully updated _**all**_ of **{discordName}'s** statistics in the database_")


@bot.command()
async def coin(ctx):
  result = await headsOrTails()
  await ctx.send(f"**{result}**")



@bot.command()
async def league(ctx, statisticToCheck, discordName = "", count = 3):
  profiles = mongoDb.profiles
  leagueStats = mongoDb.leagueStats
  currProfile = profiles.find_one({"DiscordName": discordName})

  if "#" in discordName:
    currProfile = profiles.find_one({"DiscordName": discordName})
    lolName = currProfile['LoLName']
    
    leagueQuery = leagueStats.find_one({"LoLName": lolName})
    
  elif "#" in statisticToCheck and "#" not in discordName:
    discordName, statisticToCheck = statisticToCheck, discordName
    currProfile = profiles.find_one({"DiscordName": discordName})
    lolName = currProfile['LoLName']
    
    leagueQuery = leagueStats.find_one({"LoLName": lolName})
    
  statisticToCheck = statisticToCheck.lower()
                  
  try:
    if statisticToCheck == "topchamps":
      await recentGames(ctx, riotName, count, False)
    elif statisticToCheck == "recent":
      await recentGames(ctx, riotName, count, True)
    elif statisticToCheck == "leaderboard":
      await leagueLeaderboard(ctx, statisticToCheck)
    elif statisticToCheck == "points":
      await ctx.send(f"Collecting points for {riotName}...")
      playerPoints = getLeaguePoints(discordName)
                  
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
    if statisticToCheck == "currKDA" or statisticToCheck == "kd":
      await ctx.send(f"**{valName}'s** current competitive KDA is: _{valQuery['currKDA']}_")
      return
    elif  statisticToCheck == "currhs%" or statisticToCheck == "hs%":
      await ctx.send(f"**{valName}'s** current HS% is: _{valQuery['currHS']}_")
      return
    elif statisticToCheck == "currdmg/r" or statisticToCheck == "dmg/r":
      await ctx.send(f"**{valName}'s** current DMG/Round is: _{valQuery['currDmg/Round']}_")
      return
    elif statisticToCheck == "currfbr" or statisticToCheck == "fbr":
      await ctx.send(f"**{valName}'s** current first blood rate is: _{valQuery['currFBR']}_")
      return
    elif statisticToCheck == "currpoints" or statisticToCheck == "points":
      await ctx.send(f"**{valName}'s** current Valorant points is _{valQuery['points']}_")
      return
    elif statisticToCheck == "":
      outstring = playerValorantProfile(valName, valQuery)
      await ctx.send(outstring)
    
    elif statisticToCheck == "leaderboard" or statisticToCheck == "globalleaderboard":
      members = await serverMembers(ctx)
      
      stat = "points"
      discordName = discordName.lower()
      
      if discordName == "hs%":
        stat = "currHS"
      elif discordName == "kda":
        stat = "currKDA"
      elif discordName == "dmg/round":
        stat = "currDmg/Round"
      elif discordName == "fbr":
        stat = "currFBR"
      else:
        discordName = stat
        

      leaderboard = valorantStats.find({}).sort(stat, -1)
      currentServerLeaderboard = []
      outstring = ""
      
      if statisticToCheck == "leaderboard":
        outstring = f"_**Valorant {discordName.upper()} Leaderboard**_\n----------------------------------------\n"
        
        for player in leaderboard:
          playerProfile = profiles.find_one({"ValorantName": player["ValorantName"]})
          if playerProfile["DiscordName"] not in members:
            continue
          currentServerLeaderboard.append(player)
      else:
        outstring = f"_**Valorant {discordName.upper()} Global Leaderboard**_\n----------------------------------------\n"
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
      await ctx.send(f"Tag wasn't included in Valorant name \"_{valName}_\"")
    elif type(err) == requests.exceptions.HTTPError:
      await ctx.send(f"Can't find the player. Double check your player name and tag. If those are correct, try loging into tracker.gg with that name and try again.")
    else:
      await ctx.send(f"There was an error. For those who care, the error was: _\"{err}\"_")

@bot.command()
async def wild(ctx, statisticToCheck, discordName = ""):
  profiles = mongoDb.profiles
  wildStats = mongoDb.wildStats

@bot.command()
async def delete(ctx, discordName = "", valName = "", lolName = ""):
  profiles = mongoDb.profiles
  valorantStats = mongoDb.valorantStats
  leagueStats = mongoDb.leagueStats
  
  profile = profiles.find_one({"DiscordName": discordName})
  val = valorantStats.find_one({"ValorantName": valName})
  league = leagueStats.find_one({"LoL": lolName})
  
  if profile != None:
    deleteQueryInCollection(profiles, profile)
  if val != None:
    deleteQueryInCollection(valorantStats, val)
  if league != None:
    deleteQueryInCollection(leagueStats, league)

  await ctx.send(f"_Successfully removed {discordName} from the database_")

async def serverMembers(ctx):
  members = []
  for member in ctx.guild.members:
    members.append(str(member.name) + "#" + str(member.discriminator))

  return members
bot.run(os.environ["_profilerBotToken"])