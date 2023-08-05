# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

classifiers = (
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 2.7',
    'License :: OSI Approved :: MIT License',
)

required = (
    'pandas'
)

kw = {
    'name': 'vincent',
    'version': '0.1.5',
    'description': 'A Python to Vega translator',
    'long_description': open('README.rst', 'rt').read(),
    'author': 'Rob Story',
    'author_email': 'wrobstory@gmail.com',
    'license': 'MIT License',
    'url': 'https://github.com/wrobstory/vincent',
    'keywords': 'data visualization',
    'classifiers': classifiers,
    'packages': ['vincent'],
    'package_data': {'vincent': ['*.html']},
    'install_requires': required,
    'zip_safe': True,
}

setup(**kw)
