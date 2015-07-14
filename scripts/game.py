class Game:
    def __init__(self, home, away, setting):
        self.home = home
        self.away = away
        self.setting = setting
        self.home.add_setting(setting)
        self.away.add_setting(setting)
        return None

    def get_team_names():
        return {"home": self.home.name, "away": self.away.name}

    def __str__(self):
        ret = ("home:\n")
        ret += str(self.home)
        ret += ("\n---------\n")
        ret += ("away:\n")
        ret += str(self.away)
        ret += ("\n---------\n")
        # ret += ("setting:\n")
        # ret += str(self.setting)
        return ret


