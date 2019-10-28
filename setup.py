# -*- coding: utf-8 -*-

import sys
import fastentrypoints
from setuptools import find_packages, setup
if not sys.version_info[0] == 3:
    sys.exit("Python 3 is required. Use: \'python3 setup.py install\'")

dependencies = []

config = {
    "version": "0.01",
    "name": "raidcalc",
    "url": "https://github.com/jakeogh/raidcalc",
    "license": "ISC",
    "author": "Justin Keogh",
    "author_email": "github.com@v6y.net",
    "description": "Short explination of what it does _here_",
    "long_description": __doc__,
    "packages": find_packages(exclude=['tests']),
    "include_package_data": True,
    "zip_safe": False,
    "platforms": "any",
    "install_requires": dependencies,
    "entry_points": {
        "console_scripts": [
            "raidcalc=raidcalc.raidcalc:cli",
        ],
    },
}

setup(**config)
