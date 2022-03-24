import sqlite3
import time
import traceback

from sqlalchemy import create_engine
import logging

from . sqlscripters import SqliteScripter

logger = logging.getLogger(__name__)


class Database(object):
    """Définit un objet représentant la base de données (singleton).

    """
    cxn = None

    def __init__(self):
        """Initialise le singleton.

        """
        # logger.info("Database, instantiating database handler")
        pass

    def connect_db(self):
        """Retourne la connexion à la base de données.

        :return: la connexion à la base de données.
        """
        # logger.info("Database, getting database connexion")
        if self.cxn is not None:
            return self.cxn

        cxn_str = "mysql+pymysql://daniel:soleil@localhost:3306/mdm"
        self.cxn = create_engine(cxn_str)
        # mysql.connector.connect(
        #     host="localhost",
        #     port="3306",
        #     user="daniel",
        #     password="soleil",
        #     database="mdm"
        # )
        return self.cxn


class DatabaseWriter(object):
    """Définit l'interface de génération de la base de données décisionnelle issue du système scolaire.

    """

    def __init__(self, db_filepath, system, model_type='olap'):
        """Initialise l'interface de génération de la base de données décisionnelle issue du système scolaire.

        :param db_filepath: le chemin vers la base de données sqlite.
        :param system: le système scolaire.
        :param model_type: le type de modèle de données, seul olap est pris en charge présentement.
        """
        logger.info("Database, writing to database {}".format(db_filepath))
        if model_type == 'olap':
            self.__save_to_olap(db_filepath, system)
        else:
            raise NotImplementedError

    def __save_to_olap(self, db, system):
        logger.info("Saving simulation data to database")
        start_time = time.time()

        # Create database
        scripter = SqliteScripter()
        cxn = sqlite3.connect(db)

        # Create tables
        for key in sorted(scripter.ddl.keys()):
            for stmt in scripter.ddl[key].split(";"):
                cxn.execute(stmt)
                cxn.commit()

        # Fill database
        # Hierarchy css -> school -> school year -> group
        # -> topics -> teachers
        # -> students -> results
        for css in system.get_csss():
            logger.info("Database, processing css {}".format(css.id))
            css_id = css.id
            css_name = css.name
            for calendar in css.get_calendars():
                try:
                    logger.debug("Database, processing calendar dates")
                    values_date = []
                    for school_day in calendar.get_schooldays():
                        school_date = school_day.get_date()
                        values_date.append(
                            (school_date, school_date.year, school_date.month,
                             school_date.day, school_date.weekday(), calendar.school_year,
                             school_day.get_school_day(), school_day.get_school_week()))
                    cursor = cxn.cursor()
                    stmt = scripter.dml["insert_dates"]
                    cursor.executemany(stmt, values_date)
                    cxn.commit()
                except:
                    logger.error("Database, could not insert dates")
                finally:
                    cursor.close()
                    logger.debug("Database, inserted {} calendar dates to database".format(len(values_date)))

            for school in css.get_schools():
                logger.info("Database, processing school {}".format(school.id))
                school_id = school.id
                school_name = school.name
                school_milieu = school.milieu
                for school_year in school.get_schoolyears():
                    logger.info("Database, processing school year {}".format(school_year.school_year))
                    school_year_name = school_year.school_year
                    try:
                        logger.info("Database, processing groups")
                        values_groups = []
                        for group in school_year.get_groups():
                            values_groups.append((group.id, css_id, css_name, school_id, school_name, school_milieu,
                                                  school_year_name, group.grade, group.size, group.enrolment))
                        cursor = cxn.cursor()
                        stmt = scripter.dml["insert_groups"]
                        cursor.executemany(stmt, values_groups)
                        cxn.commit()
                    except:
                        logger.error("Database, could not insert groups")
                    finally:
                        cursor.close()
                        logger.info("Database, inserted {} groups to database".format(len(values_groups)))

                    for group in school_year.get_groups():
                        try:
                            logger.debug("Database, processing topics and teachers")
                            values_teachers = []
                            values_topics = []
                            for topic in group.get_topics():
                                teacher = topic.get_staff()
                                try:
                                    values_teachers.append((teacher.uid, teacher.uid + "@css.qc.ca", teacher.firstname,
                                                            teacher.lastname, teacher.dob, teacher.gender))
                                    values_topics.append((topic.id, topic.name, topic.isSpeciality))
                                except:
                                    logger.error("Database, could not insert teacher or topic to list")
                            cursor = cxn.cursor()
                            stmt = scripter.dml["insert_teachers"]
                            cursor.executemany(stmt, values_teachers)
                            cxn.commit()
                            logger.debug("Database, inserted {} teachers to database".format(len(values_teachers)))
                            stmt = scripter.dml["insert_topics"]
                            cursor.executemany(stmt, values_topics)
                            cxn.commit()
                            logger.debug("Database, inserted {} topics to database".format(len(values_topics)))
                        except:
                            logger.error("Database, could not insert teacher or topic to database")
                        finally:
                            cursor.close()

                        try:
                            logger.info("Database, processing students and results")
                            values_students = []
                            values_results = []
                            for student in group.get_students():
                                try:
                                    values_students.append(
                                        (student.uid, student.uid + "@css.qc.ca", student.firstname, student.lastname,
                                         student.dob, student.gender, student.status))
                                    context = (css_id, school_id, school_year.school_year, group.id, student.uid)
                                    for result in student.results:
                                        # (topic_id, evaluation_id, evaluation_type, evaluation_date, evaluation_score,
                                        #  evaluation_total, evaluation_pct, evaluation_weight, evaluation_duration,
                                        #  evaluation_is_retake) = result
                                        values_results.append(context + result)
                                except:
                                    logger.error("Database, could not insert student in list")
                            cursor = cxn.cursor()
                            stmt = scripter.dml["insert_students"]
                            cursor.executemany(stmt, values_students)
                            cxn.commit()
                            stmt = scripter.dml["insert_s_results"]
                            cursor.executemany(stmt, values_results)
                            cxn.commit()
                        except:
                            traceback.print_exc()
                            logger.error("Database, could not insert students or results in database")
                        finally:
                            cursor.close()
                            logger.info("Database, inserted {} student to database".format(len(values_students)))
                            logger.info("Database, inserted {} results to database".format(len(values_results)))
        try:
            cursor = cxn.cursor()
            stmt = scripter.dml["insert_into_d_evaluations"]
            cursor.execute(stmt)
            cxn.commit()
            stmt = scripter.dml["insert_into_f_results"]
            cursor.execute(stmt)
            cxn.commit()
            stmt = scripter.dml["drop_s_results"]  # drop staging table
            cursor.execute(stmt)
            cxn.commit()
            cursor.close()
        except:
            logger.error("Could not load d_evaluations")
        finally:
            cursor.close()
            cxn.close()

        logger.info("Database created in {} sec.".format(time.time() - start_time))
