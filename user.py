from riotGames import LeagueProfile

class User:
  def __init__(self, userName, riotName = ""):
    self.userName = userName
    self.riotName = None
    self.leagueProfile = LeagueProfile(self.riotName)

    