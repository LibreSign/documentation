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
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_logo = "images/logo.png"
html_theme_options = {
    'style_nav_header_background': '#184c4e',
	'logo_only': True,
	'navigation_with_keys': True,
	'style_external_links': True,
	'version_selector': False,
}
