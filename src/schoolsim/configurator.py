import json
import logging

FORMATTER = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMATTER, level=logging.INFO)
logger = logging.getLogger(__name__)


class Configurator(object):
    """Configurateur de la simulation SchoolSim qui permet de créer un fichier configuration de base
    de la simlation SchoolSim.

    """

    def __init__(self):
        """Initialise une simulation SchoolSim.

        """
        self.simulation_type = None
        self.simulation_name = None
        self.simulation_description = None
        self.simulation_author = None
        self.simulation_scenario = None
        self.simulation_start_year = None
        self.simulation_duration = None
        self.css_definition_list = []

    def __str__(self):
        return self

    def save_to_file(self, filepath):
        """Sauvegarde le fichier de configuration de SchoolSim au format JSON.

        :param filepath: le chemin complet au fichier
        :return:
        """
        simulation = {
            "simulation": {
                "sim_type": self.simulation_type,
                "sim_name": self.simulation_name,
                "sim_description": self.simulation_description,
                "sim_author": self.simulation_author,
                "sim_scenario": self.simulation_scenario,
                "sim_year_start": self.simulation_start_year,
                "sim_year_duration": self.simulation_duration,
                "system_parameters": {"css_list": self.css_definition_list}
            }
        }
        try:
            # Human readable
            with open(filepath, 'w+', encoding='utf8') as fh:
                fh.write(json.dumps(simulation, indent=4, sort_keys=True, ensure_ascii=False))
        except:
            logger.error("Could not save simulation configuration to file {}".format(filepath))

    def set_simulation_default(self):
        """Définit les paramètres par défaut de la simulation SchoolSim.

        :return:
        """
        # TODO lire les paramètres à partir d'un fichier de configuration
        logger.info("Configuration, generating configuration file")
        self.simulation_type = "education"
        self.simulation_name = "School simulation 001"
        self.simulation_description = "Simulation de données pour une école primaire du projet Fabrique REL"
        self.simulation_author = "Daniel Chamberland-Tremblay"
        self.simulation_scenario = "default"
        self.simulation_start_year = 2015
        self.simulation_duration = 7
        self.__set_css_default()
        self.__set_school_default()
        self.__set_school_year_default()

    def __set_css_default(self):
        """Définit les paramètres par défaut du centre de services scolaires dans SchoolSim.

        :return:
        """
        logger.info("Configuration, adding CSS to simulation")
        css_parameters = [(1, "CSS de la Réussite", "Français", 0, 0)]
        for css_tuple in css_parameters:
            (id, name, language, css_sf, css_sv) = css_tuple
            self.css_definition_list.append(
                {"id": id, "name": name, "language": language, "success_factor": css_sf,
                 "success_variability": css_sv})

    def __set_school_default(self):
        """Définit les paramètres par défaut de l'école primaire dans SchoolSim.

        :return:
        """
        logger.info("Configuration, adding schools to simulation")
        school_parameters = [(1, "École du Bleu Infini", "Français", "primary", 10, "standard", 20, 0, 0)]
        school_definition_list = []
        for css_dict in self.css_definition_list:
            if css_dict["id"] == 1:
                for school_tuple in school_parameters:
                    (school_id, school_name, school_language, school_level, schedule_days, milieu,
                     capacity, school_sf, school_sv) = school_tuple
                    school_definition_list.append(
                        {"id": school_id, "name": school_name, "language": school_language,
                         "level": school_level, "schedule_days": schedule_days, "milieu": milieu,
                         "capacity_groups": capacity, "success_factor": school_sf,
                         "success_variability": school_sv})
                css_dict['school_list'] = school_definition_list

    def __set_school_year_default(self):
        """Définit les paramètres par défaut de l'année scolaire dans SchoolSim.

        :return:
        """
        logger.info("Configuration, adding school years with groups and topics to simulation")
        # Group tuple : id, grade, size, sucess factor, success variability
        group_parameters = [(1, 1, 20, 0.01, 0.001), (2, 1, 20, -0.01, 0.001), (3, 2, 20, 0.001, 0.0001),
                            (4, 2, 20, 0.001, 0.0001), (5, 3, 22, 0.001, 0.0001), (6, 3, 22, 0.001, 0.0001),
                            (7, 4, 22, 0.001, 0.0001), (8, 4, 22, 0.001, 0.0001), (9, 5, 24, 0.001, 0.0001),
                            (10, 5, 24, 0.001, 0.0001), (11, 6, 24, 0.001, 0.0001), (12, 6, 24, 0.001, 0.0001)]
        # Topic tuple : id, name, hours TODO include sucess factor ?
        topic_parameters = [(1, "Français", -0.03, 0.005), (2, "Mathématiques", -0.05, 0.005),
                            (3, "Éducation physique", 0.05, 0.01), (4, "Anglais langue seconde", 0, 0.005),
                            (5, "Arts plastiques", 0.05, 0.01), (6, "Musique", 0, 0), (7, "Éthique", 0, 0),
                            (8, "Univers social", 0, 0), (9, "Sciences", -0.03, 0.05)]
        # Year topic tuple : grade, topic id, hours
        year_topic_parameters = [(1, 1, 9), (1, 2, 7), (1, 3, 2), (1, 4, 1), (1, 5, 2), (1, 6, 1), (1, 7, 1), (2, 1, 9),
                                 (2, 2, 7), (2, 3, 2), (2, 4, 1), (2, 5, 2), (2, 6, 1), (2, 7, 1), (3, 1, 9), (3, 2, 5),
                                 (3, 3, 2), (3, 4, 2), (3, 5, 2), (3, 6, 2), (3, 7, 1), (3, 8, 2), (3, 9, 2), (4, 1, 9),
                                 (4, 2, 5), (4, 3, 2), (4, 4, 2), (4, 5, 2), (4, 6, 2), (4, 7, 1), (4, 8, 2), (4, 9, 2),
                                 (5, 1, 9), (5, 2, 5), (5, 3, 2), (5, 4, 2), (5, 5, 2), (5, 6, 2), (5, 7, 1), (5, 8, 2),
                                 (5, 9, 2), (6, 1, 9), (6, 2, 5), (6, 3, 2), (6, 4, 2), (6, 5, 2), (6, 6, 2), (6, 7, 1),
                                 (6, 8, 2), (6, 9, 2)]
        for css_dict in self.css_definition_list:
            for school_dict in css_dict['school_list']:
                school_year_parameters = []
                for idx in range(0, self.simulation_duration):
                    school_year = str(self.simulation_start_year + idx) + "-" + str(
                        self.simulation_start_year + idx + 1)
                    group_list = []
                    for group_tuple in group_parameters:
                        topic_list = []
                        (group_id, group_grade, group_size, group_sf, group_sv) = group_tuple
                        for year_topic_tuple in year_topic_parameters:
                            (topic_grade, topic_id, topic_duration) = year_topic_tuple
                            (topic_id, topic_name, topic_sf, topic_sv) = [topic for topic in topic_parameters if
                                                                          topic[0] == topic_id][0]

                            if group_grade == topic_grade:
                                topic_list.append(
                                    {"id": topic_id, "name": topic_name, "grade": topic_grade,
                                     "duration": topic_duration, "success_factor": topic_sf,
                                     "success_variability": topic_sv})
                        group_list.append(
                            {"id": group_id, "grade": group_grade, "size": group_size, "success_factor": group_sf,
                             "success_variability": group_sv, "topic_list": topic_list})

                    school_year_parameters.append({"school_year": school_year, "group_list": group_list})
            school_dict['school_year_list'] = school_year_parameters
