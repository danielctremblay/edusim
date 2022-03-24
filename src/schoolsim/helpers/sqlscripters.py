import logging

FORMATTER = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMATTER, level=logging.INFO)
logger = logging.getLogger(__name__)


class SqliteScripter(object):
    """Définit les scripts SQL pour sqlite.

    """

    def __init__(self):
        """Initialise la classe.

        """
        logger.info("Database, instantiating sqlite scripter")

    ddl = {
        "d_dates": '''CREATE TABLE d_dates
                        (
                            id         INTEGER NOT NULL
                                CONSTRAINT dates_pk
                                    PRIMARY KEY AUTOINCREMENT,
                            date     INTEGER NOT NULL,
                            year     INTEGER NOT NULL,
                            month     INTEGER NOT NULL,
                            day     INTEGER NOT NULL,
                            weekday     INTEGER NOT NULL,
                            school_year TEXT NOT NULL,
                            schedule_day   INTEGER NOT NULL,
                            schedule_week   INTEGER NOT NULL
                        );''',
        "d_evaluations": '''CREATE TABLE d_evaluations
                        (
                            
                            id         INTEGER NOT NULL
                                CONSTRAINT evaluations_pk
                                    PRIMARY KEY AUTOINCREMENT,
                            type     TEXT NOT NULL,
                            duration     TEXT NOT NULL,
                            isRetake     INTEGER NOT NULL
                        );''',
        "d_groups": '''CREATE TABLE d_groups
                        (
                            id         INTEGER NOT NULL
                                CONSTRAINT groups_pk
                                    PRIMARY KEY AUTOINCREMENT,
                            group_id     INTEGER NOT NULL,
                            css_id     INTEGER NOT NULL,
                            css_name     TEXT NOT NULL,
                            school_id      INTEGER NOT NULL,
                            school_name      INTEGER NOT NULL,
                            school_milieu   TEXT NOT NULL,
                            school_year TEXT NOT NULL,
                            grade   INTEGER NOT NULL, 
                            group_size      INTEGER NOT NULL,
                            enrolment  INTEGER NOT NULL
                        );
                        CREATE UNIQUE INDEX d_groups_css_id_school_id_group_id_uindex
                            ON d_groups (css_id, school_id, group_id, school_year);''',
        "d_students": '''CREATE TABLE d_students
                        (
                            id              INTEGER NOT NULL
                                CONSTRAINT students_pk
                                    PRIMARY KEY AUTOINCREMENT,
                            uid TEXT    NOT NULL,
                            email TEXT    NOT NULL,
                            firstname       TEXT    NOT NULL,
                            lastname        TEXT    NOT NULL,
                            dob             TEXT    NOT NULL,
                            gender          TEXT    NOT NULL,
                            "status"        TEXT    NOT NULL
                        );
                        CREATE UNIQUE INDEX d_students_uid_uindex
                            ON d_students (uid);''',
        "d_teachers": '''CREATE TABLE d_teachers
                        (
                            id              INTEGER NOT NULL
                                CONSTRAINT teachers_pk
                                    PRIMARY KEY AUTOINCREMENT,
                            uid TEXT    NOT NULL,
                            email     TEXT NOT NULL,
                            firstname       TEXT    NOT NULL,
                            lastname        TEXT    NOT NULL,
                            dob             TEXT    NOT NULL,
                            gender          TEXT    NOT NULL 
                        );
                        CREATE UNIQUE INDEX d_teachers_uid_uindex
                            ON d_teachers (uid);''',
        "d_topics": '''CREATE TABLE d_topics
                        (
                            id         INTEGER NOT NULL
                                CONSTRAINT topics_pk
                                    PRIMARY KEY AUTOINCREMENT,
                            topic_id TEXT NOT NULL,
                            name     TEXT NOT NULL,
                            isSpeciality      INTEGER NOT NULL
                        );
                        CREATE UNIQUE INDEX d_topics_topic_isSpeciality_uindex
                            ON d_topics (topic_id, name, isSpeciality);''',
        "f_results": '''CREATE TABLE f_results
                        (
                            fk_dates       INTEGER NOT NULL
                                REFERENCES d_dates,
                            fk_evaluations INTEGER NOT NULL
                                REFERENCES d_evaluations,
                            fk_groups      INTEGER NOT NULL
                                REFERENCES d_groups,
                            fk_students    INTEGER NOT NULL
                                REFERENCES d_students,
                            fk_teachers    INTEGER NOT NULL
                                REFERENCES d_teachers,
                            fk_topics      INTEGER NOT NULL
                                REFERENCES d_topics,
                            evaluation_type    TEXT,
                            evaluation_value   TEXT,
                            evaluation_score   DOUBLE,
                            evaluation_total   DOUBLE,
                            evaluation_pct     DOUBLE  NOT NULL,
                            evaluation_weight  DOUBLE NOT NULL,
                            comments       TEXT
                        );''',
        "s_results": '''CREATE TABLE s_results
                        (
                            css_id          INTEGER NOT NULL,
                            school_id       INTEGER NOT NULL,
                            school_year     TEXT NOT NULL,
                            group_id        INTEGER NOT NULL,
                            student_uid     TEXT NOT NULL,
                            teacher_uid     TEXT NOT NULL,
                            topic_id        INTEGER NOT NULL,
                            evaluation_id   INTEGER NOT NULL,
                            evaluation_type    TEXT NOT NULL,
                            evaluation_date    TEXT  NOT NULL,
                            evaluation_score  FLOAT  NOT NULL,
                            evaluation_total  INTEGER NOT NULL,
                            evaluation_pct  FLOAT NOT NULL,
                            evaluation_weight  FLOAT NOT NULL,
                            evaluation_duration  INTEGER NOT NULL,
                            isRetake  INTEGER NOT NULL,
                            comments        TEXT NULL
                        );'''
    }

    dml = {
        "insert_dates": '''INSERT OR IGNORE INTO
            d_dates ("date", "year", "month", "day", weekday, school_year, schedule_day, schedule_week)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);''',
        "insert_groups": '''INSERT OR IGNORE INTO
            d_groups (group_id, css_id, css_name, school_id, school_name, school_milieu, school_year, grade, group_size, enrolment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
        "insert_students": '''INSERT OR IGNORE INTO
            d_students (uid, email, firstname, lastname, dob, gender, "status")
                VALUES (?, ?, ?, ?, ?, ?, ?);''',
        "insert_teachers": '''INSERT OR IGNORE INTO
            d_teachers (uid, email, firstname, lastname, dob, gender)
                VALUES (?, ?, ?, ?, ?, ?);''',
        "insert_topics": '''INSERT OR IGNORE INTO
            d_topics (topic_id, name, isSpeciality)
                VALUES (?, ?, ?);''',
        "insert_s_results": '''INSERT INTO
            s_results (css_id, school_id, school_year, group_id, student_uid, topic_id, teacher_uid, evaluation_id, evaluation_type, evaluation_date, evaluation_score, evaluation_total, evaluation_pct, evaluation_weight, evaluation_duration, isRetake)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
        "insert_into_d_evaluations": '''INSERT INTO d_evaluations (type, duration, isRetake) 
                SELECT DISTINCT evaluation_type, evaluation_duration, isRetake FROM s_results ORDER BY evaluation_type, evaluation_duration, isRetake;''',
        "insert_into_f_results": '''INSERT INTO
                        f_results (fk_dates, fk_evaluations, fk_groups, fk_students, fk_teachers, fk_topics, evaluation_type, evaluation_value, evaluation_score, evaluation_total, evaluation_pct, evaluation_weight)
                    SELECT
                        d_dates.id, d_evaluations.id, d_groups.id, d_students.id, d_teachers.id, d_topics.id, 'quantitative', 'NA', evaluation_score,
                        evaluation_total, evaluation_pct, evaluation_weight
                    FROM
                        s_results,
                        d_dates,
                        d_evaluations,
                        d_groups,
                        d_students,
                        d_teachers,
                        d_topics
                    WHERE
                          s_results.evaluation_date = d_dates.date
                      AND s_results.evaluation_type = d_evaluations.type AND s_results.evaluation_duration = d_evaluations.duration AND s_results.isRetake = d_evaluations.isRetake
                      AND s_results.css_id = d_groups.css_id AND s_results.school_id = d_groups.school_id AND s_results.school_year = d_groups.school_year AND s_results.group_id = d_groups.group_id
                      AND s_results.student_uid = d_students.uid
                      AND s_results.teacher_uid = d_teachers.uid
                      AND s_results.topic_id = d_topics.topic_id;'''
    }
