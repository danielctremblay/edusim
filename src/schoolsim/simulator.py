import datetime
import logging
import random

FORMATTER = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMATTER, level=logging.INFO)
logger = logging.getLogger(__name__)


class Simulator(object):
    """
    Simulateur de données de la réussite scolaire des élèves pour le milieu scolaire primaire québécois.

    """

    def __init__(self, **kwargs):
        """Initialise le simulateur à partir des paramètres de simulation

        :param kwargs: level, nom, description, auteur, année de début et durée en années.
        """
        logger.info("Simulation, simulating new school system")
        self.id = random.getrandbits(128)
        self.ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.type = kwargs.get("sim_type", "Primary school system")
        self.name = kwargs.get("sim_name", "School simulation")
        self.description = kwargs.get("sim_description", "No description")
        self.author = kwargs.get("sim_author", "Fabrique REL")
        self.scenario = kwargs.get("sim_scenario", "default")
        self.date = datetime.date.today()
        self.start_year = kwargs.get("sim_year_start", datetime.date.today().year)
        self.duration = kwargs.get("sim_year_duration", 1)
        # self.engine = SimulationEngine()
        self.system = self.engine.simulate(
            **dict(kwargs.get("system_parameters", {}), start_year=self.start_year, duration=self.duration))


    def __str__(self):
        return self.describe()

    def describe(self):
        """Retourne la description textuelle de l'état du simulateur.

        :return: la description textuelle de l'état du simulateur.
        """
        details = "Simulation: {}\n".format(self.id)
        details += "Name: {}\n".format(self.name)
        details += "Description: {}\n".format(self.description)
        details += "Author: {}\n".format(self.author)
        details += "Timestamp: {}\n".format(self.ts)
        details += "School System\n"
        details += self.system.describe()
        return details

    def save_to_json(self, filepath):
        # TODO make this portable
        pass

    def save_to_txt(self, filepath=None):
        # TODO make this portable
        logger.info("Saving simulation to text file")
        if not filepath:
            filepath = "/Users/daniel/Workspace/GitHub/school_simulation/resources/archive/simulation-" + self.ts + ".txt"
        with open(filepath, "w+") as fh:
            fh.write(self.describe())
            fh.close()

    def save_to_sql(self, filepath):
        # TODO make this portable
        pass

    def save_to_sqlite(self, filepath=None):
        # TODO make this portable
        # if not filepath:
        #     filepath = "/Users/daniel/Workspace/GitHub/school_simulation/resources/archive/simulation" + ".sqlite"
        # try:
        #     Path(filepath).unlink()  # Delete if db exists
        # except:
        #     pass
        # database = DatabaseWriter(filepath, self.system, 'olap')
        pass
