import MySQLdb as _mysql
import config


class Db:

    def __init__(self):
        self.config = config.db_config

    def connect(self):
        _mysql.connect(
            host = self.config['host'],
            user = self.config['user'],
            passwd = self.config['passwd'],
            db = self.config['db'],
            port = self.config['port']
        )
