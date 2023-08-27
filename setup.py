#!/usr/bin/env python

from setuptools import setup, find_packages

requirements = [x.strip() for x in open("requirements.txt", "r").readlines()]

setup(name='MineSight',
      version='1.0.13',
      description='Investigate a Minecraft account',
      author='Gobutsu',
      packages=find_packages(),
      url='https://github.com/Gobutsu/MineSight',
      install_requires=requirements,
        package_data={'minesight': ['sites.json']},
      entry_points={
            'console_scripts': [
                    'minesight = minesight.main:main'
            ]
        },
      python_requires='>=3.6'
)