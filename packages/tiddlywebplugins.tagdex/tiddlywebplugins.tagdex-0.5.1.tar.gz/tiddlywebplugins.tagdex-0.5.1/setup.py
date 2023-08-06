import os

from setuptools import setup, find_packages


# XXX: these should go into the package's __init__
VERSION = '0.5.1'
AUTHOR = 'FND'
LICENSE = 'BSD'

DESC = os.path.join(os.path.dirname(__file__), 'README')
DESC = ''.join(line for line in open(DESC)
        if not line.startswith('[![build status](http')) # XXX: fugly hack

META = {
    'name': 'tiddlywebplugins.tagdex',
    'url': 'https://github.com/FND/tiddlywebplugins.tagdex',
    'version': VERSION,
    'description': 'TiddlyWeb indexer for faceted tag-based tiddler retrieval',
    'long_description': DESC,
    'license': LICENSE,
    'author': AUTHOR,
    'packages': find_packages(exclude=['test']),
    'platforms': 'Posix; MacOS X; Windows',
    'include_package_data': False,
    'zip_safe': False,
    'install_requires': ['tiddlyweb>=1.4.8', 'tiddlywebplugins.utils'],
    'extras_require': {
        'testing': ['pytest', 'wsgi-intercept', 'httplib2', 'pyquery'],
        'coverage': ['figleaf', 'coverage']
    }
}


if __name__ == '__main__':
    setup(**META)
