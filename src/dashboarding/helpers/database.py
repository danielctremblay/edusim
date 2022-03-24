import sqlite3
import logging
import traceback

logger = logging.getLogger(__name__)

class Database(object):
    cxn = None

    def __init__(self, db_filepath):
        # logger.info("Database, instantiating database handler")
        self.cxn_str = db_filepath
        pass

    def connect_db(self):
        # logger.info("Database, getting database connexion")
        if self.cxn is not None:
            return self.cxn

        try:
            print(self.cxn_str)
            self.cxn = sqlite3.connect(self.cxn_str)
        except:
            logger.error("Could not connect to database")
            self.cxn = None
            traceback.print_exc()

        return self.cxn


