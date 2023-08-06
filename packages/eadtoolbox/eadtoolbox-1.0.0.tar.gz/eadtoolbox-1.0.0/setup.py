"""Tools for working with Encoded Archival Description (EAD) XML files.
"""

from __future__ import with_statement

import sys

# Import Distribute / Setuptools
import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages

# Check Python version
py_version = getattr(sys, 'version_info', (0, 0, 0))

# Basic information
_name = "eadtoolbox"
_version = "1.0.0"
_description = "Tools for working with EAD XML files."
_author = 'John Harrison'
_author_email = 'john.harrison@liv.ac.uk'

# Find longer description from README
with open('README.rst', 'r') as fh:
    _long_description = fh.read()

# Requirements
with open('requirements.txt', 'r') as fh:
    _install_requires = fh.readlines()

if py_version < (2, 7):
    _install_requires.append('argparse')


# Setup
setup(
    name=_name,
    version=_version,
    description=_description,
    long_description=_long_description,
    packages=[_name],
    author=_author,
    author_email=_author_email,
    maintainer=_author,
    maintainer_email=_author_email,
    include_package_data=True,
    package_data={_name: ['data/css/*.css', 'data/html/*.*', 'data/xml/*.*']},
    exclude_package_data={'': ['README.*', '.gitignore']},
    requires=['lxml(>=2.1)', 'wsgiref'],
    install_requires=_install_requires,
    setup_requires=['setuptools-git'],
    entry_points={
        'console_scripts': [
            "ead-sandbox = eadtoolbox.sandbox:start",
            "ead-validate = eadtoolbox.validate:validate"
        ]
    },
    url='http://github.com/bloomonkey/ead-toolbox',
    license="BSD",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7", 
        "Topic :: Text Processing :: Markup",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ]
)
