import xlsxwriter
from pathlib import Path

from .helpers.database import Database


def create_spreadsheets(db_filepath, output_path):
    db = Database(db_filepath)
    cnx = db.connect_db()

    cursor = cnx.cursor()

    result_qry = '''SELECT
                    dg.grade AS 'Niveau',
                    dg.group_id AS 'Groupe',
                    d.name AS 'Matière',
                    dd.date AS "Date de l'évaluation",
                    de.type AS "Type d'évaluation",
                    de.duration AS "Durée de l'évaluation",
                    dt.firstname AS "Prénom de l'enseignant",
                    dt.lastname AS "Nom de famille de l'enseignant",
                    ds.firstname AS "Prénom de l'étudiant",
                    ds.lastname AS "Nom de l'étudiant",
                    evaluation_score AS "Résultat",
                    evaluation_total AS "Total",
                    evaluation_pct AS "Pourcentage",
                    evaluation_weight AS "Poids de l'évaluation"
                FROM
                    f_results
                        LEFT JOIN d_groups dg ON dg.id = f_results.fk_groups
                        LEFT JOIN d_teachers dt ON dt.id = f_results.fk_teachers
                        LEFT JOIN d_students ds ON ds.id = f_results.fk_students
                        LEFT JOIN d_topics d ON d.id = f_results.fk_topics
                        LEFT JOIN d_dates dd ON dd.id = f_results.fk_dates
                        LEFT JOIN d_evaluations de ON de.id = f_results.fk_evaluations
                WHERE
                      dd.school_year = '2021-2022'  AND dd.date < '2022-01-15'
                ORDER BY
                    dg.grade,
                    dg.group_id,
                    d.name,
                    dd.date,
                    ds.lastname, 
                    ds.firstname;'''

    cursor.execute(result_qry)
    rs = cursor.fetchall()
    print(len(rs))

    (grade_base, group_base, topic_base, eval_date_base, evaluation_base, student_fn_base, student_ln_base) = [None] * 7

    workbook = None
    worksheet = None
    row_idx = 0

    for record in rs:
        (grade, group, topic, eval_date, evaluation, duration, teacher_fn, teacher_ln, student_fn, student_ln, score,
         total, pct, weight) = record

        if grade_base != grade or group_base != group:
            # Close previous workbook
            try:
                workbook.close()
                workbook = None
                worksheet = None
                row_idx = 0
            except:
                # No workbook open
                pass
            # Create new workbook
            workbook_filepath = Path(output_path).joinpath("resultats-niveau{}-groupe{}.xlsx".format(grade, group))
            workbook = xlsxwriter.Workbook(workbook_filepath)

        if topic_base != topic:
            # create a new sheet
            sheet_name = topic.split(" ")[0]
            worksheet = workbook.add_worksheet("{}".format(sheet_name))
            row_idx = 0

        col_idx = 0
        for item in [grade, group, topic, eval_date, evaluation, duration, teacher_fn, teacher_ln, student_fn,
                     student_ln, score, total, pct, weight]:
            worksheet.write(row_idx, col_idx, item)
            col_idx += 1
        row_idx += 1

        (grade_base, group_base, topic_base, eval_date_base, evaluation_base, student_fn_base, student_ln_base) = (
            grade, group, topic, eval_date, evaluation, student_fn, student_ln)

    try:
        workbook.close()
    except:
        pass
