# Copyright (C) 2013 Wesley Baugh
from setuptools import setup, find_packages


PROGRAM_NAME = 'inferhotspot'
VERSION = '0.1'
DESCRIPTION = ('Infer information about local hotspots.')
with open('requirements.txt') as f:
    REQUIREMENTS = f.read()
with open('README.md') as f:
    LONG_DESCRIPTION = f.read()


setup(
    name=PROGRAM_NAME,
    version=VERSION,
    packages=find_packages(),

    install_requires=REQUIREMENTS,

    author="Wesley Baugh",
    author_email="wesley@bwbaugh.com",
    url="http://www.github.com/bwbaugh/{0}".format(PROGRAM_NAME),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license='Creative Commons Attribution-NonCommercial-ShareAlike 3.0 '
            'Unported License',
    classifiers=["Intended Audience :: Developers",
                 "Intended Audience :: Education",
                 "Intended Audience :: Science/Research",
                 "Natural Language :: English",
                 "Programming Language :: Python",
                 "Topic :: Scientific/Engineering :: Artificial Intelligence",
                 "Topic :: Scientific/Engineering :: Information Analysis",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 "Topic :: Text Processing :: Linguistic"],
)
