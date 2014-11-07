#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from pip.req import parse_requirements


ENTRY_POINTS = {
    'console_scripts': [
        'prettytypo = prettytypo:main'
    ]
}

README = open('README.md').read()
CHANGELOG = open('docs/changelog.md').read()
REQUIREMENTS = [req for req in parse_requirements('requirements.txt')]


setup(
    name="prettytypo",
    version="0.0.1",
    url='',
    author='Evgeniy Bastrykov',
    author_email='vporoshok@gmail.com',
    description=README,
    long_description=README + '\n' + CHANGELOG,
    packages=['prettytypo'],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    entry_points=ENTRY_POINTS,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Natural Language :: Russian',
        'Topic :: Text Editors :: Text Processing',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Markup :: LaTeX',
    ],
    test_suite='prettytypo.tests',
)
