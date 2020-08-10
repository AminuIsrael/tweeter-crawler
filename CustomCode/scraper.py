import twint

c = twint.Config()
c.Limit = 20
c.Username = "Aminu_israelb"
c.Pandas = True
c.User_full = True

twint.run.Followers(c)

Users_df = twint.storage.panda.User_df