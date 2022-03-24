import datetime
import logging

from .agenda import SchoolCalendar

LANGUAGE_1ST = 'Langue principale'
LANGUAGE_1ST_ENGLISH = 'Anglais'
LANGUAGE_1ST_FRENCH = 'Français'
LANGUAGE_2ND = 'Langue seconde'
LANGUAGE_2ND_ENGLISH = 'Anglais langue seconde'
LANGUAGE_2ND_FRENCH = 'Français langue seconde'
LANGUAGE_ELECTIVE = 'Langue troisième'
LANGUAGE_ELECTIVE_SPANISH = 'Espagnol langue autre'
MATHEMATICS = 'Mathématiques'
PHYSICAL_EDUCATION = 'Éducation physique'
DRAMA = 'Art dramatique'
PLASTIC_ARTS = 'Arts plastiques'
DANCE = 'Danse'
MUSIC = 'Musique'
ETHICS = 'Éthique'
GEOGRAPHY = 'Géographie'
STEM = 'Science'
KINDERGARDEN = 'maternelle'
GRADE_1 = '1e année'
GRADE_2 = '2e année'
GRADE_3 = '3e année'
GRADE_4 = '4e année'
GRADE_5 = '5e année'
GRADE_6 = '6e année'
GRADE_DEFAULT = 'grade_default'
GRADE_ALL = 'grade_all'
GRADE_MULTI_23 = 'grade_multi23'
LANGUAGE_FRENCH = 'Français'
LANGUAGE_ENGLISH = 'Anglais'
MILIEU_STANDARD = 'Standard'
MILIEU_UNDERPRIVILEGED = 'Défavorisé'
LEVEL_PRIMARY = 'Primaire'
LEVEL_SECONDARY = 'Secondaire'
SCHOOL_DEFAULT = 'school_default'
SCHOOL_ALL = 'school_all'
GROUP_SIZE_DEFAULT = 'group_size_default'

logger = logging.getLogger(__name__)


class Topic(object):
    """Définit la matière scolaire.

    """

    def __init__(self, **kwargs):
        """Initialise la matière scolaire.

        :param kwargs: les paramètres de définition de la matière scolaire.
        """
        self.id = kwargs.get("id", "N/A")
        self.name = kwargs.get("name", "N/A")
        self.grade = kwargs.get("grade", "N/A")
        self.duration = kwargs.get("duration", "N/A")
        self.success_factor = kwargs.get("success_factor", 0)
        self.success_variability = kwargs.get("success_variability", 0)
        self.workload = self.duration / 25.0
        self.teacher = None
        if self.name in [PHYSICAL_EDUCATION, LANGUAGE_2ND_ENGLISH, LANGUAGE_2ND_FRENCH, LANGUAGE_ELECTIVE_SPANISH,
                         MUSIC]:
            self.isSpeciality = True
        else:
            self.isSpeciality = False
        if self.name in [PHYSICAL_EDUCATION, MUSIC]:
            self.sharesRoom = 1
        else:
            self.sharesRoom = 0

    def __str__(self):
        return self.describe()

    def set_staff(self, teacher):
        """Définit la personne enseignante.

        :param teacher: la personne enseignante.
        :return:
        """
        self.teacher = teacher

    def get_staff(self):
        """Retourne la personne enseignante.

        :return: la personne enseignante.
        """
        return self.teacher

    def describe(self, offset=0):
        """Retourne la description textuelle de l'état de la matière scolaire.

        :param offset: le nombre de tabulations pour l'indentation du texte.
        :return: la description textuelle de l'état de la matière scolaire.
        """
        spacer_0 = "\t" * offset
        spacer_1 = "\t" * (offset + 1)
        details = spacer_0
        details += "Topic: {}\n".format(self.name) + spacer_1
        details += "Topic grade: {}\n".format(self.grade) + spacer_1
        details += "Topic duration: {}\n".format(self.duration) + spacer_1
        details += "Topic is speciality: {}\n".format(self.isSpeciality) + spacer_1
        offset += 1
        if self.teacher:
            details += "Topic teacher: \n{}".format(self.teacher.describe(offset=offset))
        else:
            details += "Topic teacher: NONE\n"
        return details


class Group(object):
    """Définit le groupe scolaire.

    """

    def __init__(self, **kwargs):
        """Initialise le groupe scolaire.

        :param kwargs: les paramètres du groupe scolaire.
        """
        logger.debug(
            "Group, instantiation group {} in grade {} from parameters".format(kwargs.get("id"), kwargs.get("grade")))
        self.id = kwargs.get("id", -1)
        self.grade = kwargs.get("grade", -1)
        self.success_factor = kwargs.get("success_factor", 0)
        self.success_variability = kwargs.get("success_variability", 0)
        if 1 <= self.grade <= 2:
            self.cycle = 1
        elif 2 < self.grade <= 4:
            self.cycle = 2
        else:
            self.cycle = 3
        self.size = kwargs.get("size", -1)
        self.titulaire = None
        self.students = []
        self.enrolment = len(self.students)
        self.topics = []
        for topics in kwargs.get("topic_list", []):
            self.topics.append(Topic(**topics))

    def __str__(self):
        return self.describe()

    def get_topics(self):
        """Retourne la liste des matières scolaires du groupe.

        :return: la liste des matières scolaires du groupe.
        """
        return self.topics

    def get_students(self):
        """Retourne la liste des élèves dans le groupe scolaire.

        :return: la liste des élèves dans le groupe scolaire.
        """
        return self.students

    def add_student(self, student):
        """Ajoute un élève dans le groupe scolaire.

        :param student: l'élève à ajouter.
        :return:
        """
        # TODO manage case weight with return of success failure to add
        self.students.append(student)
        self.enrolment = self.enrolment + student.caseweight

    def set_staff(self, teacher):
        """Définit la personne enseignante du groupe scolaire.

        :param teacher: la personne enseignante du groupe scolaire.
        :return:
        """
        self.titulaire = teacher

    def describe(self, offset=0):
        """Retourne la description textuelle de l'état du groupe scolaire.

        :param offset: le nombre de tabulations pour l'indentation du texte.
        :return: la description textuelle de l'état du groupe scolaire.
        """
        spacer_0 = "\t" * offset
        spacer_1 = "\t" * (offset + 1)
        details = spacer_0
        details += "Group id: {}\n".format(self.id) + spacer_1
        details += "Group grade: {}\n".format(self.grade) + spacer_1
        details += "Group cycle: {}\n".format(self.cycle) + spacer_1
        details += "Group size: {}\n".format(self.size) + spacer_1
        try:
            details += "Group titulaire: {}\n".format(self.titulaire.firstname + " " + self.titulaire.lastname)
        except:
            logger.error("No titulaire for group {}".format(self.id))
        offset += 1
        for topic in self.topics:
            details += topic.describe(offset=offset)
        return details


class SchoolYear(object):
    """Définit l'année scolaire à l'école en gérant les groupes et l'horaire.

    """

    def __init__(self, **kwargs):
        """Initialise l'année scolaire.

        :param kwargs: les paramètres de l'année scolaire.
        """
        logger.debug("School Year, instantiating school year {} from parameters".format(kwargs.get("school_year")))
        self.school_year = kwargs.get("school_year", None)
        self.groups = []
        for group in kwargs.get("group_list", []):
            self.groups.append(Group(**group))
        self.schedule = None

    def __str__(self):
        return self.describe()

    def get_groups(self):
        """Retourne la liste des groupes de l'année scolaire.

        :return: la liste des groupes de l'année scolaire.
        """
        return self.groups

    def describe(self, offset=0):
        """Retourne la description textuelle de l'état de l'année scolaire.

        :param offset: le nombre de tabulations pour l'indentation du texte.
        :return: la description textuelle de l'état de l'année scolaire.
        """
        spacer_0 = "\t" * offset
        details = spacer_0
        details += "School Year: {}\n".format(self.school_year)
        offset += 1
        for group in self.groups:
            details += group.describe(offset=offset)
        return details


class School(object):
    """Définit l'école.

    """

    def __init__(self, **kwargs):
        """Initialise l'école.

        :param kwargs: les paramètres de l'école.
        """
        logger.debug("School, instantiating school {} from parameters".format(kwargs.get("id")))
        self.id = kwargs.get("id", None)
        self.name = kwargs.get("name", None)
        self.language = kwargs.get("language", None)
        self.level = kwargs.get("level", None)
        self.schedule_days = kwargs.get("schedule_days", None)
        self.milieu = kwargs.get("milieu", None)
        self.capacity_groups = kwargs.get("capacity_groups", None)
        self.success_factor = kwargs.get("success_factor", 0)
        self.success_variability = kwargs.get("success_variability", 0)
        self.school_years = []
        for school_year_parameters in kwargs.get("school_year_list", []):
            self.add_schoolyear(**school_year_parameters)

    def __str__(self):
        return self.describe()

    def get_id(self):
        """Retourne l'identifiant unique de l'école.

        :return: l'identifiant unique de l'école.
        """
        return self.id

    def add_schoolyear(self, **kwargs):
        """Ajoute une année scolaire à l'école.

        :param kwargs: les paramètres de l'année scolaire.
        :return:
        """
        self.school_years.append(SchoolYear(**kwargs))

    def get_schoolyears(self):
        """Retourne la liste des années scolaires.

        :return: la liste des années scolaires.
        """
        return self.school_years

    def describe(self, offset=0):
        """Retourne la description textuelle de l'état de l'école.

        :param offset: le nombre de tabulations pour l'indentation du texte.
        :return: la description textuelle de l'état de l'école.
        """
        spacer_0 = "\t" * offset
        spacer_1 = "\t" * (offset + 1)
        details = spacer_0
        details += "School id: {}\n".format(self.id) + spacer_1
        details += "School name: {}\n".format(self.name) + spacer_1
        details += "School language: {}\n".format(self.language) + spacer_1
        details += "School level: {}\n".format(self.level)
        offset += 1
        for school_year in self.school_years:
            details += school_year.describe(offset=offset)
        return details


class Css(object):
    """Définit le centre de services scolaires.

    """

    def __init__(self, **kwargs):
        """Initialise le centre de services scolaires.

        :param kwargs: les paramètres du centre de services scolaires.
        """
        logger.debug("CSS, instantiating CSS {} from parameters".format(kwargs.get("id")))
        self.id = kwargs.get("id", "No css id provided")
        self.name = kwargs.get("name", "No css name provided")
        self.language = kwargs.get("language", "No css language provided")
        self.success_factor = kwargs.get("success_factor", 0)
        self.success_variability = kwargs.get("success_variability", 0)
        self.calendars = {}
        self.schools = []
        for idx in range(0, kwargs.get("duration", 1)):
            start_year = kwargs.get("start_year", datetime.date.today().year) + idx
            end_year = start_year + 1
            school_year = "{}-{}".format(start_year, end_year)
            self.add_calendar(school_year)
        for school_parameters in kwargs.get("school_list", []):
            self.add_school(**school_parameters)

    def __str__(self):
        return self.describe()

    def add_school(self, **kwargs):
        """Ajoute une école au centre de services scolaires.

        :param kwargs: les paramètres de l'école à ajouter
        :return:
        """
        self.schools.append(School(**kwargs))

    def get_id(self):
        """Retourne l'identifiant unique du centre de services scolaires.

        :return: l'identifiant unique du centre de services scolaires.
        """
        return self.id

    def add_calendar(self, school_year):
        """Ajoute un calendrier scolaire au cendre de services scolaires.

        :param school_year: les paramètres du calendrier scolaire.
        :return:
        """
        self.calendars[school_year] = SchoolCalendar(int(school_year[0:4]))

    def get_school(self, school_id):
        """Retourne l'école à partir de son identifiant unique.

        :param school_id: l'identifiant unique de l'école.
        :return: l'école à partir de son identifiant unique.
        """
        for school in self.schools:
            if school.get_id() == school_id:
                return school
        return None

    def get_schools(self):
        """Retourne la liste des écoles du centre de services scolaires.

        :return: la liste des écoles du centre de services scolaires.
        """
        return self.schools

    def get_calendars(self):
        """Retourne la liste des calendriers scolaires du centre de services scolaires.

        :return: la liste des calendriers scolaires du centre de services scolaires.
        """
        return self.calendars.values()

    def describe(self, offset=0):
        """Retourne la description textuelle de l'état du centre de services scolaires.

        :param offset: le nombre de tabulations pour l'indentation du texte.
        :return: la description textuelle de l'état du centre de services scolaires.
        """
        spacer_0 = "\t" * offset
        spacer_1 = "\t" * (offset + 1)
        details = spacer_0
        details += "CSS id: {}\n".format(self.id) + spacer_1
        details += "CSS name: {}\n".format(self.name) + spacer_1
        details += "CSS language: {}\n".format(self.language)
        offset += 1
        for school in self.schools:
            details += school.describe(offset=offset)
        return details


class SchoolSystem(object):
    """Définit le système scolaire à simuler.

    """

    def __init__(self):
        """Initialise le système scolaire à simuler.

        """
        logger.info("Simulation, simulating the school system")
        self.css = []

    def get_css(self, css_id):
        """Retourne le centre de service selon son identifiant unique

        :param css_id: l'identifiant unique du centre de service
        :return: le centre de service
        """
        logger.debug(("Searching for css {}".format(css_id)))
        for a_css in self.css:
            if a_css.get_id() == css_id:
                return a_css
        return None

    def get_csss(self):
        """Retourne la liste des centres de services scolaires du système scolaire.

        :return: la liste des centres de services scholaires.
        """
        return self.css

    def add_css(self, **kwargs):
        """Ajouter un centre de services scolaires au système scolaire.

        :param kwargs: les paramètres du centre de services scolaires.
        :return:
        """
        self.css.append(Css(**kwargs))

    def describe(self):
        """Retourne la description textuelle de l'état du système scolaire.

        :return: la description textuelle de l'état du système scolaire.
        """
        details = ""
        for center in self.css:
            details += center.describe()
        return details
