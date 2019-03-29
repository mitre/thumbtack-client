# -*- coding: utf-8 -*-

project = 'thumbtack-client'
copyright = '2019, The MITRE Corporation'
author = 'The MITRE Corporation'

version = '0.1.2'
release = '0.1.2'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

language = None

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'


html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    # 'canonical_url': '',
    # 'analytics_id': '',
    # 'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    # 'style_external_links': False,
    # 'vcs_pageview_mode': '',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 2,
    # 'includehidden': True,
    # 'titles_only': False
}

htmlhelp_basename = 'thumbtack-clientdoc'

latex_elements = {}

latex_documents = [
    (master_doc, 'thumbtack-client.tex', 'thumbtack-client Documentation',
     'The MITRE Corporation', 'manual'),
]

man_pages = [
    (master_doc, 'thumbtack-client', 'thumbtack-client Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'thumbtack-client', 'thumbtack-client Documentation',
     author, 'thumbtack-client', 'One line description of project.',
     'Miscellaneous'),
]
