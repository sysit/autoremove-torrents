#-*- coding:UTF-8 -*-

from setuptools import setup, find_packages
from autoremovetorrents.version import __version__

setup(name = 'autoremove-torrents',
    version = __version__,
    description = 'Automatically remove torrents according to your strategies.',
    long_description = open('README.rst', 'r', encoding='utf-8').read(),
    long_description_content_type = 'text/x-rst',
    classifiers = [
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ], # Get classifiers from https://pypi.org/pypi?%3Aaction=list_classifiers
    keywords = 'python autoremove torrent',
    author = 'jerrymakesjelly',
    author_email = 'ganzhaoyu037@gmail.com',
    url = 'https://github.com/jerrymakesjelly/autoremove-torrents',
    license = 'MIT',
    packages = find_packages(),
    include_package_data = True,
    # PLY writes its generated parsetab.py next to the package at import time,
    # which is impossible inside a zip
    zip_safe = False,
    install_requires = [
        'deluge-client',
        'ply',
        'pyyaml',
        'requests',
    ],
    entry_points = {
        'console_scripts':[
            'autoremove-torrents = autoremovetorrents.main:main'
        ]
    }
)
