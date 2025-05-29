import os
import sys
sys.path.insert(0, os.path.abspath('.'))

project = 'LibreSign Documentation'
author = 'LibreSign Team'
release = '1.0'

extensions = [
    'sphinx_rtd_theme',
    'sphinx_rtd_dark_mode',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
	'logo_only': True,
	'navigation_with_keys': True,
	'style_external_links': True,
	'version_selector': False,
}
html_static_path = ['_static']
