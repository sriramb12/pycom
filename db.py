import pickle
from conf import config
from os.path import exists
import json
from util import createLogger



class MftDb:
  def __init__(self):
     self.logger = createLogger("db", "debug")
     self.logger.error("Init db")
     self.dbfile = config.get('Settings', 'dbfile')
     self.loadDb()

  def addApprover(self, approver, grp):
      self.logger.info("approver ", approver, "added for group", grp)
      print(grp, self.db['SDEApproverGroups'][grp])
      if approver not in self.db['SDEApproverGroups'][grp]:
         self.db['SDEApproverGroups'][grp] += [approver]

  def isSdeUser(self, user):
     return user in self.db['SDEUsers']

  def addUser(self, user):
    self.logger.info("user", user, "added")
    if user not in self.db['SDEUsers']:
       self.db['SDEUsers'] += [user]
       return
    print(user, "exists")

  def loadDb(self):
    try:
     with open(self.dbfile) as json_file:
       self.db = json.load(json_file)
       print(self.db)
    except:
         print("Unable to load ", self.dbfile)
         exit(0)
    #self.showDb()

  def writeDb(self):
    with open(self.dbfile, 'w') as json_file:
     json.dump(self.db, json_file)

  def showDb(self):
    print("Users")
    print(self.db['SDEUsers'])
    print(self.db['SDEApproverGroups'])

if __name__ == "__main__":
  db = MftDb()
  db.addUser('sriram')
  db.addUser('sriram')
  db.addApprover('anton', 'IP')
  db.addApprover('matt', 'NonIP')
  db.addApprover('anton', 'NonIP')
  db.addApprover('birk', 'IP')
  db.showDb()
  print(db.isSdeUser('sriram'))
  print(db.isSdeUser('joe'))
  db.writeDb()
