import sqlite3
import logging
import traceback

logger = logging.getLogger(__name__)

class Database(object):
    cxn = None

    def __init__(self, db_filepath):
        logger.debug("Database, instantiating database handler for dashboarding")
        self.cxn_str = db_filepath

    def connect_db(self):
        logger.debug("Database, getting database connexion for dashboarding")
        if self.cxn is not None:
            return self.cxn

        try:
            self.cxn = sqlite3.connect(self.cxn_str)
        except:
            logger.error("Could not connect to dashboarding database")
            self.cxn = None
            traceback.print_exc()

        return self.cxn


