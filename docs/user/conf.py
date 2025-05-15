import os
import sys
sys.path.insert(0, os.path.abspath('.'))

project = 'LibreSign Documentation'
author = 'LibreSign Team'
release = '1.0'

extensions = [
    'sphinxcontrib.openapi',
    'sphinxcontrib.redoc',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
