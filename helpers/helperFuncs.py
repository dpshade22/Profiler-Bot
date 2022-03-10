def insertSortLists(keys, values):
    for i in range(0, len(keys)):
        key = values[i]
        key2 = keys[i]

        j = i - 1
        while j >= 0 and key > values[j]:
            values[j + 1] = values[j]
            keys[j + 1] = keys[j]
            j -= 1

        values[j + 1] = key
        keys[j + 1] = key2

    return keys, values

def insertSortChamps(champList):
    for i in range(0, len(champList)):
        key = champList[i]
        key2 = champList[i]

        j = i - 1
        while j >= 0 and key.points > champList[j].points:
            champList[j + 1] = champList[j]
            j -= 1
        champList[j + 1] = key
        champList[j + 1] = key2

    return champList

def parseInput(message):
  wordsList = message.split(' ')
  return wordsList