"""
LibreSign Documentation configuration (conf.py)

This configuration file sets up Sphinx for the LibreSign project documentation.
It also documents the current signature appearance and preview pipeline:

- **Signature Appearance**: The signature rendering uses the LibreSign
  rendering engine with default visual styles defined in the `signature.css`
  file located in the `static/` directory. The appearance can be customized
  via the `signature_style` configuration variable in the application.

- **Preview Pipeline**: When a user uploads a document for signing, the
  preview pipeline follows these steps:
  1. Parse the document and extract placeholder fields.
  2. Render the signature appearance using the configured style.
  3. Generate a preview PDF/HTML with embedded signature placeholders.
  4. Serve the preview to the user via the `/preview` endpoint.

The documentation includes a dedicated section under **Usage → Signature
Preview** that explains how to modify the appearance and how the pipeline
operates.
"""

import os
import sys
import datetime

# Ensure the project root is on the Python path for autodoc
sys.path.insert(0, os.path.abspath('.'))

now = datetime.datetime.now()

copyright = f"{now.year} LibreCode coop"
project = "LibreSign Documentation"
author = "LibreSign Team"
release = "1.0"

extensions = [
    "sphinx_rtd_theme",
    "sphinx_rtd_dark_mode",
    "sphinx_copybutton",
    "notfound.extension",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_logo = "images/logo.png"
html_theme_options = {
    "style_nav_header_background": "#184c4e",
    "logo_only": True,
    "navigation_with_keys": True,
    "style_external_links": True,
    "version_selector": False,
}
html_extra_path = ["html"]

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