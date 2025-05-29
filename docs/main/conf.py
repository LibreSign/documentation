# conf.py para a documentação principal

project = 'LibreSign'
copyright = ''
author = ''

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
