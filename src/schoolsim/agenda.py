import datetime
import dateutil.easter

import logging

logger = logging.getLogger(__name__)

BEFORE = 'before'
AFTER = 'after'
MONDAY = 'mo'
TUESDAY = 'tu'
WEDNESDAY = 'we'
THURSDAY = 'th'
FRIDAY = 'fr'
SATURDAY = 'sa'
SUNDAY = 'su'
SCHOOL_CLOSED = 'school_closed'
CURRENT_YEAR = 2021


class SchoolSchedule(object):
    """Stub: Définit un horaire des cours sur cycle de 5 ou 10 jours.

    """
    # TODO Design SchoolSchedule class
    pass


class SchoolCalendar(object):
    """Définit un calendrier scolaire annuel générique basé sur la structure d'une année scolaire québécoise.

    """

    def __init__(self, year_start, level='primary'):
        """Initialise le calendrier scolaire annuel à partir de l'année du début du calendrier scolaire.
        Ainsi l'année correspondante au calendrier scolaire 2029-2030 est 2029.

        :param year_start: Année de début du calendrier scolaire.
        :param level: Type de calendrier, la valeur par défaut est 'primary'.
        """
        self.year_start = year_start
        self.year_end = year_start + 1
        self.school_year = '{}-{}'.format(self.year_start, self.year_end)
        self.period = '{}-{}'.format(self.year_start, self.year_end)
        self.level = level

        # Civic Holidays
        self.dt_sjb = datetime.date(self.year_end, 6, 24)  # National Holiday, June 24th
        self.dt_patriot = SchoolCalendar.weekday_before(datetime.date(self.year_start, 5, 25),
                                                        MONDAY)  # National Patriot's Day, Monday preceding May 25
        self.dt_easter = dateutil.easter.easter(self.year_end)  # Easter, computed by std library
        self.dt_newyear = datetime.date(self.year_end, 1, 1)  # New Year's Day, January 1st
        self.dt_xmas = datetime.date(self.year_start, 12, 25)  # Christmas Day, December 25th
        self.dt_thanksgiving = SchoolCalendar.weekday_after(
            SchoolCalendar.weekday_after(datetime.date(self.year_start, 9, 30), MONDAY),
            MONDAY)  # Thanksgiving, second Monday in October
        self.dt_labour = SchoolCalendar.weekday_after(datetime.date(self.year_start, 8, 31),
                                                      MONDAY)  # Labour Day, first Monday in September
        self.dt_canadaday = datetime.date(self.year_start, 7, 1)  # Canada Day, July 1st (not used)

        # Other Holidays
        self.springbreak_start = SchoolCalendar.weekday_before(datetime.date(self.year_end, 3, 4), 'Mo')

        self.holidays = []  # Days that are considered holidays (cnt: 20)
        self.pedagogicals = []  # Days that are pedagogical (cnt: 20)
        self.schooldays = []  # Days of school (cnt: 180)

        self.__setup_school_days()
        logger.debug(
            "Instantiating calendar for year {} with {} school days".format(self.school_year, len(self.schooldays)))

    def get_schooldays(self):
        """Retourne la liste des jours de classe.

        :return: la liste des jours de classe.
        """
        return self.schooldays

    def get_holidays(self):
        """Retourne la liste des jours fériés et de congé.

        :return: la liste des jours fériés et de congé.
        """
        return self.holidays

    def get_pedagogicals(self):
        """Retourne la liste des jours pédagogiques.

        :return: la liste des jours pédagogiques.
        """
        return self.pedagogicals

    def __setup_holidays(self):
        # TODO sjb if on weekend
        if self.dt_sjb.weekday() > 4:
            self.holidays.append(SchoolCalendar.workday_before(self.dt_sjb))  # SJ Baptiste
        else:
            self.holidays.append(self.dt_sjb)  # SJ Baptiste
        self.holidays.append(SchoolCalendar.workday_after(self.dt_easter))  # Easter
        self.holidays.append(SchoolCalendar.workday_before(self.dt_easter))  # Easter
        springbreak = [self.springbreak_start] + [SchoolCalendar.workday_offset(self.springbreak_start, AFTER, idx) for
                                                  idx in range(1, 5)]
        self.holidays.extend(springbreak[::-1])
        xmas_end = SchoolCalendar.workday_before(datetime.date(self.year_end, 1, 5))
        xmasbreak = [xmas_end] + [SchoolCalendar.workday_offset(xmas_end, BEFORE, idx) for idx in range(1, 10)]
        self.holidays.extend(xmasbreak)
        self.holidays.append(self.dt_thanksgiving)
        self.holidays.append(self.dt_labour)
        self.holidays = self.holidays[::-1]

    def __setup_pedagogicals(self):
        self.pedagogicals.append(SchoolCalendar.workday_after(SchoolCalendar.workday_after(self.dt_sjb)))
        self.pedagogicals.append(SchoolCalendar.workday_after(self.dt_sjb))
        self.pedagogicals.append(SchoolCalendar.weekday_after(datetime.date(self.year_end, 5, 31), MONDAY))
        self.pedagogicals.append(
            SchoolCalendar.weekday_after(SchoolCalendar.weekday_after(datetime.date(self.year_end, 5, 15), FRIDAY),
                                         MONDAY))
        self.pedagogicals.append(SchoolCalendar.weekday_after(datetime.date(self.year_end, 5, 15), FRIDAY))
        self.pedagogicals.append(SchoolCalendar.weekday_before(datetime.date(self.year_end, 5, 1), FRIDAY))
        self.pedagogicals.append(SchoolCalendar.weekday_after(datetime.date(self.year_end, 3, 31), FRIDAY))
        self.pedagogicals.append(SchoolCalendar.weekday_after(self.springbreak_start, MONDAY))
        self.pedagogicals.append(SchoolCalendar.weekday_before(datetime.date(self.year_end, 2, 16), MONDAY))
        self.pedagogicals.append(SchoolCalendar.weekday_after(datetime.date(self.year_end, 1, 15), FRIDAY))
        self.pedagogicals.append(SchoolCalendar.workday_offset(self.dt_newyear, AFTER, 3))
        self.pedagogicals.append(
            SchoolCalendar.weekday_after(SchoolCalendar.weekday_after(datetime.date(self.year_start, 11, 30), FRIDAY),
                                         FRIDAY))  # Second Friday in December
        self.pedagogicals.append(
            SchoolCalendar.weekday_before(datetime.date(self.year_start, 11, 30), FRIDAY))  # Last Friday in November
        self.pedagogicals.append(
            SchoolCalendar.weekday_after(SchoolCalendar.weekday_after(datetime.date(self.year_start, 10, 31), MONDAY),
                                         MONDAY))  # Second Monday in November
        self.pedagogicals.append(
            SchoolCalendar.weekday_before(self.dt_thanksgiving, FRIDAY))  # Friday before Thanksgiving
        self.pedagogicals.append(
            SchoolCalendar.weekday_before(SchoolCalendar.weekday_before(SchoolCalendar.weekday_before(
                self.dt_thanksgiving, FRIDAY), FRIDAY), FRIDAY))  # Third Friday before Thanksgiving
        self.pedagogicals.append(
            SchoolCalendar.weekday_before(self.dt_labour, FRIDAY))  # Friday before Labour Day
        # All days after August 24th to sum up 180 school days done in setup_school_days

    def __setup_school_days(self):
        self.__setup_holidays()
        self.__setup_pedagogicals()
        offdays = self.holidays + self.pedagogicals
        current_day = SchoolCalendar.workday_before(self.dt_sjb)
        current_school_day = 10
        current_school_week = 18 if current_school_day == 10 else 36  # 18 cycle of 10 days or 36 of 5 days
        # Create school days from the end of the semester to the beginning
        while len(self.schooldays) < 180:
            if current_day not in offdays:
                self.schooldays.append(SchoolDay(current_day, current_school_day, current_school_week))
                # Decrease school name_day
                current_school_day = current_school_day - 1 if current_school_day > 1 else 10
                # Decrease school week
                current_school_week = current_school_week - 1 if current_school_day == 10 else current_school_week
            current_day = SchoolCalendar.workday_before(current_day)
        # Complete pedagogical: prepend school days prior to the 24th
        while current_day > datetime.date(self.year_start, 8, 24):
            self.holidays.append(current_day)
            current_day = SchoolCalendar.workday_before(current_day)
        self.pedagogicals = self.pedagogicals[::-1]
        self.schooldays = self.schooldays[::-1]

    @staticmethod
    def workday_before(date):
        """Retourne le jour de classe précédant la date.

        :param date: la date au format datetime.date
        :return: le jour de classe précédant la date.
        """
        return SchoolCalendar.workday_offset(date, BEFORE, 1)

    @staticmethod
    def workday_after(date):
        """Retourne le jour de classe suivant la date.

        :param date: la date au format datetime.date
        :return: le jour de classe suivant la date.
        """
        return SchoolCalendar.workday_offset(date, AFTER, 1)

    @staticmethod
    def workday_offset(date, direction, offset):
        """Retourne le nième jour de classe précédant ou suivant la date.

        :param date: la date au format datetime.date
        :param direction: la direction du traitement, prend la valeur 'before' ou 'after'
        :param offset: le nombre de jours de classe précédant ou suivant la date.
        :return: le nième jour de classe précédant ou suivant la date.
        """

        if date.weekday() > 4:
            if direction == AFTER:
                date = date + datetime.timedelta(days=1)
            else:
                date = date - datetime.timedelta(days=1)
            return SchoolCalendar.workday_offset(date, direction, offset)
        if offset <= 0:
            # print('Return {}'.format(date))
            return date
        else:
            if direction == AFTER:
                date = date + datetime.timedelta(days=1)
            else:
                date = date - datetime.timedelta(days=1)
            return SchoolCalendar.workday_offset(date, direction, offset - 1)

    @staticmethod
    def weekday_before(date, name_day):
        """Retourne la date du jour précédant la date soumise et correspondant au nom du jour de la semaine désigné.

        :param date: la date au format datetime.date
        :param name_day: le nom du jour de la semaine, prend la valeur 'mo', 'tu', 'we, 'th, 'fr', 'sa', 'su'
        :return: la date du jour précédant la date soumise et correspondant au nom du jour de la semaine désigné.
        """
        return SchoolCalendar.weekday_offset(date, BEFORE, name_day)

    @staticmethod
    def weekday_after(date, name_day):
        """Retourne la date du jour suivant la date soumise et correspondant au nom du jour de la semaine désigné.

        :param date: la date au format datetime.date
        :param name_day: le nom du jour de la semaine, prend la valeur 'mo', 'tu', 'we, 'th, 'fr', 'sa', 'su'
        :return: la date du jour suivant la date soumise et correspondant au nom du jour de la semaine désigné.
        """
        return SchoolCalendar.weekday_offset(date, AFTER, name_day)

    @staticmethod
    def weekday_offset(date, direction, name_day):
        """Retourne la date du jour précédant ou suivant la date soumise, correspondant au nom du jour de la semaine
        désigné et à la direction désignée.

        :param date: la date au format datetime.date
        :param direction: la direction du traitement, prend la valeur 'before' ou 'after'
        :param name_day: le nom du jour de la semaine, prend la valeur 'mo', 'tu', 'we, 'th, 'fr', 'sa', 'su'
        :return: la date du jour précédant ou suivant les conditions
        """
        days = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        if direction == BEFORE:
            date = date - datetime.timedelta(days=1)
        else:
            date = date + datetime.timedelta(days=1)

        if date.weekday() == days.index(name_day[0:2].lower()):
            return date
        else:
            return SchoolCalendar.weekday_offset(date, direction, name_day)

    def describe(self):
        """Retourne la description textuelle de l'état du calendrier scolaire.

        :return: la description textuelle de l'état du calendrier scolaire.
        """
        details = "Calendar: {}\n".format(self.school_year)
        details += "Number of days: {}\n".format(len(self.schooldays))
        return details


class SchoolDay(object):
    """Définit un jour de classe.

    """

    def __init__(self, date, schedule_day_no, schedule_week_no):
        """Initialise la journée de classe

        :param date: la date en format datetime.date
        :param schedule_day_no: le jour de l'horaire de cours
        :param schedule_week_no: le numéro de la semaine du calendrier scolaire
        """
        self.date = date
        self.schedule_day_no = schedule_day_no
        self.schedule_week_no = schedule_week_no

    def __str__(self):
        return "{} {} {}".format(self.date, self.schedule_day_no, self.schedule_week_no)

    def get_date(self):
        """Retoure la date du jour de classe.

        :return: la date du jour de classe.
        """
        return self.date

    def get_school_day(self):
        """Retourne le jour de l'horaire de cours.

        :return: le jour de l'horaire de cours.
        """
        return self.schedule_day_no

    def get_school_week(self):
        """Retourne le numéro de la semaine du calendrier scolaire.

        :return: le numéro de la semaine du calendrier scolaire.
        """
        return self.schedule_week_no
