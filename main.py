from database import Db
import MySQLdb as _mysql
from config import ig_config
from instagram import client
from instagram.bind import InstagramAPIError
from multiprocessing import Pool


__author__ = 'jaychow'

class igMine:

    #API var
    apiLimit = 5000
    apiCurrent = 0
    clientPosition = 0
    clientLength = 0

    #mine var
    lat = "51.511620"
    lng = "-0.117492"
    distance = 5000

    def __init__(self):
        self.ig_config = ig_config
        self.clientLength = len(ig_config)
        print self.clientLength

    def initDB(self):
        self.db = Db()
        self.db.connect()

    def initIg(self):
        pos = self.clientPosition
        self.api = client.InstagramAPI(
            client_id=self.ig_config[pos]['client_id'],
            client_secret=self.ig_config[pos]['client_secret']
        )

    def search(self, max_timestamp, min_timestamp):
        media_search = self.api.media_search(
            lat=self.lat,
            lng=self.lng,
            distance=self.distance,
            max_timestamp = max_timestamp,
            min_timestamp = min_timestamp
        )

        for media in media_search:
            print "-----" + str(self.apiCurrent) + ' - entry: ' + media.id + " - " + media.link
            self.apiCurrent += 1



timeStart = 1443398400
timeEnd = 1442793600
advInterval = 60
apiCall = 0

miner = igMine()
miner.initDB()
miner.initIg()

while(timeStart > timeEnd):
    try:
        nextTime = timeStart - advInterval
        print str(apiCall) + " - " + str(timeStart)
        miner.search(max_timestamp = timeStart, min_timestamp = nextTime)
        apiCall += 1
        timeStart = nextTime
    except InstagramAPIError as e:
        print e.status_code
        print e.message


