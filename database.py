import MySQLdb as _mysql
import config


class Db:

    def __init__(self):
        self.config = config.db_config

    def connect(self):
        self.db = _mysql.connect(
            host = self.config['host'],
            user = self.config['user'],
            passwd = self.config['passwd'],
            db = self.config['db'],
            port = self.config['port']
        )
        self.db.set_character_set('utf8mb4')
        self.cursor = self.db.cursor()
        self.cursor.execute('SET NAMES utf8mb4;')
        self.cursor.execute('SET CHARACTER SET utf8mb4;')
        self.cursor.execute('SET character_set_connection=utf8mb4;')


    def getTagId(self, tag):
        self.cursor.execute(
            """
            SELECT id
            FROM tags
            WHERE tag = %s
            """, (tag,)
        )

        row = self.cursor.fetchone()

        while row is not None:
            return row[0]

    def addTag(self,tag):
        self.cursor.execute(
            """
            INSERT INTO tags (tag)
            VALUES (%s)
            """,
            (tag, )
        )
        self.db.commit()
        return self.cursor.lastrowid
    def tagRelationExists(self, tagId, igId):
        self.cursor.execute(
            """
            SELECT image_id, tag_id
            FROM tags_images
            WHERE
              tag_id = %s AND
              image_id = %s
            """,
            (tagId, igId)
        )
        row = self.cursor.fetchone()
        while row is not None:
            return True


    def addTagRelation(self, tagId, igId):
        self.cursor.execute(
            """
            INSERT INTO tags_images (tag_id, image_id)
            VALUES (%s, %s)
            """,
            (tagId, igId)
        )
        self.db.commit()

    def addImage(self, tablename, image):

        sql = """
        INSERT INTO
        {tablename}
        (
            id,
            type,
            like_count,
            caption,
            filter,
            link,
            user_id,
            username,
            created_time,
            low_res,
            thumbnail,
            standard_res,
            lat,
            lon
        )
        VALUES
        (
            {id},
            '{type}',
            '{like_count}',
            '{caption}',
            '{filter}',
            '{link}',
            {user_id},
            '{username}',
            '{created_time}',
            '{low_res}',
            '{thumbnail}',
            '{standard_res}',
            {lat},
            {lon}
        )
        ON DUPLICATE KEY UPDATE
            `type` = '{type}',
            `like_count` = '{like_count}',
            `caption` = '{caption}',
            `filter` = '{filter}',
            `link` = '{link}',
            `user_id` = {user_id},
            `username` = '{username}',
            `created_time` = '{created_time}',
            `low_res` = '{low_res}',
            `thumbnail` = '{thumbnail}',
            `standard_res` = '{standard_res}',
            `lat` = {lat},
            `lon` = {lon}

        """.format(
            tablename=tablename,
            id=image['id'],
            type=image['type'],
            like_count=image['like_count'],
            caption=image['caption'],
            filter=image['filter'],
            link=image['link'],
            user_id=image['user_id'],
            username=image['username'],
            created_time=image['created_time'],
            low_res=image['low_res'],
            thumbnail=image['thumbnail'],
            standard_res=image['standard_res'],
            lat=image['lat'],
            lon=image['lon']
        )

        self.cursor.execute(sql)
        self.db.commit()

