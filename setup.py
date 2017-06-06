#!/usr/bin/python
from __future__ import (
    absolute_import,
    print_function,
    )

from setuptools import find_packages, setup

setup(
    name="scame",
    description="A composite linter and style checker.",
    version="0.1.0",
    maintainer="Adi Roiban",
    maintainer_email="adi.roiban@chevah.com",
    url="https://github.com/chevah/scame",
    packages=find_packages('.'),
      entry_points={
          'console_scripts': [
              'scame = scame.__main__:main'
          ]
      },
    )
