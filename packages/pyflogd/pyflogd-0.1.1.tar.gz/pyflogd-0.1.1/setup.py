#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(name='pyflogd',
      version='0.1.1',
      description='File system access monitoring daemon',
      long_description=long_description,
      author='Maik Kulbe',
      author_email='info@linux-web-development.de',
      license='MIT',
      packages=['pyflogd'],
      entry_points = {
        "console_scripts": [
          "pyflogd = pyflogd.pyflogd:main",
        ],
      },
      install_requires=[
        'pyinotify',
        'docopt',
        'schema',
        'python-daemon',
        'lockfile',
      ],
    )
