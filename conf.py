import os
import sys
import datetime
sys.path.insert(0, os.path.abspath('.'))

now = datetime.datetime.now()

copyright = str(now.year) + ' LibreCode coop'
project = 'LibreSign Documentation'
author = 'LibreSign Team'
release = '1.0'

extensions = [
    'sphinx_rtd_theme',
    'sphinx_rtd_dark_mode',
    'sphinx_copybutton',
    'notfound.extension',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
# Single shared logo for every manual (each manual's conf.py imports this file).
html_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "logo.png")
html_theme_options = {
    'style_nav_header_background': '#184c4e',
	'logo_only': True,
	'navigation_with_keys': True,
	'style_external_links': True,
	'version_selector': False,
}
html_extra_path = ['html']

# "Edit on GitHub" link shown at the top of each page by sphinx_rtd_theme.
# Each manual overrides conf_py_path with its own directory.
html_context = {
    'display_github': True,
    'github_user': 'LibreSign',
    'github_repo': 'documentation',
    'github_version': 'main',
    'conf_py_path': '/',
}

# -- Options for sphinx-notfound-page extension -----------------------------------
# https://github.com/readthedocs/sphinx-notfound-page

# content context passed to the 404 template
notfound_context = {
    "title": "404 Page Not Found",
    "body": """
<h1>Page Not Found</h1>
<h2>Sorry, we can't seem to find the page you're looking for.</h2>
<h6>Error code: 404</h6>

<h3>Here are some alternatives:</h3>
<ol>
  <li>Try using the search box.</li>
  <li>Check the content menu on the side of this page.</li>
  <li>Regroup at our <a href="/">documentation homepage.</a></p></li>
</ol>
""",
}

notfound_urls_prefix = None
# Versioned site support is independent of the theme's selector flag.
from versioning.sphinx_config import configure as _configure_versioning
_configure_versioning(globals())
