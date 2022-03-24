import datetime
import logging
import pandas as pd

from bokeh.embed import file_html
from bokeh.models import Div, Column, Row, Legend, LegendItem, ColumnDataSource, TableColumn, DataTable, \
    HTMLTemplateFormatter
from bokeh.palettes import PuBu4
from bokeh.plotting import figure, show, output_file, save
from bokeh.resources import JSResources, CDN
from jinja2 import Template

from . helpers.htmlscripters import HtmlScripter
from . helpers.sqlscripters import SqliteScripter
from . helpers.database import Database

FORMATTER = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMATTER, level=logging.DEBUG)
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
    bulletgraph = setup_figure()
    bulletgraph.x_range.range_padding = 0
    bulletgraph.grid.grid_line_color = None
    bulletgraph.xaxis[0].ticker.num_minor_ticks = 0
    bulletgraph.margin = (0, 20, 0, 0)
    for left, right, color in zip(limits[:-1], limits[1:], PuBu4[::-1]):
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
    logger.debug("Got CSS and Schools, {} were returned".format(len(rs)))

    # Data: school year period
    cursor.execute(scripter.dql['select_period'])
    rs = cursor.fetchall()
    (school_year_min, year_min, school_year_max, year_max) = rs[0]
    logger.debug("Got school years, {} were returned".format(len(rs)))

    # Data : topic list
    cursor.execute(scripter.dql['select_topic_list'])
    rs = cursor.fetchall()
    topic_list = [topic[0] for topic in rs]
    logger.debug("Got topics, {} were returned".format(len(topic_list)))

    # Data : school number of students
    cursor.execute(scripter.dql['select_institution_headcount'], (school_year_max,))
    rs = cursor.fetchall()
    (student_headcount,) = rs[0]
    logger.debug("Got student head count, {} were returned".format(len(rs)))

    # Data: gender division
    cursor.execute(scripter.dql['select_gender_pct'], (school_year_max, school_year_max))
    rs = cursor.fetchall()
    (pct_m, pct_f) = rs[0]
    logger.debug("Got gender division, {} were returned".format(len(rs)))

    # Data : school number of students by topic by grade over current year
    stmt = scripter.dql['select_topic_grade_headcount']
    df = pd.read_sql(stmt, con=cnx, params=[school_year_max])
    df_topic_grade_headcount = df.pivot(index='topic', columns=['grade'], values='hc').fillna(0)
    print(df)

    # Data: school number of failing students by topic by grade over current year
    stmt = scripter.dql['select_failure_topic_grade']
    df = pd.read_sql(stmt, con=cnx, params=[school_year_max])
    df_topic_grade_failures = df.pivot(index='topic', columns=['grade'], values='fc').fillna('s/o')

    # Data: school number of failing students by topic by grade by gender over current year
    stmt = scripter.dql['select_failure_topic_grade_gender']
    df = pd.read_sql(stmt, con=cnx, params=[school_year_max, 'f'])
    df_topic_grade_gender_f_failures = df.pivot(index='topic', columns=['grade'], values='fc').fillna('s/o')
    df = pd.read_sql(stmt, con=cnx, params=[school_year_max, 'm'])
    df_topic_grade_gender_m_failures = df.pivot(index='topic', columns=['grade'], values='fc').fillna('s/o')

    # Data : Reformat dataframe for dashboard
    for df in [df_topic_grade_headcount, df_topic_grade_failures, df_topic_grade_gender_f_failures,
               df_topic_grade_gender_m_failures]:
        for grade in range(1, 7):
            try:
                df[grade]
            except:
                df[grade] = ['s/o'] * len(df.index)
        df.sort_index(axis=1, inplace=True)
        df.set_axis(list('123456'), axis=1, inplace=True)
        df.reset_index(inplace=True)

    cursor.close()
    cnx.close()

    htmlscripter = HtmlScripter()
    template = Template(htmlscripter.html['document'])

    # Setup dashboard parameters
    ds_width = 1024

    # Setup dashboard title
    div_title = Div(
        text="""<h1>Analyse de la réussite {}<br>{} au {}</h1>""".format(school_year_max, school_name, css_name),
        style=htmlscripter.css['title'])
    div_title.sizing_mode = "scale_width"
    div_title.align = "center"

    # Setup header panorama
    div_headcount = Div(text="Nombre d'élèves<br>{}".format(student_headcount), style=htmlscripter.css['pano_featured'])
    div_gender_f = Div(text="Genre féminin<br>{}%".format(pct_f), style=htmlscripter.css['pano_featured'])
    div_gender_m = Div(text="Genre masculin<br>{}%".format(pct_m), style=htmlscripter.css['pano_featured'])
    div_gender_a = Div(text="Genre inclusif<br>{}%".format(0), style=htmlscripter.css['pano_featured'])

    # Setup analysis of failures
    cell_template = """
    <div <%=
        (function colorfromvalue(){
            if (value >= 7) {
                return('style="background-color:rgba(255, 0, 0, 1.0); font-size:12pt; color:rgba(255, 255, 255, 1.0); padding-left:5px"')}
            else if (value >= 5) {
                return('style="background-color:rgba(255, 0, 0, 0.25); font-size:12pt; padding-left:5px"')}
            else {
                return('style="background-color:rgba(255, 0, 0, 0.0); font-size:12pt; padding-left:5px"')}
            }()) %>><%= value %></div>
    """

    cell_formatter = HTMLTemplateFormatter(template=cell_template)
    topic_formatter = HTMLTemplateFormatter(template="""<div style="font-size:12pt"><%= value %></div>""")

    columns = [
        TableColumn(field="topic", title="Matière", formatter=topic_formatter),
        TableColumn(field="1", title="1ere année", formatter=cell_formatter),
        TableColumn(field="2", title="2e année", formatter=cell_formatter),
        TableColumn(field="3", title="3e année", formatter=cell_formatter),
        TableColumn(field="4", title="4e année", formatter=cell_formatter),
        TableColumn(field="5", title="5e année", formatter=cell_formatter),
        TableColumn(field="6", title="6e année", formatter=cell_formatter)
    ]

    div_failure_all_title = Div(
        text="Nombre d'élèves en situation d'échec par matière, par niveau en {}".format(school_year_max),
        style={"font-size": "16pt"}, margin=(30, 0, 0, 0))
    source_all = ColumnDataSource(df_topic_grade_failures)
    table_all = DataTable(source=source_all, columns=columns, index_position=None, editable=False, width=1800, height=300)

    div_failure_f_title = Div(
        text="Nombre de filles en situation d'échec par matière, par niveau en {}".format(school_year_max),
        style={"font-size": "16pt"}, margin=(0, 0, 0, 0))
    source_f = ColumnDataSource(df_topic_grade_gender_f_failures)
    table_f = DataTable(source=source_f, columns=columns, index_position=None, editable=False, width=1800, height=300)

    div_failure_m_title = Div(
        text="Nombre de garçons en situation d'échec par matière, par niveau en {}".format(school_year_max),
        style={"font-size": "16pt"}, margin=(0, 0, 0, 0))
    source_m = ColumnDataSource(df_topic_grade_gender_m_failures)
    table_m = DataTable(source=source_m, columns=columns, index_position=None, editable=False, width=1800, height=300)

    # Setup metadata
    div_md_title = Div(text="Métadonnées",
                       style={"color": "silver", "font-size": "100%", "border-top": "1px solid silver"},
                       margin=(30, 0, 0, 0))
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

    # Row : Table panorama
    pano_table = Row(Column(div_failure_all_title, table_all, div_failure_f_title, table_f, div_failure_m_title, table_m))

    # Document assembled stack of 4 layers
    column0 = Column(pano_title, pano_featured, pano_table, pano_md)

    date_current = datetime.date.today().strftime('%Y%m%d')
    dashboard_html = file_html(column0, template=template, resources=CDN, title="Tableau de bord")

    return dashboard_html

