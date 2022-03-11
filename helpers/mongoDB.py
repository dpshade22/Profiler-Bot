from pymongo import MongoClient

def createProfile(discord, valName = "", leagueName = "", codName = ""):
  myData = {
      "discordName": discord,
      "valName": valName,
      "leagueName": leagueName,
      "codName": codName,
  }
  return myData

client = MongoClient(
    "mongodb+srv://dpshade22:dpS82212201!@cluster0.z1jes.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
)

db = client.profileDB

profiles = db.profiles

profiles.insert_one(createProfile("dpshade22#0196", "41619#NA1", "41619"))
