import logging

FORMATTER = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMATTER, level=logging.INFO)
logger = logging.getLogger(__name__)



class HtmlScripter(object):

    def __init__(self):
        logger.info("Scripter, instantiating html scripter")

    css = {
        "title": {"font-size": "150%", "text-align": "center"},
        "pano_featured": {"font-size": "150%", "color": "grey", "text-align": "center", "border": "1px solid grey"}
    }

    html = {
        "document": """
<!DOCTYPE html>
<html lang="fr">
    <head>
        <meta charset="utf-8">
        <title>{{ title if title else "Tableau de bord" }}</title>
        {{ bokeh_css | safe }}
        {{ bokeh_js | safe }}
        <style>
          .slick-header-column {
            background-color: rgba(187, 187, 187, 1.0) !important;
            background-image: none !important;
            font-size: 14pt;
            font-style: italic;
          }
        </style>
    </head>
    <body>
        {{ plot_div | safe }}
        {{ plot_script | safe }}
    </body>
</html> """
    }
