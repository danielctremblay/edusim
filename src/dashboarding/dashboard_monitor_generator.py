import datetime
import logging

from bokeh.colors import RGB
from bokeh.embed import file_html
from bokeh.models import Div, Column, Row, Legend, LegendItem
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.util.browser import view
from jinja2 import Template

from . helpers.htmlscripters import HtmlScripter
from . helpers.sqlscripters import SqliteScripter
from . helpers.database import Database

FORMATTER = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMATTER, level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_figure():
    fig = figure()
    fig.height = 20
    fig.width = 200
    fig.axis.visible = False
    fig.grid.visible = False
    fig.border_fill_color = None
    fig.outline_line_color = None
    fig.min_border = 0
    fig.toolbar.logo = None
    fig.toolbar_location = None
    return fig

def setup_bulletgraph(score, target, limits=[0, 60, 80, 100]):
    ds_colors = [RGB(239, 239, 239), RGB(187, 187, 187), RGB(153, 153, 153)]
    bulletgraph = setup_figure()
    bulletgraph.x_range.range_padding = 0
    bulletgraph.grid.grid_line_color = None
    bulletgraph.xaxis[0].ticker.num_minor_ticks = 0
    bulletgraph.margin = (0, 20, 0, 0)
    for left, right, color in zip(limits[:-1], limits[1:], ds_colors[::-1]):
        bulletgraph.hbar(y=[""], left=left, right=right, height=1, color=color)
        bulletgraph.hbar(y=[""], left=0, right=score, height=0.2, color="black")
        bulletgraph.segment(x0=[target], y0=[-0.5], x1=[target], y1=[0.5], color="black", line_width=1)
    return bulletgraph


def create_dashboard(db_filepath):
    # Setup data access
    db = Database(db_filepath)
    cnx = db.connect_db()
    scripter = SqliteScripter()
    cursor = cnx.cursor()

    # Data: school credentials
    cursor.execute(scripter.dql['select_institution'])
    rs = cursor.fetchall()
    (school_name, css_name) = rs[0]

    # Data: school year period
    cursor.execute(scripter.dql['select_period'])
    rs = cursor.fetchall()
    (school_year_min, year_min, school_year_max, year_max) = rs[0]

    # Data : topic list
    rs = cursor.execute(scripter.dql['select_topic_list'])
    topic_list = [topic[0] for topic in rs]

    # Data : school number of students
    cursor.execute(scripter.dql['select_institution_headcount'], (school_year_max,))
    rs = cursor.fetchall()
    (student_headcount,) = rs[0]

    # Data : school number of students by grade
    headcount_grade_dict = {}
    stmt = scripter.dql['select_grade_headcount']
    for grade in range(1, 7):
        cursor.execute(stmt, (grade, school_year_max))
        headcount_grade_dict[grade] = cursor.fetchall()

    # Data : school number of students by topic
    headcount_topic_dict = {}
    stmt = scripter.dql['select_topic_headcount']
    for topic in topic_list:
        cursor.execute(stmt, (topic,school_year_max))
        headcount_topic_dict[topic] = cursor.fetchall()

    # Data: gender division
    cursor.execute(scripter.dql['select_gender_pct'], (school_year_max, school_year_max))
    rs = cursor.fetchall()
    (pct_m, pct_f) = rs[0]

    # Data: year to year overall progress by gender
    cursor.execute(scripter.dql['select_progress_gender'])
    rs = cursor.fetchall()
    mean_m = [avg for (school_year, gender, avg) in rs if gender == "m"]
    mean_f = [avg for (school_year, gender, avg) in rs if gender == "f"]
    mean_sy = [int(school_year[0:4]) for (school_year, gender, avg) in rs if gender == "f"]

    cursor.execute(scripter.dql['select_progress_overall'])
    rs = cursor.fetchall()
    mean_all = [avg for (school_year, avg) in rs]

    # Data: year to year progress by grade
    progress_grade_dict = {}
    stmt = scripter.dql['select_progress_grade']
    for grade in range(1, 7):
        cursor.execute(stmt, (grade,))
        progress_grade_dict[grade] = cursor.fetchall()

    # Data: year to year failure by grade
    failure_grade_dict = {}
    stmt = scripter.dql['select_failure_grade']
    for grade in range(1, 7):
        cursor.execute(stmt, (grade,))
        failure_grade_dict[grade] = cursor.fetchall()

    # Data: year to year progress by topic
    progress_topic_dict = {}
    stmt = scripter.dql['select_progress_topic']
    for topic in topic_list:
        cursor.execute(stmt, (topic,))
        progress_topic_dict[topic] = cursor.fetchall()

    # Data: year to year failure by topic
    failure_topic_dict = {}
    stmt = scripter.dql['select_failure_topic']
    for topic in topic_list:
        cursor.execute(stmt, ("{}".format(topic),))
        failure_topic_dict[topic] = cursor.fetchall()

    cursor.close()
    cnx.close()

    htmlscripter = HtmlScripter()
    template = Template(htmlscripter.html['document'])

    # Setup dashboard parameters
    ds_width = 1024
    ds_colors = [RGB(239, 239, 239), RGB(187, 187, 187), RGB(153, 153, 153)]

    # Setup dashboard title
    div_title = Div(
        text="""<h1>Réussite scolaire {}<br>{} au {}</h1>""".format(school_year_max, school_name, css_name),
        style=htmlscripter.css['title'])
    div_title.sizing_mode = "scale_width"
    div_title.align = "center"

    # Setup header panorama
    div_headcount = Div(text="Nombre d'élèves<br>{}".format(student_headcount), style=htmlscripter.css['pano_featured'])
    div_gender_f = Div(text="Genre féminin<br>{}%".format(pct_f), style=htmlscripter.css['pano_featured'])
    div_gender_m = Div(text="Genre masculin<br>{}%".format(pct_m), style=htmlscripter.css['pano_featured'])
    div_gender_a = Div(text="Genre inclusif<br>{}%".format(0), style=htmlscripter.css['pano_featured'])

    # Setup overall progress
    fig_progress_overall = setup_figure()
    fig_progress_overall.title = "Moyennes globales par genre par année"
    fig_progress_overall.margin = (20, 0, 0, 40)
    fig_progress_overall.x_range.range_padding = 0
    fig_progress_overall.width = ds_width
    fig_progress_overall.height = 200
    fig_progress_overall.axis.visible = True
    fig_progress_overall.yaxis.bounds = (55, 85)
    fig_progress_overall.xaxis.minor_tick_line_color = None
    fig_progress_overall.yaxis.minor_tick_line_color = None
    r = fig_progress_overall.multi_line(xs=[mean_sy, mean_sy, mean_sy], ys=[mean_f, mean_m, mean_all],
                                        color=ds_colors[::-1],
                                        line_width=2)
    legend = Legend(items=[LegendItem(label="Genre féminin", renderers=[r], index=0),
                           LegendItem(label="Genre masculin", renderers=[r], index=1),
                           LegendItem(label="Moyenne globale", renderers=[r], index=2)])
    fig_progress_overall.add_layout(legend, 'right')
    pano_progress_overall = Row(fig_progress_overall)

    # Setup progress by grade panorama
    div_progress_grade_title = Div(text="Réussite des élèves par niveau en {}".format(school_year_max),
                                   style={"font-size": "125%"}, margin=(30, 0, 0, 0))
    div_progress_grade_title.min_width = 600
    rows_progress_grade = [Row(div_progress_grade_title),
                           Row(Div(text="Niveaux", style={"font-style": "italic"}, width=150),
                               Div(text="Tendance sur 7 ans", style={"font-style": "italic"}, width=120),
                               Div(text="", style={"font-style": "italic"}, width=50),
                               Div(text="Moy. actuelle", style={"font-style": "italic"}, width=80),
                               Div(text="Cible", style={"font-style": "italic"}))]
    for grade in sorted(progress_grade_dict.keys()):
        div_label = Div(text="{} année".format(grade))
        div_label.width = 150
        fig = setup_figure()
        data_x = [int(school_year[0:4]) for (school_year, avg) in progress_grade_dict[grade]]
        data_y = [avg for (school_year, avg) in progress_grade_dict[grade]]
        fig.line(x=data_x, y=data_y, line_color=ds_colors[2], line_width=2)
        fig2 = setup_figure()
        fig2.width = 30
        try:
            if data_y[-1] < data_y[-2] and data_y[-2] < data_y[-3]:
                alpha = 1
            elif data_y[-1] < data_y[-2]:
                alpha = 0
            else:
                alpha = 0
        except:
            alpha = 1
        fig2.circle([0], [0], size=10, color="red", alpha=alpha)
        div_value = Div(text="{:.2f} %".format(round(data_y[-1], 2)))
        bulletg = setup_bulletgraph(data_y[-1], 75-3+int(grade))
        rows_progress_grade.append(Row(div_label, fig, fig2, div_value, bulletg))

    # Setup failure by grade panorama
    div_failure_title = Div(text="Nombre d'élèves en situation d'échec par niveau en {}".format(school_year_max),
                            style={"font-size": "125%"}, margin=(30, 0, 0, 0))
    div_failure_title.min_width = 600
    rows_failure_grade = [Row(div_failure_title),
                          Row(Div(text="Niveaux", style={"font-style": "italic"}, width=150),
                              Div(text="Tendance sur 7 ans", style={"font-style": "italic"}, width=120),
                              Div(text="", style={"font-style": "italic"}, width=50),
                              Div(text="Nombre d'élèves", style={"font-style": "italic"}))]
    for grade in sorted(failure_grade_dict.keys()):
        div_label = (Div(text="{} année".format(grade)))
        div_label.width = 150
        fig = setup_figure()
        data_x = [int(school_year[0:4]) for (school_year, avg) in failure_grade_dict[grade]]
        data_y = [avg for (school_year, avg) in failure_grade_dict[grade]]
        data_hc = [cnt for (grade, cnt) in headcount_grade_dict[grade]]
        fig.line(x=data_x, y=data_y, line_color=ds_colors[2], line_width=2)
        fig2 = setup_figure()
        fig2.width = 30
        if data_y[-1] >= 5:
            alpha = 1
        elif data_y[-1] == 4:
            alpha = 0
        else:
            alpha = 0
        fig2.circle([0], [0], size=10, color="red", alpha=alpha)
        div_value = Div(text="{} /  {}".format(data_y[-1], data_hc[-1]))


        rows_failure_grade.append(Row(div_label, fig, fig2, div_value))

    # Setup progress by topic panorama
    div_progress_topic_title = Div(text="Réussite des élèves par matière en {}".format(school_year_max),
                                   style={"font-size": "125%"}, margin=(30, 0, 0, 0))
    div_progress_topic_title.min_width = 600
    rows_progress_topic = [Row(div_progress_topic_title),
                           Row(Div(text="Matière", style={"font-style": "italic"}, width=150),
                               Div(text="Tendance sur 7 ans", style={"font-style": "italic"}, width=120),
                               Div(text="", style={"font-style": "italic"}, width=50),
                               Div(text="Moy. actuelle", style={"font-style": "italic"}, width=80),
                               Div(text="Cible", style={"font-style": "italic"}))]
    target_topic={
        "Français": 75,
        "Mathématiques": 65,
        "Éducation physique": 85,
        "Anglais langue seconde": 75,
        "Arts plastiques": 82,
        "Musique": 82,
        "Éthique": 75,
        "Univers social": 81,
        "Sciences": 68
    }
    for topic in sorted(progress_topic_dict.keys()):
        div_label = Div(text="{}".format(topic))
        div_label.width = 150
        fig = setup_figure()
        data_x = [int(school_year[0:4]) for (school_year, avg) in progress_topic_dict[topic]]
        data_y = [avg for (school_year, avg) in progress_topic_dict[topic]]
        fig.line(x=data_x, y=data_y, line_color=ds_colors[2], line_width=2)
        fig2 = setup_figure()
        fig2.width = 30
        if data_y[-1] < data_y[-2] and data_y[-2] < data_y[-3]:
            alpha = 1
        elif data_y[-1] < data_y[-2]:
            alpha = 0
        else:
            alpha = 0
        fig2.circle([0], [0], size=10, color="red", alpha=alpha)
        div_value = Div(text="{:.2f} %".format(round(data_y[-1], 2)))
        bulletg = setup_bulletgraph(data_y[-1], target_topic[topic])
        rows_progress_topic.append(Row(div_label, fig, fig2, div_value, bulletg))

    # Setup failure by topic
    div_failure_topic_title = Div(text="Nombre d'élèves en situation d'échec par matière en {}".format(school_year_max),
                                  style={"font-size": "125%"}, margin=(30, 0, 0, 0))
    div_failure_topic_title.min_width = 600
    rows_failure_topic = [Row(div_failure_topic_title),
                          Row(Div(text="Niveaux", style={"font-style": "italic"}, width=150),
                              Div(text="Tendance sur 7 ans", style={"font-style": "italic"}, width=120),
                              Div(text="", style={"font-style": "italic"}, width=50),
                              Div(text="Nombre d'élèves", style={"font-style": "italic"}))]
    for topic in sorted(failure_topic_dict.keys()):
        div_label = (Div(text="{}".format(topic)))
        div_label.width = 150
        fig = setup_figure()
        data_x = [int(school_year[0:4]) for (school_year, avg) in failure_topic_dict[topic]]
        data_y = [avg for (school_year, avg) in failure_topic_dict[topic]]
        data_hc = [cnt for (topic, cnt) in headcount_topic_dict[topic]]
        fig.line(x=data_x, y=data_y, line_color=ds_colors[2], line_width=2)
        fig2 = setup_figure()
        fig2.width = 30
        if data_y[-1]/data_hc[-1] >= 0.12:
            alpha = 1
        elif data_y[-1]/data_hc[-1] >= 0.09:
            alpha = 0.25
        else:
            alpha = 0
        fig2.circle([0], [0], size=10, color="red", alpha=alpha)
        div_value = Div(text="{} / {}".format(data_y[-1], data_hc[-1]))
        rows_failure_topic.append(Row(div_label, fig, fig2, div_value))

    # Setup metadata
    div_md_title = Div(text="Métadonnées", style={"color": "silver", "font-size": "100%", "border-top": "1px solid silver"}, margin=(30, 0, 0, 0))
    div_md_title.min_width = ds_width
    date_current = datetime.date.today().strftime('%Y/%m/%d')
    author = "Fabrique REL"
    author_url = "https://fabriquerel.org"

    data_source = "Source : Fabrique REL"
    licence = "Licence CC BY-NC-SA"
    licence_url = "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr"
    licence_img_url = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png"

    div_author = Div(text='Auteur : <a href="{}">{}</a>'.format(author_url, author), style={"color": "silver"})
    div_data = Div(text='Données source : <a href="{}">{}</a>'.format(author_url, author), style={"color": "silver"})
    div_date = Div(text="Mise à jour : {}".format(date_current), style={"color": "silver"})
    div_licence = Div(text='<a href="{}"><img src="{}" alt="{}" style="height:20px"></a>'.format(licence_url,
                                                                                                 licence_img_url,
                                                                                                 licence),
                      style={"color": "silver"})

    pano_md = Column(div_md_title, Row(div_author, div_data, div_date, div_licence))

    #
    # Assembling html document
    #

    # Row : Title
    pano_title = Row(div_title)
    pano_title.align = 'center'

    # Row : Featured panorama
    pano_featured = Row(div_headcount, div_gender_f, div_gender_m, div_gender_a)
    pano_featured.align = 'center'

    # Progress by grade panorama
    pano_progress_grade = Column(*rows_progress_grade)
    pano_progress_grade.min_width = 400

    # Failure by grade panorama
    pano_failure_grade = Column(*rows_failure_grade)
    pano_failure_grade.min_width = 400

    # Row : progress and failure by grade panorama
    progress_failure_grade_row = Row(pano_progress_grade, pano_failure_grade)
    progress_failure_grade_row.min_width = 800

    # Progress by topic panorama
    pano_progress_topic = Column(*rows_progress_topic)
    pano_progress_topic.min_width = 400

    # Failure by topic panorama
    pano_failure_topic = Column(*rows_failure_topic)
    pano_failure_topic.min_width = 400

    # Row : progress and failure by topic panorama
    progress_failure_topic_row = Row(pano_progress_topic, pano_failure_topic)
    progress_failure_topic_row.min_width = 800

    # Document assembled stack of 4 layers
    column0 = Column(pano_title, pano_featured, pano_progress_overall, progress_failure_grade_row,
                     progress_failure_topic_row, pano_md)

    dashboard_html = file_html(column0, template=template, resources=CDN, title="Tableau de bord")
    return dashboard_html
