# -*- coding: utf-8 -*-
import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-cms-simple-events',
    version = '0.4.1',
    packages = ['simple_events'],
    include_package_data = True,
    license = 'BSD License', # example license
    description = 'A django-cms application for managing an events calendar.',
    long_description = README,
    url = 'http://www.toporojo.es/',
    author = 'Alejandro Núñez Liz',
    author_email = 'alejandro@toporojo.es',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    zip_safe=False,
    install_requires=['django-hvad', ],
)
