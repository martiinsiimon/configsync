#!/usr/bin/env python3
#-*- coding: UTF-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'configsync',
    'version': '0.9',
    'packages': ['configsync'],
    'entry_points' : {
        'gui_scripts': [
            'configsync = configsync.configsync:main',
        ]
    },
    
    'package_data' : {'':['*.ui']},
    'install_requires': ['PyGObject'],
    
    # used for PyPI
    'author': 'Martin Simon',
    'author_email': 'martiinsiimon@gmail.com',
    'description': 'A tool to synchronize config files among different systems ',
    'license': 'MIT',
    'keywords' : 'synchronization configuration python',
    'url': 'https://github.com/martiinsiimon/configsync'
}


setup(**config)
