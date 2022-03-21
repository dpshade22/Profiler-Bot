import pymongo
import os

mongoPass = os.environ['mongoPass']

client = pymongo.MongoClient(f"mongodb+srv://dpshade22:{mongoPass}@cluster0.z1jes.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
mongoDb = client.profileDB

def insertObjIntoMongo(collection, obj):
  collection.insert_one(obj)
  print(f"Successfully added {obj} to the MongoDB Collection: {collection.name}")

def updateMongoQueryWObj(collection, query, obj):
  collection.update_one(query, {"$set": obj})
  print(f"Successfully updated {obj} in the MongoDB Collection:{collection.name}")