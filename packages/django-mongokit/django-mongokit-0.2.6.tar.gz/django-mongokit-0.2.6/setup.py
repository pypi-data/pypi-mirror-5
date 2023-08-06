#!/usr/bin/env python
# Copyright (c) 2010-2012 Peter Bengtsson, mail@peterbe.com
from setuptools import setup, find_packages

setup(
    name='django-mongokit',
    version=open('django_mongokit/version.txt').read().strip(),
    author="Peter Bengtsson",
    author_email="mail@peterbe.com",
    url="https://github.com/peterbe/django-mongokit",
    description='Bridging Django to MongoDB with the MongoKit ODM',
    long_description=open('README.md').read(),
    package_dir={
        'djangomongokitlib': 'django-mongokitlib',
    },
    packages=[
        'django_mongokit',
        'django_mongokit.forms',
        'django_mongokit.mongodb',
    ],
    package_data={'django_mongokit': ['version.txt']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    install_requires=[
        'mongokit',
    ],
)
