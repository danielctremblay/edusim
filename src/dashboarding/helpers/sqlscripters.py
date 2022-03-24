import logging

FORMATTER = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMATTER, level=logging.INFO)
logger = logging.getLogger(__name__)


class SqliteScripter(object):

    def __init__(self):
        logger.info("Scripter, instantiating sqlite database scripter")

    dql = {
        "select_institution": '''SELECT DISTINCT school_name, css_name FROM d_groups;''',
        "select_period": '''SELECT MIN(school_year), SUBSTR(MIN(school_year), 1, 4), MAX(school_year), SUBSTR(MAX(school_year), 1, 4)
                            FROM
                                d_dates;''',
        "select_institution_headcount": '''SELECT COUNT(DISTINCT fk_students)
                                            FROM
                                                f_results
                                                    LEFT JOIN d_dates dd ON dd.id = f_results.fk_dates
                                            WHERE
                                                dd.school_year = ?;''',
        "select_grade_headcount": '''SELECT dg.grade, COUNT(DISTINCT fk_students)
                                        FROM
                                            f_results
                                                LEFT JOIN d_dates dd ON dd.id = f_results.fk_dates
                                                LEFT JOIN d_groups dg ON dg.id = f_results.fk_groups
                                        WHERE
                                            dg.grade = ? AND
                                            dd.school_year = ?;''',
        "select_topic_headcount": '''SELECT dt.name, COUNT(DISTINCT fk_students)
                                        FROM
                                            f_results
                                                LEFT JOIN d_dates dd ON dd.id = f_results.fk_dates
                                                LEFT JOIN d_topics dt ON dt.id = f_results.fk_topics
                                        WHERE
                                            dt.name = ? AND
                                            dd.school_year = ?;''',
        "select_topic_grade_headcount": '''SELECT dt.name AS topic, CASE
                                        WHEN grade IN (1, 2) THEN 1
                                        WHEN grade IN (3, 4) THEN 2
                                        ELSE 3
                                        END AS cycle, dg.grade, COUNT(DISTINCT fk_students) AS hc
                                        FROM
                                            f_results
                                                LEFT JOIN d_dates dd ON dd.id = f_results.fk_dates
                                                LEFT JOIN d_topics dt ON dt.id = f_results.fk_topics
                                                LEFT JOIN d_groups dg ON dg.id = f_results.fk_groups
                                        WHERE
                                            dd.school_year = ?
                                        GROUP BY
                                            dt.name, cycle, dg.grade;''',
        "select_gender_pct": '''WITH
                                    cte_male AS
                                        (SELECT COUNT(DISTINCT fk_students) AS cnt_m
                                         FROM
                                             f_results
                                                 JOIN d_dates dd ON f_results.fk_dates = dd.id
                                                 JOIN d_students ds ON f_results.fk_students = ds.id
                                         WHERE
                                               dd.school_year = ?
                                           AND ds.gender = 'm'),
                                    cte_total AS
                                        (SELECT COUNT(DISTINCT fk_students) AS cnt_t
                                         FROM
                                             f_results
                                                 JOIN d_dates dd ON f_results.fk_dates = dd.id
                                                 JOIN d_students ds ON f_results.fk_students = ds.id
                                         WHERE
                                             dd.school_year = ?)
                                SELECT cnt_m * 100 / cnt_t AS pct_m, 100 - (cnt_m * 100 / cnt_t) AS pct_f
                                FROM
                                    cte_male,
                                    cte_total;''',
        "select_progress_overall": '''SELECT dd.school_year, SUM(evaluation_score) / SUM(evaluation_total) * 100.0 AS 'moyenne'
                                    FROM
                                        f_results
                                            LEFT JOIN d_dates dd ON f_results.fk_dates = dd.id
                                            LEFT JOIN d_students ds ON ds.id = f_results.fk_students
                                    GROUP BY
                                        dd.school_year
                                    ORDER BY
                                        dd.school_year;''',
        "select_progress_gender": '''SELECT dd.school_year, ds.gender, SUM(evaluation_score) / SUM(evaluation_total) * 100.0 AS 'moyenne'
                                    FROM
                                        f_results
                                            LEFT JOIN d_dates dd ON f_results.fk_dates = dd.id
                                            LEFT JOIN d_students ds ON ds.id = f_results.fk_students
                                    GROUP BY
                                        dd.school_year, ds.gender
                                    ORDER BY
                                        dd.school_year;''',
        "select_progress_grade": '''SELECT dd.school_year, SUM(evaluation_score) / SUM(evaluation_total) * 100.0 AS 'moyenne'
                                    FROM
                                        f_results
                                            LEFT JOIN d_dates dd ON f_results.fk_dates = dd.id
                                            LEFT JOIN d_groups dg ON f_results.fk_groups = dg.id
                                    WHERE
                                        dg.grade = ?
                                    GROUP BY
                                        dd.school_year
                                    ORDER BY
                                        dd.school_year;''',
        "select_failure_grade": '''WITH
                                        cte_moyenne AS (SELECT dd.school_year, ds.uid, SUM(evaluation_score) / SUM(evaluation_total) * 100.0 AS 'moyenne'
                                                        FROM
                                                            f_results
                                                                LEFT JOIN d_dates dd ON f_results.fk_dates = dd.id
                                                                LEFT JOIN d_groups dg ON f_results.fk_groups = dg.id
                                                                LEFT JOIN d_students ds ON f_results.fk_students = ds.id
                                                        WHERE
                                                            grade = ?
                                                        GROUP BY dd.school_year, ds.uid
                                                        HAVING
                                                            moyenne < 60
                                                        ORDER BY dd.school_year)
                                    SELECT school_year, COUNT(moyenne)
                                    FROM
                                        cte_moyenne
                                    GROUP BY
                                        school_year
                                    ORDER BY
                                        school_year;''',
        "select_topic_list": '''SELECT DISTINCT name
                                FROM
                                    d_topics
                                ORDER BY
                                    topic_id;''',
        "select_progress_topic": '''SELECT dd.school_year, SUM(evaluation_score) / SUM(evaluation_total) * 100.0 AS 'moyenne'
                                        FROM
                                            f_results
                                                LEFT JOIN d_dates dd ON f_results.fk_dates = dd.id
                                                LEFT JOIN d_topics dt ON f_results.fk_topics = dt.id
                                        WHERE
                                            dt.name = ?
                                        GROUP BY
                                            dd.school_year
                                        ORDER BY
                                            dd.school_year;''',
        "select_failure_topic": '''WITH
                                        cte_moyenne AS (SELECT dd.school_year, ds.uid, SUM(evaluation_score) / SUM(evaluation_total) * 100.0 AS 'moyenne'
                                                        FROM
                                                            f_results
                                                                LEFT JOIN d_dates dd ON f_results.fk_dates = dd.id
                                                                LEFT JOIN d_topics dt ON f_results.fk_topics = dt.id
                                                                LEFT JOIN d_students ds ON f_results.fk_students = ds.id
                                                        WHERE
                                                            dt.name = ?
                                                        GROUP BY dd.school_year, ds.uid
                                                        HAVING
                                                            moyenne < 60
                                                        ORDER BY dd.school_year)
                                    SELECT school_year, COUNT(moyenne)
                                    FROM
                                        cte_moyenne
                                    GROUP BY
                                        school_year
                                    ORDER BY
                                        school_year;''',
        "select_failure_topic_grade": '''WITH
                                    cte_moyenne AS (SELECT
                                                        dd.school_year, dt.name AS topic, dg.grade, ds.uid,
                                                        SUM(evaluation_score) / SUM(evaluation_total) * 100.0 AS 'moyenne'
                                                    FROM
                                                        f_results
                                                            LEFT JOIN d_dates dd ON f_results.fk_dates = dd.id
                                                            LEFT JOIN d_groups dg ON f_results.fk_groups = dg.id
                                                            LEFT JOIN d_students ds ON f_results.fk_students = ds.id
                                                            LEFT JOIN d_topics dt ON dt.id = f_results.fk_topics
                                                    WHERE
                                                        dd.school_year = ?
                                                    GROUP BY dd.school_year, dt.name, dg.grade, ds.uid
                                                    HAVING
                                                        moyenne < 60
                                    )
                                SELECT
                                    topic, grade,
                                    CASE
                                        WHEN grade IN (1, 2) THEN 1
                                        WHEN grade IN (3, 4) THEN 2
                                        ELSE 3
                                        END AS cycle, COUNT(moyenne) AS fc 
                                FROM
                                    cte_moyenne
                                GROUP BY
                                    school_year, grade, topic
                                ORDER BY
                                    school_year;''',
        "select_failure_topic_grade_gender": '''WITH
                                        cte_moyenne AS (SELECT
                                                            dd.school_year, dt.name AS topic, dg.grade, ds.uid, ds.gender,
                                                            SUM(evaluation_score) / SUM(evaluation_total) * 100.0 AS 'moyenne'
                                                        FROM
                                                            f_results
                                                                LEFT JOIN d_dates dd ON f_results.fk_dates = dd.id
                                                                LEFT JOIN d_groups dg ON f_results.fk_groups = dg.id
                                                                LEFT JOIN d_students ds ON f_results.fk_students = ds.id
                                                                LEFT JOIN d_topics dt ON dt.id = f_results.fk_topics
                                                        WHERE
                                                            dd.school_year = ?
                                                        GROUP BY dd.school_year, dt.name, dg.grade, ds.uid
                                                        HAVING
                                                            moyenne < 60
                                        )
                                    SELECT
                                        topic, grade, gender,
                                        CASE
                                            WHEN grade IN (1, 2) THEN 1
                                            WHEN grade IN (3, 4) THEN 2
                                            ELSE 3
                                            END AS cycle, COUNT(moyenne) AS fc 
                                    FROM
                                        cte_moyenne
                                    WHERE
                                        gender = ?
                                    GROUP BY
                                        school_year, grade, topic, gender
                                    ORDER BY
                                        school_year;'''

    }
