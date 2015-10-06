from database import Db
import MySQLdb as _mysql
from config import ig_config
from instagram import client
from instagram.bind import InstagramAPIError
from multiprocessing import Pool
import sys, logging

reload(sys)
sys.setdefaultencoding("utf-8")


__author__ = 'jaychow'

class shortcodeMine:
    #shortcode var
    filename = "shortcodes.txt"

    #API var
    apiLimit = 5000
    apiCurrent = 0
    clientPosition = 0
    clientLength = 0

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


miner = shortcodeMine()
miner.initDB()
miner.initIg()

with open(miner.filename, 'r') as f:
    for line in f:
        try:
            media_shortcode = miner.api.media_shortcode(shortcode = line)
            print media_shortcode.type + " - " + media_shortcode.link

            ids = media_shortcode.id.split('_')

            lat = 0
            lon = 0
            location = 0
            caption = ""

            if(hasattr(media_shortcode, 'location')):
                lat = media_shortcode.location.point.latitude
                lon = media_shortcode.location.point.longitude
            if(media_shortcode.caption is not None):
                caption = media_shortcode.caption.text.replace("'", r"\'")
            image = {
                'id': ids[0],
                'type': media_shortcode.type,
                'like_count': media_shortcode.like_count,
                'caption': caption,
                'filter': media_shortcode.filter,
                'link': media_shortcode.link,
                'user_id': media_shortcode.user.id,
                'username': media_shortcode.user.username,
                'created_time': media_shortcode.created_time,
                'low_res': media_shortcode.images['low_resolution'].url,
                'thumbnail': media_shortcode.images['thumbnail'].url,
                'standard_res': media_shortcode.images['standard_resolution'].url,
                'lat': lat,
                'lon': lon
            }

            for tag in media_shortcode.tags:
                tagId = miner.db.getTagId(tag=tag.name)
                if(tagId):
                    if(not miner.db.tagRelationExists(tagId, ids[0])):
                        miner.db.addTagRelation(tagId, ids[0])
                else:
                    tagId = miner.db.addTag(tag.name)
                    if(not miner.db.tagRelationExists(tagId, ids[0])):
                        miner.db.addTagRelation(tagId, ids[0])

            miner.db.addImage(tablename='london_selfie', image=image)

        except Exception as e:
            logging.warning(line + " - " + str(e.status_code) + ": " + e.error_type + " - " + e.error_message)


