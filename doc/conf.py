import sys
sys.path.insert(0, '.')

project = u'aiotraversal'
copyright = u'2014-2016, Alexander "ZZZ" Zelenyak'
version = '0.10.0'
release = version

# extensions = ['sphinx.ext.autodoc']
extensions = ['alabaster']
# templates_path = ['_templates']

source_suffix = '.rst'
source_encoding = 'utf8'
master_doc = 'index'
exclude_trees = ['_build']

pygments_style = 'sphinx'
html_theme = 'alabaster'
# html_static_path = ['_static']
