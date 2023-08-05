#!/usr/bin/env python

from setuptools import setup, find_packages

DESCRIPTION = """
file metadata tagger
"""

entry_points = {
    'console_scripts': [
        'mad = mad2.cli.main:dispatch'
        ]}

setup(name='mad2',
      version='0.0.6',
      description=DESCRIPTION,
      author='Mark Fiers',
      author_email='mark.fiers42@gmail.com',
      entry_points = entry_points,
      url='http://mfiers.github.com/mad2',
      packages=find_packages(),
      requires=['Leip',
                'Yaco',
                'xlrd',
                ],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        ]

     )
