#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='gardnr',
    version='0.5.5',
    author='Jason Biegel',
    url='https://github.com/gardnr/gardnr',
    license='LICENSE',
    description='Monitor and control your grow operation.',
    packages=find_packages(exclude=['docs', 'samples', 'tests']),
    include_package_data=True,
    install_requires=[
        'APScheduler==3.5.3',
        'cron-descriptor==1.2.21',
        'Flask==1.0.2',
        'flask-command==0.0.3',
        'Flask-WTF==0.14.2',
        'gunicorn==19.9.0',
        'grow-recipe==0.9.0',
        'peewee==3.7.1',
        'pytz'
    ],
    entry_points={
        'console_scripts': [
            'gardnr=gardnr.cli:main',
            'gardnr-automata=gardnr.automata:main',
            'gardnr-server=gardnr.server:main'
        ]
    }
)
