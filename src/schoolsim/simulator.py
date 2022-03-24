import datetime
import logging
import random
import traceback
import time
import numpy as np

from operator import attrgetter
from pathlib import Path

from . person import TeacherPool, StudentPool
from . establishment import SchoolSystem
from . helpers.database import DatabaseWriter

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
        logger.info("Simulation, initiating SchoolSim")
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
        self.engine = SimulatorEngine()
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
        """STUB"""
        # TODO make this portable
        pass

    def save_to_txt(self, filepath=None):
        """Sauvegarde sous une forme textuelle la simulation du système scolaire.

        :param filepath: le chemin vers le fichier de la base de données.
        :return:
        """
        # TODO make this portable
        logger.info("Saving simulation to text file")
        if not filepath:
            filepath = "~/simulation-" + self.ts + ".txt"
        try:
            with open(filepath, "w+") as fh:
                fh.write(self.describe())
                fh.close()
        except:
            logger.error("Could not save simulation to file")

    def save_to_sql(self, filepath):
        """Sauvegarde les données de simulation dans une base de données au format OLAP pour analyse.

        :param filepath: le chemin vers le fichier de la base de données.
        :return:
        """
        # TODO make this portable
        if not filepath:
            filepath = "~/simulation" + self.ts +  ".sqlite"
        try:
            Path(filepath).unlink()  # Delete if db exists
        except:
            try:
                database = DatabaseWriter(filepath, self.system, 'olap')
            except:
                logger.error("Could not save OLAP data model to database")



    def save_to_sqlite(self, filepath=None):
        """Stub: Sauvegarde les données de simulation dans une base de données au format OLAP.

        :param filepath: le chemin vers le fichier de la base de données.
        :return:
        """
        if not filepath:
            filepath = "~/simulation" + self.ts +  ".sqlite"
            logger.debug("Creating default database {}".format(filepath))

        try:
            Path(filepath).unlink()  # Delete if db exists
        except:
            pass # ignore if file is present

        try:
            database = DatabaseWriter(filepath, self.system, model_type='olap')
        except:
            logger.error("Could not save OLAP data model to database")
            traceback.print_exc()


class SimulatorEngine(object):
    """Définit le moteur de simulation.

    """
    cnx = None
    """Connexion à la base de données."""

    def __init__(self):
        """Initialise le moteur de simulation.

        """
        logger.debug("Simulation, instantiating simulation engine")
        self.staff_pool = []
        self.student_pool = []
        self.state = None
        self.registry = SimulatorRegistry()
        self.system = SchoolSystem()

    def simulate(self, **kwargs):
        """Démarre la simulation et produit un système scolaire complet.

        :param kwargs: les paramètres de la simulation.
        :return: le système scolaire.
        """
        logger.debug("Simulation, starting simulation")
        random.seed()
        for css_parameters in kwargs.get("css_list", []):
            self.__setup_infrastructure(**dict(css_parameters, start_year=kwargs.get("start_year"),
                                               duration=kwargs.get("duration")))
            self.__simulate_staff()
            self.__simulate_enrolment()
            self.__simulate_evaluations()
            # TODO build assiduity fact table w/r to grades
            # print(self.system)  # Prints to file from main
        return self.system

    def __setup_infrastructure(self, **kwargs):
        logger.debug("Simulation, generating infrastructure")
        start_time = time.time()
        self.system.add_css(**kwargs)  # Refer to Configurator for dict structure
        logger.debug("Simulation, infrastructure simulated in {} sec.".format(time.time() - start_time))

    def __simulate_enrolment(self):
        logger.debug("Simulation, simulating student enrolment")
        student_cnt = 0
        start_time = time.time()
        for css in self.system.get_csss():
            css_id = css.id
            for school in css.get_schools():
                school_id = school.id
                for school_year in school.get_schoolyears():
                    school_year_name = school_year.school_year
                    for group in school_year.get_groups():
                        logger.debug(
                            "Simulation, enrolling students to group for css {}, school {} school year {}".format(
                                css_id, school_id, school_year_name))
                        while (group.size - group.enrolment) >= 1:
                            student = self.registry.get_student(css_id, school_id, group, school_year_name)
                            group.add_student(student)
                            student_cnt += 1
        logger.debug("Simulation, {} students simulated in {} sec.".format(student_cnt, time.time() - start_time))

    def __simulate_staff(self):
        logger.debug("Simulation, simulating course staff")
        start_time = time.time()
        staff_cnt = 0
        for css in self.system.get_csss():
            css_id = css.id
            for school in css.get_schools():
                school_id = school.id
                logger.debug("School Year list size is {}".format(len(school.get_schoolyears())))
                for school_year in school.get_schoolyears():
                    # logger.warning("School Year: {}".format(school_year))
                    school_year_name = school_year.school_year
                    for group in school_year.get_groups():
                        titulaire = self.registry.get_titulaire(css_id, school_id, school_year_name, group.grade)
                        group.set_staff(titulaire)
                        logger.debug("Simulation, staffing group {} with titulaire {}".format(group.id, titulaire.uid))
                        for topic in group.get_topics():
                            logger.debug("Simulation, staffing topics with teachers")
                            if topic.isSpeciality is False:
                                teacher = titulaire
                            else:
                                teacher = self.registry.get_specialist(css_id, school_id, school_year_name, topic)
                            topic.set_staff(teacher)
                            staff_cnt += 1
        logger.debug("Simulation, {} staff members simulated in {} sec.".format(staff_cnt, time.time() - start_time))

    def __simulate_evaluations(self):
        logger.debug("Simulation, simulating evaluations for topics and students")
        start_time = time.time()
        evaluation_cnt = 0
        student_cnt = 0
        student_trend_male = -0.03 / 7.0  # minus 3% over 5 years
        student_trend_female = 0.07 / 7.0  # plus 2% over 5 years
        # TODO scheduling: currently a naïve representation, replace with a real school day schedule
        for css in self.system.get_csss():
            css_sf = css.success_factor
            css_sv = css.success_variability
            logger.debug(css.calendars.keys())
            for school in css.get_schools():
                school_sf = school.success_factor
                school_sv = school.success_variability
                idx_yr = 0
                for school_year in sorted(school.get_schoolyears(), key=lambda d: d.school_year):
                    logger.debug("Processing school year: {}".format(school_year.school_year))
                    calendar = css.calendars[school_year.school_year]
                    for group in school_year.get_groups():
                        # TODO evaluation : currently a bonified randomized evaluation scheme,
                        #  replace with a real school day evaluation schedule
                        # TODO scheduling: currently a random school day schedule based on
                        #  number of hours by topic and 10 day schedule, replace with a real school day schedule
                        # if topic_number in (1, 2):
                        #     schedule_days = list(range(1, 11))
                        # elif topic_number in (3, 5, 8, 9):
                        #     schedule_days = sorted(random.sample(range(1, 11), 4))
                        # else:
                        #     schedule_days = sorted(random.sample(range(1, 11), 2))

                        # Randomize the number of evaluation from one group to another : prof variability
                        group_sf = group.success_factor
                        group_sv = group.success_variability
                        for topic in group.get_topics():
                            # TODO manage calendar for evaluation dates
                            topic_id = topic.id
                            topic_sf = topic.success_factor
                            topic_sv = topic.success_variability
                            teacher_sf = topic.teacher.success_factor
                            teacher_sv = topic.teacher.success_variability

                            number_evaluation_topic = [25, 25, 10, 15, 12, 12, 12, 15, 15]
                            number_evaluations = random.randint(number_evaluation_topic[topic_id - 1] - 1,
                                                                number_evaluation_topic[topic_id - 1] + 3)
                            css_id_list = [css.id] * number_evaluations
                            school_id_list = [school.id] * number_evaluations
                            topic_id_list = [topic.id] * number_evaluations
                            topic_teacher_list = [topic.teacher.uid] * number_evaluations
                            evaluation_id_list = range(1, number_evaluations + 1)
                            evaluation_types = []
                            evaluation_dates = []
                            evaluation_durations = []
                            evaluation_totals = []
                            evaluation_is_retake = [False] * number_evaluations  # Not currently used
                            for evaluation_period in [10, 70, 130]:
                                # These blocks correspond to evaluation period with respectif end at
                                #  end of november, end of january and end of june base on calendar of 180 days
                                if evaluation_period in (10, 70):
                                    number_evaluation_period = number_evaluations // 3
                                else:
                                    number_evaluation_period = number_evaluations - (2 * (number_evaluations // 3))
                                evaluation_types_temp = random.choices(('exercices', 'devoir', 'quiz'),
                                                                       weights=(10, 10, 2),
                                                                       k=(number_evaluation_period - 2))
                                evaluation_types_temp.extend(('quiz', 'examen'))
                                evaluation_types.extend(evaluation_types_temp)
                                dates = sorted(random.sample(
                                    calendar.schooldays[evaluation_period:evaluation_period + 48],
                                    number_evaluation_period - 2), key=attrgetter('date'))
                                dates.append(calendar.schooldays[evaluation_period + 48])  # Should be quiz
                                dates.append(calendar.schooldays[evaluation_period + 49])  # Should be exam
                                evaluation_dates.extend([item_date.date for item_date in dates])  # Keep only the date
                                # TODO Move date to prior schedule date and sort dates, currently randomized
                                for item in evaluation_types_temp:
                                    if item in ('exercices', 'quiz'):
                                        evaluation_durations.extend(random.sample(range(8, 25), 1))
                                        evaluation_totals.extend(random.sample(range(15, 25), 1))
                                    elif item in ('examen'):
                                        evaluation_durations.extend(random.sample(range(15, 45), 1))
                                        evaluation_totals.extend(random.sample(range(25, 75), 1))
                                    else:
                                        evaluation_durations.append(0)
                                        evaluation_totals.extend(random.sample(range(10, 25), 1))
                                    evaluation_is_retake.append(False)
                            for student in group.get_students():
                                # Trending can be inserted in config (success factor, success variability)
                                # or be parametrized here as an ad hoc situation
                                student_cnt += 1
                                student_sf = student.success_factor
                                student_sv = student.success_variability
                                trend = student_trend_male if student.gender == 'm' else student_trend_female
                                # Generating results based on :
                                # Student performance, group effect, teacher effect, topic effect, general trend
                                evaluation_results = np.random.normal(student_sf, student_sv,
                                                                      number_evaluations) * \
                                                     (1.0 + np.random.normal(group_sf, group_sv, 1)[0]) * \
                                                     (1.0 + np.random.normal(teacher_sf, teacher_sv, 1)[0]) * \
                                                     (1.0 + np.random.normal(topic_sf, topic_sv, 1)[0]) * (
                                                             1.0 + student.success_year_trend) ** idx_yr * (
                                                             (1 + trend) ** idx_yr)
                                evaluation_cnt += number_evaluations
                                evaluation_results = [
                                    round(result, 3) if result <= 1.0 else round(result - 2 * (result - 1), 3) for
                                    result in evaluation_results]
                                evaluation_scores = [round(pct * total, 1) for (pct, total) in
                                                     zip(evaluation_results, evaluation_totals)]
                                evaluation_pct = [round(score / total, 2) for (score, total) in
                                                  zip(evaluation_scores, evaluation_totals)]
                                evaluation_weights = [round(total * 0.01, 2) for total in
                                                      evaluation_totals]  # TODO improve weights

                                # Generate evaluation tuples for the year
                                try:
                                    evaluation_scheme = zip(topic_id_list, topic_teacher_list, evaluation_id_list,
                                                            evaluation_types, evaluation_dates, evaluation_scores,
                                                            evaluation_totals, evaluation_pct, evaluation_weights,
                                                            evaluation_durations, evaluation_is_retake)
                                    student.results.extend(evaluation_scheme)

                                except:
                                    traceback.print_exc()
                                    logger.warning(
                                        "Simulation, failed to add evaluation")
                idx_yr += 1  # For trending
        logger.debug(
            "Simulation, {} evaluations for {} students simulated in {} sec.".format(evaluation_cnt, student_cnt,
                                                                                     time.time() - start_time))


class SimulatorRegistry(object):
    """Définit les registres des personnes dans la simulation. Les registres assurent la cohérence temporelle des
    années scolaires de la simulation.

    """
    # TODO move registry as subclass
    def __init__(self):
        """Initialise les registres des personnes dans la simulation.

        """
        self.staff_pool = TeacherPool()
        self.staff_registry = []  # All staff
        self.student_pool = StudentPool()
        self.student_registry = []
        self.evaluation_registry = []

    def get_student(self, css_id, school_id, group, school_year):
        """Produit un élève à partir de paramètres en prenant compte de l'année scolaire précédente.

        :param css_id: l'identifiant unique du centre de services scolaires.
        :param school_id: l'identifiant unique de l'école.
        :param group: le group à pourvoir.
        :param school_year: l'année scolaire.
        :return: un élève.
        """
        logger.debug(
            "Simulating a student to css {}, school {}, group {}, school year {}".format(css_id, school_id, group.id,
                                                                                         school_year))
        student_uids = []
        previous_year = str(int(school_year[0:4]) - 1) + "-" + str(int(school_year[5:9]) - 1)
        for registrant in self.student_registry:
            # creating a registry of enrolled student
            (student_css, student_school, student_school_year, student_group, student) = registrant
            if student_css == css_id and student_school == school_id and student_school_year == school_year and \
                    student_group.grade == group.grade and student_group.id == group.id:
                student_uids.append(student.uid)

        for registrant in self.student_registry:
            (student_css, student_school, student_school_year, student_group, student) = registrant
            if student_css == css_id and student_school == school_id and student_school_year == previous_year and \
                    (student_group.grade - 1) == group.grade and student.uid not in student_uids and (
                    group.size - group.enrolment) < student.caseweight:
                self.student_registry.append((css_id, school_id, school_year, group, student))
                return student
        student = self.student_pool.pop()
        # Correct year for age (1st year, 6 years old on sept 30)
        dob = student.dob
        ref_year = int(school_year[0:4]) - (5 + group.grade)
        if 1 < dob.month < 10:
            yob = ref_year
        else:
            yob = ref_year + 1
        dob = dob.replace(year=yob)
        student.dob = dob
        self.student_registry.append((css_id, school_id, school_year, group, student))
        return student

    def get_titulaire(self, css_id, school_id, school_year, grade):
        """Produit une personne enseigante titulaire à partir de paramètres en prenant compte de l'année scolaire précédente.

        :param css_id: l'identifiant unique du centre de services scolaires.
        :param school_id: l'identifiant unique de l'école.
        :param school_year: l'année scolaire.
        :param grade: le niveau (année) scolaire.
        :return: une personne enseignante titulaire d'un groupe.
        """
        logger.debug("Staffing a titulaire")
        staffed_uids = []
        previous_year = str(int(school_year[0:4]) - 1) + "-" + str(int(school_year[5:9]) - 1)
        for registrant in self.staff_registry:
            # Create registry of staffed teacher
            (staff_css, staff_school, staff_school_year, staff_role, staff_grade, staff_topic, teacher,
             workload) = registrant
            if staff_css == css_id and staff_school == school_id and staff_school_year == school_year \
                    and staff_grade == grade and staff_role == 'titulaire':
                staffed_uids.append(teacher.uid)
        for registrant in self.staff_registry:
            # Look for previous year staff teacher
            (staff_css, staff_school, staff_school_year, staff_role, staff_grade, staff_topic, teacher,
             workload) = registrant
            if staff_css == css_id and staff_school == school_id and staff_school_year == previous_year \
                    and staff_grade == grade and staff_role == 'titulaire' and teacher.uid not in staffed_uids:
                self.staff_registry.append((css_id, school_id, school_year, 'titulaire', grade, None, teacher, 1))
                return teacher
        teacher = self.staff_pool.pop()
        self.staff_registry.append((css_id, school_id, school_year, 'titulaire', grade, None, teacher, 1))
        return teacher

    def get_specialist(self, css_id, school_id, school_year, topic):
        """Produit une personne enseigante spécialiste à partir de paramètres en prenant compte de l'année scolaire précédente.

                :param css_id: l'identifiant unique du centre de services scolaires.
                :param school_id: l'identifiant unique de l'école.
                :param school_year: l'année scolaire.
                :param topic: la matière scolaire.
                :return: une personne enseignante titulaire d'un groupe.
        """
        logger.debug("Staffing a specialist")
        previous_year = str(int(school_year[0:4]) - 1) + "-" + str(int(school_year[5:9]) - 1)
        for registrant in self.staff_registry:
            # Create registry of staffed teacher
            (staff_css, staff_school, staff_school_year, staff_role, staff_grade, staff_topic, teacher,
             workload) = registrant
            if staff_css == css_id and staff_school == school_id and staff_school_year == school_year \
                    and staff_topic == topic.name and staff_role == 'specialist' and (1 - workload) < topic.workload:
                registrant[-1] += topic.workload  # Simple update of workload
                return teacher
        for registrant in self.staff_registry:
            # Look for previous year staff teacher
            (staff_css, staff_school, staff_school_year, staff_role, staff_grade, staff_topic, teacher,
             workload) = registrant
            if staff_css == css_id and staff_school == school_id and staff_school_year == previous_year \
                    and staff_topic == topic.name and staff_role == 'specialist':
                self.staff_registry.append(
                    (css_id, school_id, school_year, 'specialist', None, topic, teacher, topic.workload))
                return teacher
        teacher = self.staff_pool.pop()
        self.staff_registry.append((css_id, school_id, school_year, 'specialist', None, topic, teacher, topic.workload))
        return teacher
