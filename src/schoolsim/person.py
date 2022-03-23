import datetime
import math
import random
import re
from abc import abstractmethod, ABC
import numpy as np
import pandas as pd
import logging

import unidecode as unidecode

from simulation.lib.database import Database

PEOPLE_ALL = 'people_all'

logger = logging.getLogger(__name__)


class Person(ABC):
    """Person class"""

    def __init__(self, firstname, lastname, dob, gender):
        self.id = (lastname[0:3] + firstname[0:1] + str(dob.year)).lower()
        self.firstname = firstname
        self.lastname = lastname
        self.dob = dob
        self.gender = gender
        self.profile = None


class Student(Person):
    """Student class"""

    def __init__(self, firstname, lastname, dob, gender, caseweight=1):
        super().__init__(firstname, lastname, dob, gender)
        self.profile = 'student'
        self.status = 'normal'  # TODO provide profile + headcount + success_factor penality
        self.uid = re.sub('[- .]', 'x', lastname[0:3].lower()) + firstname[0:1].lower() + str(dob.day).zfill(2) + str(
            dob.month).zfill(2)
        self.uid = unidecode.unidecode(self.uid)  # Remove accents
        self.caseweight = caseweight
        self.success_factor = np.random.normal(0.78, 0.08, 1)[0] if self.gender == 'f' else np.random.normal(0.68, 0.08, 1)[0]
        self.success_variability = abs(np.random.normal(0, 0.05, 1)[0])
        self.success_year_trend = np.random.normal(0, 0.01, 1)[0]
        self.results = []

    def __str__(self):
        return self.descibe()

    def describe(self, offset=0):
        spacer_0 = "\t" * offset
        spacer_1 = "\t" * (offset + 1)
        details = spacer_0
        details += "Student profile: {}\n".format(self.profile) + spacer_1
        details += "Student name: {} {}\n".format(self.firstname, self.lastname) + spacer_1
        details += "Student gender: {}\n".format(self.gender) + spacer_1
        details += "Student birthday: {}\n".format(self.dob) + spacer_1
        details += "Student success factor: {}\n".format(self.success_factor) + spacer_1
        details += "Student success variability: {}\n".format(self.success_variability) + spacer_1
        today = datetime.date.today()
        details += "Student age: {}\n".format(
            today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day)))
        return details


class Teacher(Person):
    """School staff class"""

    def __init__(self, firstname, lastname, dob, gender):
        today = datetime.date.today()
        super().__init__(firstname, lastname, dob, gender)
        self.profile = 'teacher'
        self.uid = re.sub('[- .]', 'x', lastname[0:3].lower()) + firstname[0:1].lower() + str(dob.day).zfill(2) + str(
            dob.month).zfill(2)
        self.uid = unidecode.unidecode(self.uid)  # Remove accents
        self.experience = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)) - 23 + random.randint(-5, 0)
        self.success_factor = np.random.normal(self.experience / 3000, 0.005, 1)[0]
        self.success_variability = 0.005
        self.workload = 0

    def __str__(self):
        return self.describe()

    def describe(self, offset=0):
        spacer_0 = "\t" * offset
        spacer_1 = "\t" * (offset + 1)
        details = spacer_0
        details += "Teacher profile: {}\n".format(self.profile) + spacer_1
        details += "Teacher name: {} {}\n".format(self.firstname, self.lastname) + spacer_1
        details += "Teacher gender: {}\n".format(self.gender) + spacer_1
        details += "Teacher birthday: {}\n".format(self.dob) + spacer_1
        today = datetime.date.today()
        details += "Teacher age: {}\n".format(
            today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))) + spacer_1
        details += "Teacher experience: {}\n".format(self.experience) + spacer_1
        details += "Teacher success factor: {}\n".format(self.success_factor)
        return details


class Specialist(Teacher):

    def __init__(self, firstname, lastname, dob, gender, topic):
        super().__init__(firstname, lastname, dob, gender)
        today = datetime.date.today()
        self.profile = 'specialist'
        self.topic = topic
        self.workload = 0


class Pool(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def __replenish_pool(self):
        raise NotImplementedError

    @abstractmethod
    def pop(self):
        raise NotImplementedError


class SpecialistPool(Pool):

    def __replenish_pool(self):
        pool = []
        for idx in range(0, 20):
            pool.append(Specialist())
        return pool


class TeacherPool(Pool):
    db = None

    def __init__(self):
        super(Pool, self).__init__()
        self.pool = []
        self.db = Database()

    def _Pool__replenish_pool(self):
        # logger.info("Replenishing teacher pool")

        def age_to_date(age):
            (d, i) = math.modf(age)
            age = int(i)
            if not (23 <= age <= 67):  # enforcing age bounds
                if age < 23:
                    age = age + (23 - age)
                else:
                    age = age - (age - 67)
            days = int(365 * d)
            today = datetime.datetime.today()
            birthyear = today.year - age
            dob = datetime.datetime(birthyear, 1, 1) + datetime.timedelta(days=days)
            if (today.month, today.day) < (dob.month, dob.day):
                try:
                    dob = dob.replace(year=dob.year - 1)
                except:
                    # In the case of bisextile year
                    logger.error("Date out of bound: {}".format(dob))
                    dob = dob.replace(day=28)
                    dob = dob.replace(year=dob.year - 1)
            return dob

        # Set simulation parameters
        pool_size = 30
        gender_f_pct = 0.85
        age_mean = 45
        age_stddev = 10

        cxn = self.db.connect_db()

        # logger.info("Getting female teacher firstnames from database")
        # noinspection SqlResolve
        qry = '''SELECT firstname, gender, occurrences FROM firstnames WHERE year = 1980 AND gender = 'f' AND occurrences > 10'''
        sql_query = pd.read_sql_query(qry, cxn)
        df_firstname_f_sql = pd.DataFrame(sql_query, columns=['firstname', 'gender', 'occurrences'])

        # logger.info("Getting male teacher firstnames from database")
        # noinspection SqlResolve
        qry = '''SELECT firstname, gender, occurrences FROM firstnames WHERE year = 1980 AND gender = 'm' AND occurrences > 10'''
        sql_query = pd.read_sql_query(qry, cxn)
        df_firstname_m_sql = pd.DataFrame(sql_query, columns=['firstname', 'gender', 'occurrences'])

        # logger.info("Getting teacher lastnames from database")
        # noinspection SqlResolve
        qry = '''SELECT lastname, occurrences FROM `lastnames-qc5000-base`'''
        sql_query = pd.read_sql_query(qry, cxn)
        df_lastname_sql = pd.DataFrame(sql_query, columns=['lastname', 'occurrences'])

        # Simulate staff
        # logger.info("Creating teacher dob pool array")
        s_age = np.random.normal(age_mean, age_stddev, pool_size)
        s_dob = np.array(list(map(age_to_date, s_age)))

        # logger.info("Creating teacher gender pool array")
        s_gender_binomial = np.random.binomial(1, gender_f_pct, pool_size)
        s_gender = np.where(s_gender_binomial == 1, 'f', 'm')

        # logger.info("Creating teacher lastname pool array")
        df_lastname = df_lastname_sql.sample(n=pool_size, replace=True, weights='occurrences', ignore_index=True)
        s_lastname = df_lastname['lastname'].to_numpy()

        # logger.info("Creating teacher firstname pool array")
        df_firstname_m = df_firstname_m_sql.sample(n=pool_size, replace=True, weights='occurrences', ignore_index=False)
        df_firstname_f = df_firstname_f_sql.sample(n=pool_size, replace=True, weights='occurrences', ignore_index=False)
        s_firstname_m = df_firstname_m['firstname'].to_numpy()
        s_firstname_f = df_firstname_f['firstname'].to_numpy()

        s_firstname = np.where(s_gender == 'f', s_firstname_f, s_firstname_m)

        np_people = list(zip(s_firstname, s_lastname, s_gender, s_dob))

        # logger.info("Creating teacher pool")
        for row in np_people:
            self.pool.append(Teacher(firstname=row[0], lastname=row[1], dob=row[3], gender=row[2]))

    def pop(self):
        if len(self.pool) == 0:
            self._Pool__replenish_pool()
        return self.pool.pop()


class StudentPool(Pool):
    db = None

    def __init__(self):
        super(Pool, self).__init__()
        self.pool = []
        self.db = Database()

    def _Pool__replenish_pool(self, age=None, pool_size=50, gender_f_pct=0.55):
        # logger.info("Replenishing student pool")

        cxn = self.db.connect_db()

        # logger.info("Getting female student firstnames from database")
        # noinspection SqlResolve
        qry = '''SELECT firstname, gender, occurrences FROM mdm.firstnames WHERE year = 1999 AND gender = 'f' AND occurrences > 10'''
        sql_query = pd.read_sql_query(qry, cxn)
        df_firstname_f_sql = pd.DataFrame(sql_query, columns=['firstname', 'gender', 'occurrences'])

        # logger.info("Getting male student firstnames from database")
        # noinspection SqlResolve
        qry = '''SELECT firstname, gender, occurrences FROM mdm.firstnames WHERE year = 1999 AND gender = 'm' AND occurrences > 10'''
        sql_query = pd.read_sql_query(qry, cxn)
        df_firstname_m_sql = pd.DataFrame(sql_query, columns=['firstname', 'gender', 'occurrences'])

        # logger.info("Getting student lastnames from database")
        # noinspection SqlResolve
        qry = '''SELECT lastname, occurrences FROM mdm.`lastnames-qc5000-base`'''
        sql_query = pd.read_sql_query(qry, cxn)
        df_lastname_sql = pd.DataFrame(sql_query, columns=['lastname', 'occurrences'])

        # Simulate staff
        # logger.info("Creating student dob pool array with age in 6th grade")
        start_date = datetime.date(2009, 10, 1)
        end_date = datetime.date(2010, 9, 30)
        days_span = (end_date - start_date).days

        def to_dob(days_offset):
            return start_date + datetime.timedelta(days=days_offset)

        s_dob = random.sample(range(0, days_span), 30)
        s_dob = list(map(to_dob, s_dob))

        # logger.info("Creating student gender pool array")
        s_gender_binomial = np.random.binomial(1, gender_f_pct, pool_size)
        s_gender = np.where(s_gender_binomial == 1, 'f', 'm')

        # logger.info("Creating student lastname pool array")
        df_lastname = df_lastname_sql.sample(n=pool_size, replace=True, weights='occurrences', ignore_index=True)
        s_lastname = df_lastname['lastname'].to_numpy()

        # logger.info("Creating student firstname pool array")
        df_firstname_m = df_firstname_m_sql.sample(n=pool_size, replace=True, weights='occurrences', ignore_index=False)
        df_firstname_f = df_firstname_f_sql.sample(n=pool_size, replace=True, weights='occurrences', ignore_index=False)
        s_firstname_m = df_firstname_m['firstname'].to_numpy()
        s_firstname_f = df_firstname_f['firstname'].to_numpy()

        s_firstname = np.where(s_gender == 'f', s_firstname_f, s_firstname_m)

        np_people = list(zip(s_firstname, s_lastname, s_gender, s_dob))

        # logger.info("Creating student pool")
        for (firsname, lastname, gender, dob) in np_people:
            self.pool.append(Student(firstname=firsname, lastname=lastname, dob=dob, gender=gender))

    def pop(self):
        if len(self.pool) == 0:
            self._Pool__replenish_pool()
        return self.pool.pop()
