from __future__ import division
from database import Db
import MySQLdb as _mysql
from config import ig_config, location_config
from instagram import client
from instagram.bind import InstagramAPIError
import multiprocessing, sys, logging, time

reload(sys)
sys.setdefaultencoding("utf-8")


__author__ = 'jaychow'

class igMine:

    #API var
    apiLimit = 5000
    apiCurrent = 0
    clientPosition = 0
    clientLength = 0

    #mine var
    lat = location_config.lat
    lng = location_config.lng
    city = location_config.city
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

        return media_search


programStartTime = time.time()
timeStart = 1443398400
timeEnd = 1442793600
advInterval = 60
apiCall = 0
totalIter = (timeStart-timeEnd)/advInterval
totalCounter = 0


miner = igMine()
miner.initDB()
miner.initIg()

def addImage(media, tags):
    try:
        miner.db.addImage(location_config.city, media)
        for tag in tags:
                tagId = miner.db.getTagId(tag=tag.name)
                if(tagId):
                    if(not miner.db.tagRelationExists(tagId, media['id'])):
                        miner.db.addTagRelation(tagId, media['id'])
                else:
                    tagId = miner.db.addTag(tag.name)
                    if(not miner.db.tagRelationExists(tagId, media['id'])):
                        miner.db.addTagRelation(tagId, media['id'])
    except Exception as e:
        logging.warning(media['id'] + " - " + str(e))

    return

while(timeStart > timeEnd):
    elapseTime = time.time()-programStartTime
    try:
        percentDone = (totalCounter/totalIter)*100
        print "Elapse Time:" + elapseTime.__str__()
        print str(percentDone) + "%.... - " + str(apiCall) + " - " + str(timeStart)
        nextTime = timeStart - advInterval
        media_search = miner.search(max_timestamp = timeStart, min_timestamp = nextTime)

        processList = []

        for media in media_search:
            #print "-----" + str(miner.apiCurrent) + ' - entry: ' + media.id + " - " + media.link
            miner.apiCurrent += 1

            ids = media.id.split('_')

            lat = 0
            lon = 0
            location = 0
            caption = ""
            
            if(hasattr(media, 'location')):
                lat = media.location.point.latitude
                lon = media.location.point.longitude
            if(media.caption is not None):
                caption = media.caption.text.replace("'", r"\'")
            image = {
                'id': ids[0],
                'type': media.type,
                'like_count': media.like_count,
                'caption': caption,
                'filter': media.filter,
                'link': media.link,
                'user_id': media.user.id,
                'username': media.user.username,
                'created_time': media.created_time,
                'low_res': media.images['low_resolution'].url,
                'thumbnail': media.images['thumbnail'].url,
                'standard_res': media.images['standard_resolution'].url,
                'lat': lat,
                'lon': lon
            }
            '''
            p = multiprocessing.Process(target=addImage, args=(image,media.tags))
            processList.append(p)
            p.start()
            '''
            addImage(image,media.tags)
        apiCall += 1
        totalCounter += 1
        timeStart = nextTime
    except InstagramAPIError as e:
        logging.warning(str(timeStart) + " - " + str(e.status_code) + ": " + e.error_type + " - " + e.error_message)
        print e.status_code
        if(e.status_code == '429'):
            if miner.clientPosition == miner.clientLength-1:
                miner.clientPosition == 0
            else:
                miner.clientPosition += 1
                miner.initIg()



